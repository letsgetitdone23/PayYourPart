import React from 'react';
import { X } from 'lucide-react';

export default function WatchDemoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-brand-900/40 backdrop-blur-sm p-4 sm:p-6 transition-all duration-300">
      
      {/* Modal Card */}
      <div className="relative w-full max-w-3xl bg-white rounded-3xl shadow-2xl border border-slate-100 overflow-hidden flex flex-col scale-[1] opacity-100 transition-all duration-300">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-50">
          <h3 className="text-md font-bold text-slate-900 flex items-center space-x-2">
            <span>🎬</span>
            <span>PayYourPart Product Tour</span>
          </h3>
          <button 
            onClick={onClose} 
            className="w-8 h-8 rounded-lg bg-slate-50 hover:bg-rose-50 text-slate-400 hover:text-rose-600 flex items-center justify-center transition-colors"
          >
            <X className="w-4.5 h-4.5" />
          </button>
        </div>

        {/* Video / Mockup Content */}
        <div className="relative aspect-video w-full bg-slate-950 flex items-center justify-center overflow-hidden">
          
          {/* Mock Video Placeholder */}
          <div className="absolute inset-0 bg-gradient-to-tr from-indigo-900 to-purple-900 flex flex-col items-center justify-center text-white space-y-4 p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center text-3xl shadow-inner animate-pulse">
              📱
            </div>
            <div className="space-y-1.5 max-w-md">
              <h4 className="text-lg font-extrabold">Watch how to scan receipts & split instantly</h4>
              <p className="text-xs text-indigo-200">
                This is a product demo showcasing our OCR scanning engine, automatic balance engine, and instant settlements integrations.
              </p>
            </div>
            
            <button className="py-2.5 px-6 bg-white hover:bg-slate-50 text-indigo-600 font-bold rounded-xl shadow-md transition-all active:scale-[0.98] text-xs">
              Play Product Tour
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}
