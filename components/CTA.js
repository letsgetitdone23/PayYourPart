import React from 'react';

export default function CTA() {
  return (
    <section className="bg-indigo-600 text-white py-20 md:py-28 relative overflow-hidden">
      {/* Decorative blobs */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/20 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/20 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8 relative">
        <h2 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
          Pay your part. Keep the good times going.
        </h2>
        <p className="text-sm sm:text-lg text-indigo-100 max-w-xl mx-auto leading-relaxed">
          Join over 1 million people splitting fairly and living freely.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <button className="w-full sm:w-auto py-3.5 px-8 bg-white hover:bg-slate-50 text-indigo-600 font-bold rounded-2xl shadow-lg active:scale-[0.98] transition-all text-sm">
            Download Now
          </button>
          <button className="w-full sm:w-auto py-3.5 px-8 bg-transparent hover:bg-white/10 text-white font-bold rounded-2xl border-2 border-white shadow-sm active:scale-[0.98] transition-all text-sm">
            Contact Sales
          </button>
        </div>
      </div>
    </section>
  );
}
