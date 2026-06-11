import React from 'react';
import { Compass, Sparkles, RefreshCw, CreditCard, MessageSquare, LineChart } from 'lucide-react';

export default function Features() {
  const features = [
    {
      title: "Trip Splitting",
      description: "Multi-currency support for that Euro-trip. Split by percentage, shares, or exact amount.",
      icon: Compass,
    },
    {
      title: "Debt Simplification",
      description: "Our greedy settlement engine simplifies multi-party debts down to the absolute minimum transactions.",
      icon: Sparkles,
    },
    {
      title: "Recurring Bills",
      description: "Set it and forget it. Rent, Netflix, and utilities handled every month without a word.",
      icon: RefreshCw,
    },
    {
      title: "Settle Up Instantly",
      description: "Connect Venmo, PayPal, or Zelle. One-click settlement that actually updates your balance.",
      icon: CreditCard,
    },
    {
      title: "Group Chat",
      description: "Internal messaging for each group. \"Who bought the snacks?!\" solved in seconds.",
      icon: MessageSquare,
    },
    {
      title: "Spending Insights",
      description: "Visual charts show where your money is going. Spoiler alert: it's mostly coffee.",
      icon: LineChart,
    },
  ];

  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        
        {/* Header */}
        <div className="text-center space-y-4 max-w-2xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-brand-900 tracking-tight">
            Everything you need to stay even
          </h2>
          <p className="text-sm sm:text-base text-slate-500 leading-relaxed">
            We've built the most comprehensive splitting engine ever. Smooth, fast, and actually enjoyable to use.
          </p>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div 
                key={idx} 
                className="bg-purple-50/20 border border-purple-50/50 p-8 rounded-3xl space-y-5 hover:bg-purple-50/40 transition-colors"
              >
                <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                  <Icon className="w-5 h-5" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-brand-900">{feat.title}</h3>
                  <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">{feat.description}</p>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
