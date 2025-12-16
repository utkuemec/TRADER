import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Activity, BarChart3, TrendingUp, Zap } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-cyber-gradient grid-bg relative">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-cyan/5 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-pink/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-neon-cyan/20">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <motion.div 
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="relative">
                <Zap className="w-8 h-8 text-neon-cyan" />
                <div className="absolute inset-0 w-8 h-8 text-neon-cyan blur-sm opacity-50">
                  <Zap className="w-8 h-8" />
                </div>
              </div>
              <div>
                <h1 className="font-display text-xl font-bold tracking-wider text-white">
                  TRADER
                </h1>
                <p className="text-[10px] text-neon-cyan/70 tracking-widest uppercase">
                  Institutional Analysis
                </p>
              </div>
            </motion.div>

            {/* Nav Links */}
            <motion.nav 
              className="hidden md:flex items-center gap-6"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <NavLink icon={<BarChart3 className="w-4 h-4" />} label="Dashboard" active />
              <NavLink icon={<TrendingUp className="w-4 h-4" />} label="Analysis" />
              <NavLink icon={<Activity className="w-4 h-4" />} label="Signals" />
            </motion.nav>

            {/* Status Indicator */}
            <motion.div 
              className="flex items-center gap-2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-bullish/30">
                <div className="w-2 h-2 rounded-full bg-bullish animate-pulse" />
                <span className="text-xs font-mono text-bullish">LIVE</span>
              </div>
            </motion.div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 relative z-10">
        {children}
      </main>

      {/* Footer */}
      <footer className="glass border-t border-neon-cyan/10 py-4 mt-auto">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span className="font-mono">© 2024 TRADER Platform</span>
            <span className="font-mono">Real-time Institutional Analysis</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

interface NavLinkProps {
  icon: ReactNode;
  label: string;
  active?: boolean;
}

function NavLink({ icon, label, active }: NavLinkProps) {
  return (
    <button
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
        active
          ? 'bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30'
          : 'text-gray-400 hover:text-white hover:bg-white/5'
      }`}
    >
      {icon}
      <span className="font-medium text-sm">{label}</span>
    </button>
  );
}

