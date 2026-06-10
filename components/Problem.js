import React from 'react';
import { Utensils, Plane, Home } from 'lucide-react';

export default function Problem() {
  const problems = [
    {
      title: "Dinner Drama",
      description: "Calculating tax, tip, and who ordered that second drink is a nightmare in your head.",
      icon: Utensils,
      color: "text-amber-600 bg-amber-100",
    },
    {
      title: "Trip Tension",
      description: "Hotels, gas, and groceries... keeping track of who paid what across 5 days is impossible.",
      icon: Plane,
      color: "text-blue-600 bg-blue-100",
    },
    {
      title: "Roommate Rage",
      description: "Electricity, internet, and TP. Recurring bills shouldn't lead to recurring arguments.",
      icon: Home,
      color: "text-purple-600 bg-purple-100",
    },
  ];

  return (
    <section className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-12">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-brand-900 tracking-tight">
          Group expenses get messy fast.
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {problems.map((prob, idx) => {
            const IconComponent = prob.icon;
            return (
              <div 
                key={idx} 
                className="bg-white border border-slate-100 p-8 rounded-3xl shadow-sm hover:shadow-md transition-shadow text-left space-y-6"
              >
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${prob.color}`}>
                  <IconComponent className="w-6 h-6" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-brand-900">{prob.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{prob.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
