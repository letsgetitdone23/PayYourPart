import React from 'react';
import { X, Check } from 'lucide-react';

export default function Comparison() {
  const oldWay = [
    "\"Who still owes me for the Airbnb?\"",
    "Awkward \"reminder\" texts at 11 PM.",
    "Spreadsheets that nobody updates.",
    "Lost receipts and forgotten items.",
  ];

  const newWay = [
    "Total clarity on who owes what.",
    "Automated, friendly nudge system.",
    "Real-time balance tracking.",
    "Settlement in one tap.",
  ];

  return (
    <section id="comparison" className="py-20 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-brand-900 tracking-tight">
            Life is better with us
          </h2>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch">
          
          {/* The Old Way */}
          <div className="bg-rose-50/15 border-2 border-rose-100/50 p-8 rounded-3xl space-y-6 flex flex-col justify-between hover:scale-[1.01] transition-transform">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-bold text-rose-950 flex items-center space-x-2">
                  <span>❌</span>
                  <span>The Old Way</span>
                </h3>
                <span className="text-[10px] uppercase font-black text-rose-600 bg-rose-100/60 px-2.5 py-1 rounded-full border border-rose-200/40">
                  Messy & Awkward
                </span>
              </div>
              <ul className="space-y-4 pt-2">
                {oldWay.map((item, idx) => (
                  <li key={idx} className="flex items-start space-x-3 text-slate-600">
                    <span className="w-5 h-5 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <X className="w-3.5 h-3.5 stroke-[3]" />
                    </span>
                    <span className="text-sm font-semibold leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* The New Way */}
          <div className="bg-emerald-50/15 border-2 border-emerald-100/50 p-8 rounded-3xl space-y-6 flex flex-col justify-between hover:scale-[1.01] transition-transform shadow-lg shadow-emerald-500/5">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-bold text-emerald-950 flex items-center space-x-2">
                  <span>✅</span>
                  <span>The New Way</span>
                </h3>
                <span className="text-[10px] uppercase font-black text-emerald-600 bg-emerald-100/60 px-2.5 py-1 rounded-full border border-emerald-200/40">
                  Easy & Transparent
                </span>
              </div>
              <ul className="space-y-4 pt-2">
                {newWay.map((item, idx) => (
                  <li key={idx} className="flex items-start space-x-3 text-slate-600">
                    <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="w-3.5 h-3.5 stroke-[3]" />
                    </span>
                    <span className="text-sm font-semibold leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
