import React from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { useAnalysis } from '../context/AnalysisContext';
import { 
  Tv, 
  Upload, 
  Layers,
  ShieldAlert,
  Activity,
  Users
} from 'lucide-react';

const MainLayout = () => {
  const location = useLocation();
  const { analysisResult } = useAnalysis();

  const hasResult = !!analysisResult;

  const navigationItems = [
    { name: 'Monitoring', path: '/monitoring', icon: Tv },
    { name: 'Upload & Test', path: '/test', icon: Upload },
    { name: 'Pool Markings', path: '/markings', icon: Layers },
  ];

  // Risk status styling
  let riskText = '--';
  let riskColorClass = 'text-brand-muted';
  if (hasResult) {
    riskText = analysisResult.overallRisk;
    if (riskText === 'CRITICAL') riskColorClass = 'text-status-critical';
    else if (riskText === 'WARNING') riskColorClass = 'text-status-warning';
    else riskColorClass = 'text-status-safe';
  }

  return (
    <div className="flex h-screen bg-brand-dark text-brand-text overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-brand-card border-r border-brand-border flex flex-col justify-between shrink-0">
        <div>
          {/* Logo Section */}
          <div className="p-5 border-b border-brand-border flex items-center gap-3">
            <ShieldAlert className="w-7 h-7 text-status-critical animate-pulse" />
            <div>
              <h1 className="text-sm font-black tracking-wider text-white uppercase leading-none">PoolSafety AI</h1>
              <span className="text-[9px] text-brand-muted uppercase tracking-widest font-mono">Proof of Concept v1.0</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${
                    isActive
                      ? 'bg-brand-border text-white shadow-md border-r-2 border-r-status-safe'
                      : 'text-brand-muted hover:bg-brand-border/40 hover:text-white'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-status-safe' : 'text-brand-muted'}`} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-brand-border text-center">
          <span className="text-[9px] text-brand-muted font-mono uppercase tracking-widest">
            CV Security Lab Setup
          </span>
        </div>
      </aside>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-brand-card border-b border-brand-border flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-6">
            {/* Live Indicator */}
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${hasResult ? 'bg-status-safe glow-safe' : 'bg-status-offline animate-pulse'}`} />
              <span className="text-[10px] font-bold tracking-widest uppercase text-brand-muted font-mono">
                {hasResult 
                  ? `SURVEILLANCE MODE: ${analysisResult.mediaType.toUpperCase()} ANALYSED` 
                  : 'SURVEILLANCE MODE: SCHEMATIC fallbacks'}
              </span>
            </div>

            {/* Quick Metrics */}
            <div className="hidden md:flex items-center gap-4 text-[10px] uppercase font-mono text-brand-muted border-l border-brand-border pl-6">
              <div className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-brand-muted" />
                <span>Detected Occupants: <strong className="text-white">{hasResult ? analysisResult.occupancy : '--'}</strong></span>
              </div>
              <div className="flex items-center gap-1.5 ml-2">
                <Activity className="w-3.5 h-3.5 text-brand-muted" />
                <span>Risk Level: <strong className={riskColorClass}>{riskText}</strong></span>
              </div>
            </div>
          </div>

          {/* Time & User details */}
          <div className="flex items-center gap-4 text-[10px] font-mono">
            <span className="text-brand-muted uppercase hidden sm:inline">{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
            <div className="px-3 py-1 bg-brand-border/60 text-white rounded border border-brand-border uppercase tracking-wider font-bold">
              SYS_OPERATOR
            </div>
          </div>
        </header>

        {/* Content Outlet */}
        <main className="flex-1 overflow-y-auto bg-brand-dark p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
