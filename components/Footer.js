import React from 'react';
import { Share2, Globe, Github } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-50 border-t border-purple-100 py-16 text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Top grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10">
          
          {/* Brand info (Col 1-4) */}
          <div className="md:col-span-4 space-y-6">
            <div className="flex items-center space-x-2">
              <img src="/logo.png" alt="PayYourPart Logo" className="w-8 h-8 object-contain" />
              <span className="text-lg font-bold tracking-tight text-brand-900">PayYourPart</span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 max-w-xs leading-relaxed">
              Built for shared experiences, not just shared bills.
            </p>
            <div className="flex items-center space-x-4">
              <a href="#" className="w-8 h-8 rounded-lg bg-white border border-slate-100 flex items-center justify-center hover:bg-slate-50 text-slate-400 hover:text-indigo-600 transition-colors">
                <Share2 className="w-4 h-4" />
              </a>
              <a href="#" className="w-8 h-8 rounded-lg bg-white border border-slate-100 flex items-center justify-center hover:bg-slate-50 text-slate-400 hover:text-indigo-600 transition-colors">
                <Globe className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Product Links (Col 5-7) */}
          <div className="md:col-span-2 space-y-4">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-widest">Product</h4>
            <ul className="space-y-2.5 text-xs sm:text-sm">
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Features</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Integrations</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Changelog</a></li>
            </ul>
          </div>

          {/* Support Links (Col 8-10) */}
          <div className="md:col-span-2 space-y-4">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-widest">Support</h4>
            <ul className="space-y-2.5 text-xs sm:text-sm">
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Help Center</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Safety</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Privacy Policy</a></li>
            </ul>
          </div>

          {/* App Stores Badges (Col 11-12) */}
          <div className="md:col-span-4 space-y-4">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-widest">Get the App</h4>
            <div className="flex flex-col sm:flex-row md:flex-col gap-3">
              
              {/* App Store Mock badge */}
              <a href="#" className="bg-black text-white px-4 py-2 rounded-xl flex items-center space-x-3 w-44 hover:opacity-90 transition-opacity">
                <svg className="w-5 h-5 text-white fill-current" viewBox="0 0 24 24">
                  <path d="M18.71,19.5C17.88,20.74 17,21.95 15.66,22C14.32,22.05 13.89,21.24 12.37,21.24C10.84,21.24 10.37,21.97 9.1,22.03C7.79,22.08 6.8,20.72 5.96,19.5C4.26,17 2.94,12.45 4.7,9.39C5.57,7.87 7.13,6.91 8.82,6.88C10.1,6.86 11.32,7.75 12.11,7.75C12.89,7.75 14.37,6.68 15.92,6.84C16.57,6.87 18.39,7.1 19.56,8.82C19.47,8.88 17.39,10.1 17.41,12.63C17.44,15.65 20.06,16.66 20.1,16.67C20.08,16.74 19.67,18.11 18.71,19.5M15.97,4.17C16.63,3.37 17.07,2.28 16.95,1C16,1.04 14.9,1.6 14.24,2.38C13.68,3.04 13.19,4.14 13.34,5.39C14.39,5.47 15.4,4.88 15.97,4.17Z" />
                </svg>
                <div>
                  <span className="block text-[9px] uppercase tracking-wider text-slate-400">Download on the</span>
                  <span className="block text-xs font-bold leading-none">App Store</span>
                </div>
              </a>

              {/* Google Play Mock badge */}
              <a href="#" className="bg-black text-white px-4 py-2 rounded-xl flex items-center space-x-3 w-44 hover:opacity-90 transition-opacity">
                <svg className="w-5 h-5 text-white fill-current" viewBox="0 0 24 24">
                  <path d="M3,5.27V18.73L16.55,12L3,5.27M17.87,11.33L19.46,12.12C20.18,12.48 20.18,13.5 19.46,13.88L17.87,14.67L15.5,13.5L17.87,11.33M3,3.5C3,3.17 3.27,2.9 3.6,2.9C3.77,2.9 3.93,2.97 4.05,3.1L20.25,11.2C20.75,11.45 20.95,12.07 20.7,12.57C20.6,12.77 20.44,12.93 20.25,13.03L4.05,21.13C3.55,21.38 2.93,21.18 2.68,20.68C2.58,20.48 2.5,20.27 2.5,20.05V3.5M14,12.75L4.5,17.5V7.5L14,12.25" />
                </svg>
                <div>
                  <span className="block text-[9px] uppercase tracking-wider text-slate-400">Get it on</span>
                  <span className="block text-xs font-bold leading-none">Google Play</span>
                </div>
              </a>

            </div>
          </div>

        </div>

        {/* Bottom footer */}
        <div className="flex flex-col sm:flex-row items-center justify-between border-t border-purple-100/50 pt-8 text-xs text-slate-400">
          <p>© 2026 PayYourPart. Built for shared experiences.</p>
          <p className="mt-2 sm:mt-0">Built with Next.js & TailwindCSS</p>
        </div>

      </div>
    </footer>
  );
}
