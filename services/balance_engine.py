from decimal import Decimal

def get_group_balances(group_id):
    from app import supabase
    if not supabase:
        return {}
        
    balances = {}
    
    # 1. Fetch all group members to initialize their balances to 0.0
    members_res = supabase.table('group_members').select('user_id').eq('group_id', group_id).execute()
    for m in members_res.data:
        balances[m['user_id']] = Decimal('0.00')
        
    # 2. Fetch all expenses with splits
    expenses_res = supabase.table('expenses').select('*, expense_splits(*)').eq('group_id', group_id).execute()
    
    for exp in expenses_res.data:
        payer = exp['paid_by']
        # If the payer is not in the balances (e.g. they left the group), initialize it
        if payer not in balances:
            balances[payer] = Decimal('0.00')
            
        for split in exp['expense_splits']:
            debtor = split['user_id']
            amount = Decimal(str(split['amount_owed']))
            
            # If debtor is not in balances, initialize it
            if debtor not in balances:
                balances[debtor] = Decimal('0.00')
                
            # debtor owes payer, so debtor gets -amount and payer gets +amount
            balances[payer] += amount
            balances[debtor] -= amount
            
    # 3. Fetch all settlements
    settlements_res = supabase.table('settlements').select('*').eq('group_id', group_id).execute()
    for s in settlements_res.data:
        payer = s['paid_by']
        receiver = s['paid_to']
        amount = Decimal(str(s['amount']))
        
        if payer not in balances:
            balances[payer] = Decimal('0.00')
        if receiver not in balances:
            balances[receiver] = Decimal('0.00')
            
        # payer paid receiver, so payer gets +amount (debt reduced), receiver gets -amount (credit reduced)
        balances[payer] += amount
        balances[receiver] -= amount
        
    return {user_id: float(bal) for user_id, bal in balances.items()}

def simplify_debts(balances, user_profiles):
    creditors = []
    debtors = []
    
    for user_id, bal in balances.items():
        val = round(bal, 2)
        if val > 0.01:
            creditors.append([user_id, val])
        elif val < -0.01:
            debtors.append([user_id, -val])
            
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)
    
    transactions = []
    i, j = 0, 0
    
    while i < len(creditors) and j < len(debtors):
        creditor_id, credit = creditors[i]
        debtor_id, debt = debtors[j]
        
        settle = min(credit, debt)
        if settle > 0.01:
            transactions.append({
                "from_user": debtor_id,
                "from_name": user_profiles.get(debtor_id, debtor_id),
                "to_user": creditor_id,
                "to_name": user_profiles.get(creditor_id, creditor_id),
                "amount": round(settle, 2)
            })
            
        creditors[i][1] = round(credit - settle, 2)
        debtors[j][1] = round(debt - settle, 2)
        
        if creditors[i][1] <= 0.01:
            i += 1
        if debtors[j][1] <= 0.01:
            j += 1
            
    return transactions
