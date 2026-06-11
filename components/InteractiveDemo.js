import React, { useState } from 'react';

export default function InteractiveDemo() {
  const [step, setStep] = useState('active'); // 'active', 'simplifying', 'settled'
  const [expenses, setExpenses] = useState([
    { id: 1, title: 'Airbnb Villa', paidBy: 'Alex', amount: 4500.0 },
    { id: 2, title: 'Seafood Dinner', paidBy: 'Rahul', amount: 1200.0 },
  ]);

  const [balances, setBalances] = useState({
    Priya: -1140.0,
    Sam: -1140.0,
    Alex: 2280.0,
    Rahul: 0.0,
  });

  const [hasAddedMock, setHasAddedMock] = useState(false);

  const addMockExpense = () => {
    if (hasAddedMock) return;
    
    // Add "Beach Drinks ₹800 paid by Priya"
    // Split 4 ways: ₹200 each. Priya gets +₹600. Others get -₹200.
    setExpenses([
      ...expenses,
      { id: 3, title: 'Beach Drinks', paidBy: 'Priya', amount: 800.0 },
    ]);

    setBalances({
      Priya: -540.0, // -1140 + 600
      Sam: -1340.0,  // -1140 - 200
      Alex: 2080.0,  // 2280 - 200
      Rahul: -200.0, // 0 - 200
    });

    setHasAddedMock(true);
  };

  // Compute transactions to settle
  // For simplicity, we define them directly based on state
  const getTransactions = () => {
    if (!hasAddedMock) {
      return [
        { from: 'Priya', to: 'Alex', amount: 1140.0, resolved: false },
        { from: 'Sam', to: 'Alex', amount: 1140.0, resolved: false },
      ];
    } else {
      return [
        { from: 'Priya', to: 'Alex', amount: 540.0, resolved: false },
        { from: 'Sam', to: 'Alex', amount: 1340.0, resolved: false },
        { from: 'Rahul', to: 'Alex', amount: 200.0, resolved: false },
      ];
    }
  };

  const [txns, setTxns] = useState([]);

  const startSimplification = () => {
    setTxns(getTransactions());
    setStep('simplifying');
  };

  const resolveTxn = (index) => {
    const updated = [...txns];
    updated[index].resolved = true;
    setTxns(updated);

    // If all resolved, transition to settled
    if (updated.every((t) => t.resolved)) {
      setTimeout(() => {
        setBalances({
          Priya: 0.0,
          Sam: 0.0,
          Alex: 0.0,
          Rahul: 0.0,
        });
        setStep('settled');
      }, 500);
    }
  };

  const resetDemo = () => {
    setExpenses([
      { id: 1, title: 'Airbnb Villa', paidBy: 'Alex', amount: 4500.0 },
      { id: 2, title: 'Seafood Dinner', paidBy: 'Rahul', amount: 1200.0 },
    ]);
    setBalances({
      Priya: -1140.0,
      Sam: -1140.0,
      Alex: 2280.0,
      Rahul: 0.0,
    });
    setHasAddedMock(false);
    setStep('active');
  };

  return (
    <section id="interactive-demo" className="py-20 bg-white relative">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12 text-center">
        
        {/* Title */}
        <div className="space-y-4">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-brand-900 tracking-tight">
            Interactive Demo
          </h2>
          <p className="text-slate-500 text-sm max-w-md mx-auto leading-relaxed">
            See our splitting engine in action. Add an expense or simulate the settle-up flow.
          </p>
        </div>

        {/* Ledger Card Container */}
        <div className="bg-white border border-slate-100 shadow-2xl rounded-3xl p-6 sm:p-8 text-left max-w-2xl mx-auto space-y-6 relative overflow-hidden">
          
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Goa Weekend Trip</h3>
              <p className="text-xs text-slate-400">
                {hasAddedMock ? '5 friends' : '4 friends'} • August 2026
              </p>
            </div>
            
            {step === 'active' && (
              <button 
                onClick={addMockExpense}
                disabled={hasAddedMock}
                className={`py-2 px-4 rounded-xl text-xs font-semibold shadow-sm transition-all ${
                  hasAddedMock 
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white active:scale-[0.98]'
                }`}
              >
                + Add Expense
              </button>
            )}

            {step !== 'active' && (
              <button 
                onClick={resetDemo}
                className="py-2 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-sm transition-all active:scale-[0.98]"
              >
                Reset Demo
              </button>
            )}
          </div>

          {/* Step: Active Expense List */}
          {step === 'active' && (
            <div className="space-y-4">
              <div className="space-y-3">
                {expenses.map((exp) => (
                  <div key={exp.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="flex items-center space-x-3">
                      <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-lg">
                        {exp.title.includes('Villa') ? '🏠' : exp.title.includes('Dinner') ? '🍔' : '🍹'}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-slate-900">{exp.title}</h4>
                        <p className="text-[10px] text-slate-500">Paid by <span className="font-semibold text-slate-700">{exp.paidBy}</span></p>
                      </div>
                    </div>
                    <span className="text-sm font-extrabold text-slate-900">₹{exp.amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              {/* Balances Section */}
              <div className="space-y-4 pt-4 border-t border-slate-100">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Balances</h4>
                <div className="grid grid-cols-4 gap-4 text-center">
                  {Object.entries(balances).map(([name, val]) => (
                    <div key={name} className="space-y-2">
                      <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-700 font-bold border border-slate-200 flex items-center justify-center mx-auto text-xs">
                        {name[0]}
                      </div>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-500">{name}</span>
                        {val > 0.01 ? (
                          <span className="text-xs font-bold text-emerald-600">+₹{val.toFixed(2)}</span>
                        ) : val < -0.01 ? (
                          <span className="text-xs font-bold text-rose-500">-₹{Math.abs(val).toFixed(2)}</span>
                        ) : (
                          <span className="text-xs font-semibold text-slate-400">Settled</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action */}
              <div className="text-center pt-4">
                <button 
                  onClick={startSimplification}
                  className="w-full py-3.5 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl shadow-lg shadow-indigo-600/10 active:scale-[0.98] transition-all text-sm"
                >
                  Simulate Settle Up
                </button>
              </div>
            </div>
          )}

          {/* Step: Simplifying Debts list */}
          {step === 'simplifying' && (
            <div className="space-y-6">
              <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-2xl">
                <p className="text-xs text-indigo-800 leading-relaxed font-medium">
                  💡 <strong>PayYourPart Settle Engine:</strong> We matched debits to credits to minimize transactions. Clear the balances below:
                </p>
              </div>

              <div className="space-y-3">
                {txns.map((txn, idx) => (
                  <div 
                    key={idx} 
                    className={`flex items-center justify-between p-4 rounded-2xl border transition-all ${
                      txn.resolved 
                      ? 'bg-slate-50 border-slate-100 opacity-60' 
                      : 'bg-white border-slate-100 shadow-sm'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${
                        txn.resolved ? 'bg-slate-100 text-slate-400' : 'bg-indigo-50 text-indigo-600'
                      }`}>
                        {txn.from[0]}
                      </div>
                      <div className="text-xs">
                        <span className="font-bold text-slate-900">{txn.from}</span>
                        <span className="text-slate-400 mx-1">owes</span>
                        <span className="font-bold text-slate-900">{txn.to}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className="text-xs font-extrabold text-slate-900">₹{txn.amount.toFixed(2)}</span>
                      <button 
                        onClick={() => resolveTxn(idx)}
                        disabled={txn.resolved}
                        className={`py-1.5 px-3 rounded-lg text-[10px] font-bold shadow-sm transition-all ${
                          txn.resolved 
                          ? 'bg-emerald-100 text-emerald-700 cursor-default' 
                          : 'bg-indigo-600 hover:bg-indigo-700 text-white active:scale-[0.98]'
                        }`}
                      >
                        {txn.resolved ? 'Paid ✓' : 'Settle'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step: All Settled Up */}
          {step === 'settled' && (
            <div className="text-center py-12 space-y-6">
              <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-md">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="space-y-2">
                <h4 className="text-2xl font-black text-brand-900">All Settled Up!</h4>
                <p className="text-xs text-slate-400 max-w-xs mx-auto">
                  Every user balance is now ₹0.00. No debts are remaining!
                </p>
              </div>
              <div>
                <button 
                  onClick={resetDemo}
                  className="py-2.5 px-6 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-md transition-all active:scale-[0.98]"
                >
                  Restart Demo
                </button>
              </div>
            </div>
          )}

        </div>

      </div>
    </section>
  );
}
