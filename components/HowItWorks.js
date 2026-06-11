import React from 'react';

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 bg-slate-50 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        
        {/* Title */}
        <div className="text-center">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-brand-900 tracking-tight">
            How it works
          </h2>
        </div>

        {/* Timeline Layout */}
        <div className="relative max-w-4xl mx-auto">
          {/* Vertical central line for desktop */}
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-indigo-100 -translate-x-1/2 hidden md:block"></div>

          {/* Step 1 */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center relative mb-16 md:mb-24">
            {/* Left side: Text */}
            <div className="md:col-span-5 md:text-right space-y-2 order-2 md:order-1">
              <h3 className="text-xl font-bold text-brand-900">Create a Group</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Add friends by phone number or unique link. Set the base currency and you're ready.
              </p>
            </div>
            
            {/* Center: Number Bubble */}
            <div className="md:col-span-2 flex justify-start md:justify-center z-10 order-1 md:order-2">
              <div className="w-10 h-10 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center shadow-md">
                1
              </div>
            </div>

            {/* Right side: Visual */}
            <div className="md:col-span-5 order-3">
              <div className="relative rounded-3xl overflow-hidden shadow-lg border border-slate-100 max-w-sm">
                <img 
                  src="https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=600&h=400&q=85" 
                  alt="Friends hanging out"
                  className="w-full h-48 object-cover" 
                />
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center relative mb-16 md:mb-24">
            {/* Left side: Visual */}
            <div className="md:col-span-5 flex justify-end order-3 md:order-1">
              <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-lg max-w-xs w-full space-y-4">
                <div className="flex justify-between items-center bg-indigo-50/50 p-3 rounded-xl border border-indigo-100/30">
                  <div>
                    <span className="block text-xs font-bold text-brand-900">Tacos & Margs</span>
                    <span className="text-[10px] text-slate-400">Dinner split</span>
                  </div>
                  <span className="text-sm font-extrabold text-indigo-600">₹640.00</span>
                </div>
                <div className="flex space-x-1">
                  <div className="w-5 h-5 rounded-full bg-indigo-400"></div>
                  <div className="w-5 h-5 rounded-full bg-emerald-400"></div>
                  <div className="w-5 h-5 rounded-full bg-rose-400"></div>
                </div>
              </div>
            </div>

            {/* Center: Number Bubble */}
            <div className="md:col-span-2 flex justify-start md:justify-center z-10 order-1 md:order-2">
              <div className="w-10 h-10 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center shadow-md">
                2
              </div>
            </div>

            {/* Right side: Text */}
            <div className="md:col-span-5 space-y-2 order-2">
              <h3 className="text-xl font-bold text-brand-900">Add Expenses</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Type in the expense amount. Split it evenly, by percentages, or by exact shares among group members.
              </p>
            </div>
          </div>

          {/* Step 3 */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center relative">
            {/* Left side: Text */}
            <div className="md:col-span-5 md:text-right space-y-2 order-2 md:order-1">
              <h3 className="text-xl font-bold text-brand-900">Settle Up</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Pay with your favorite app. We confirm the transfer and clear the debt instantly.
              </p>
            </div>
            
            {/* Center: Number Bubble */}
            <div className="md:col-span-2 flex justify-start md:justify-center z-10 order-1 md:order-2">
              <div className="w-10 h-10 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center shadow-md">
                3
              </div>
            </div>

            {/* Right side: Visual */}
            <div className="md:col-span-5 order-3">
              <div className="bg-emerald-50 border border-emerald-100/50 rounded-2xl py-4 px-6 shadow-md max-w-xs flex items-center space-x-3 text-emerald-800">
                <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 shadow-sm flex-shrink-0">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-xs font-bold uppercase tracking-wider">All Settled Up!</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
