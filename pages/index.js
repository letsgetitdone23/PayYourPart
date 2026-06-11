import React from 'react';
import Head from 'next/head';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Problem from '../components/Problem';
import Features from '../components/Features';
import HowItWorks from '../components/HowItWorks';
import InteractiveDemo from '../components/InteractiveDemo';
import StatsBar from '../components/StatsBar';
import Comparison from '../components/Comparison';
import CTA from '../components/CTA';
import Footer from '../components/Footer';

export default function Home() {
  const handleWatchDemo = () => {
    const el = document.getElementById('interactive-demo');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <Head>
        <title>PayYourPart — Split expenses. Keep friendships.</title>
        <meta name="description" content="PayYourPart makes shared bill splitting, expense tracking, and debt simplification effortless and real-time." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen flex flex-col bg-white text-slate-800 antialiased">
        <Navbar />
        
        <main className="flex-grow">
          <Hero onWatchDemo={handleWatchDemo} />
          <Problem />
          <Features />
          <HowItWorks />
          <InteractiveDemo />
          <StatsBar />
          <Comparison />
          <CTA />
        </main>

        <Footer />
      </div>
    </>
  );
}
