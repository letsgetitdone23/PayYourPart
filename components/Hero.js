import React from 'react';
import Image from 'next/image';

export default function Hero({ onWatchDemo }) {
  const rawBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';
  const backendUrl = rawBackendUrl.replace(/\/login\/?$/, '').replace(/\/$/, '');
  return (
    <section className="relative w-full overflow-hidden bg-gradient-to-b from-purple-50/50 to-white py-20 lg:py-32">
      {/* Background blobs */}
      <div className="absolute top-1/4 left-1/2 w-[500px] h-[500px] bg-indigo-200/20 rounded-full blur-[120px] pointer-events-none -z-10 -translate-x-1/2"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        
        {/* Left Column */}
        <div className="lg:col-span-7 text-left space-y-6">

          {/* Headline */}
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-brand-900 leading-[1.1]">
            Split expenses.<br />
            Keep friendships<span className="text-indigo-600">.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-500 max-w-xl leading-relaxed">
            Whether it's a cross-country road trip or a Friday night dinner, PayYourPart makes settling up effortless and transparent.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
            <a href={`${backendUrl}/register`} className="text-center py-3.5 px-8 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl shadow-lg shadow-indigo-600/15 hover:shadow-indigo-600/25 active:scale-[0.98] transition-all text-sm">
              Start Free
            </a>
            <button 
              onClick={onWatchDemo}
              className="flex items-center justify-center space-x-2 py-3.5 px-8 bg-white hover:bg-slate-50 text-indigo-600 font-bold rounded-2xl border border-slate-200 shadow-sm active:scale-[0.98] transition-all text-sm"
            >
              {/* Play Icon */}
              <svg className="w-5 h-5 text-indigo-600" viewBox="0 0 24 24" fill="currentColor">
                <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm14.02-1.09a.75.75 0 000-1.32l-5.75-3.4a.75.75 0 00-1.12.65v6.8a.75.75 0 001.12.65l5.75-3.4z" clipRule="evenodd" />
              </svg>
              <span>Watch Demo</span>
            </button>
          </div>


        </div>

        {/* Right Column (Floating UI Illustration) */}
        <div className="lg:col-span-5 relative flex justify-center">
          <div className="relative w-full max-w-[400px]">
            {/* Blob behind */}
            <div className="absolute inset-0 bg-indigo-500/10 rounded-full blur-[80px]"></div>
            
            {/* The main card */}
            <div className="relative bg-white border border-slate-100 rounded-3xl shadow-2xl p-6 space-y-6 hover:translate-y-[-4px] transition-all duration-300">
              
              {/* Top info */}
              <div className="flex items-center justify-between border-b border-slate-50 pb-4">
                <div>
                  <h3 className="text-md font-bold text-slate-900">Road Trip split</h3>
                  <p className="text-xs text-slate-400">Pondicherry • 4 members</p>
                </div>
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full">Active</span>
              </div>

              {/* Settlement Card mockup */}
              <div className="bg-slate-50 rounded-2xl p-4 flex items-center justify-between border border-slate-100/50">
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shadow-sm">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <span className="block text-xs font-bold text-emerald-800 uppercase tracking-wider">Success</span>
                    <span className="text-xs font-semibold text-slate-900">Sarah paid you</span>
                  </div>
                </div>
                <div>
                  <span className="text-lg font-extrabold text-slate-900">₹4,250.00</span>
                </div>
              </div>

              {/* Balances list mockup */}
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-[10px]">A</div>
                    <span className="font-medium text-slate-700">Alex</span>
                  </div>
                  <span className="font-bold text-rose-500">-₹2,125.00</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-[10px]">J</div>
                    <span className="font-medium text-slate-700">John</span>
                  </div>
                  <span className="font-bold text-emerald-500">+₹2,125.00</span>
                </div>
              </div>
              
            </div>

            {/* Micro Badge floating */}
            <div className="absolute top-[-20px] right-[-20px] bg-indigo-600 text-white text-[11px] font-bold px-3 py-1.5 rounded-2xl shadow-lg rotate-[6deg] hidden sm:block">
              ⚡️ Realtime
            </div>
            
          </div>
        </div>

      </div>
    </section>
  );
}
