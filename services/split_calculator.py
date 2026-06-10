from decimal import Decimal, ROUND_HALF_UP

def calculate_splits(members, amount, split_type, overrides=None):
    if overrides is None:
        overrides = {}
        
    if not members:
        return []
        
    amount_dec = Decimal(str(amount))
    n = len(members)
    
    if split_type == 'equal':
        per_person = (amount_dec / n).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        splits = []
        total_assigned = Decimal('0.00')
        for i, m in enumerate(members):
            if i == n - 1:
                share = amount_dec - total_assigned
            else:
                share = per_person
                total_assigned += share
            splits.append({"user_id": m, "amount_owed": float(share)})
        return splits
        
    elif split_type == 'exact':
        overrides_dec = {k: Decimal(str(v)) for k, v in overrides.items()}
        total_overrides = sum(overrides_dec.values())
        if total_overrides != amount_dec:
            raise ValueError(f"Sum of exact splits ({total_overrides}) must equal the total amount ({amount_dec})")
            
        splits = []
        for m in members:
            share = overrides_dec.get(m, Decimal('0.00'))
            splits.append({"user_id": m, "amount_owed": float(share)})
        return splits
        
    elif split_type == 'percentage':
        overrides_dec = {k: Decimal(str(v)) for k, v in overrides.items()}
        total_pct = sum(overrides_dec.values())
        if total_pct != Decimal('100.00') and total_pct != Decimal('100'):
            raise ValueError(f"Sum of percentages ({total_pct}) must equal 100%")
            
        splits = []
        total_assigned = Decimal('0.00')
        for i, m in enumerate(members):
            pct = overrides_dec.get(m, Decimal('0.00'))
            if i == n - 1:
                share = amount_dec - total_assigned
            else:
                share = (amount_dec * pct / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                total_assigned += share
            splits.append({"user_id": m, "amount_owed": float(share)})
        return splits
    else:
        raise ValueError(f"Unsupported split type: {split_type}")
