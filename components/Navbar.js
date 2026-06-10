import React from 'react';

export default function Navbar() {
  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-purple-100 bg-white/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Logo */}
        <div className="flex items-center space-x-2 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-500 flex items-center justify-center shadow-md">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span className="text-xl font-bold tracking-tight text-brand-900">PayYourPart</span>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center space-x-8">
          <button onClick={() => scrollToSection('features')} className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">Features</button>
          <button onClick={() => scrollToSection('how-it-works')} className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">How It Works</button>
          <button onClick={() => scrollToSection('comparison')} className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">Pricing</button>
        </nav>

        {/* Actions */}
        <div className="flex items-center space-x-4">
          <a href="http://localhost:5000/login" className="text-sm font-medium text-slate-700 hover:text-indigo-600 transition-colors">Sign In</a>
          <a href="http://localhost:5000/register" className="text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-5 py-2.5 rounded-full shadow-sm shadow-indigo-600/10 hover:shadow-indigo-600/20 active:scale-[0.98] transition-all">
            Get Started
          </a>
        </div>
      </div>
    </header>
  );
}
