import React from 'react';

export default function StatsBar() {
  const stats = [
    { number: "450k", label: "Trips Managed" },
    { number: "12M+", label: "Expenses Split" },
    { number: "85%", label: "Friendships Saved" },
  ];

  return (
    <section className="w-full bg-indigo-600 py-10 md:py-16 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center items-center">
          {stats.map((stat, idx) => (
            <div key={idx} className="space-y-1">
              <span className="block text-4xl sm:text-5xl font-black tracking-tight">{stat.number}</span>
              <span className="block text-[11px] sm:text-xs font-bold uppercase tracking-widest text-indigo-200">{stat.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
