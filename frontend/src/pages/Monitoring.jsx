import React from 'react';
import { useAnalysis } from '../context/AnalysisContext';
import { Shield, EyeOff, AlertTriangle, Info, Play, Trash2, Users } from 'lucide-react';

const Monitoring = () => {
  const { analysisResult, clearAnalysis } = useAnalysis();
  const host = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

  const hasResult = !!analysisResult;
  const isVideo = hasResult && analysisResult.mediaType === 'video';
  const mediaUrl = hasResult ? `${host}${analysisResult.processedUrl}` : null;

  // Determine current safety status classes and color
  let statusText = 'NO ANALYSIS AVAILABLE';
  let statusColorClass = 'text-brand-muted bg-brand-border/40 border-brand-border';
  
  if (hasResult) {
    if (analysisResult.overallRisk === 'CRITICAL') {
      statusText = 'CRITICAL';
      statusColorClass = 'text-status-critical bg-status-critical/10 border-status-critical/30';
    } else if (analysisResult.overallRisk === 'WARNING') {
      statusText = 'WARNING';
      statusColorClass = 'text-status-warning bg-status-warning/10 border-status-warning/30';
    } else {
      statusText = 'SAFE';
      statusColorClass = 'text-status-safe bg-status-safe/10 border-status-safe/30';
    }
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 h-[calc(100vh-120px)] overflow-hidden">
      {/* CCTV Screen - Left Column (3/4 of layout) */}
      <div className="xl:col-span-3 flex flex-col bg-brand-card border border-brand-border rounded-xl overflow-hidden relative">
        {/* Stream Header */}
        <div className="bg-brand-dark/80 px-4 py-3 border-b border-brand-border flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <span className={`w-2.5 h-2.5 rounded-full ${hasResult ? 'bg-status-safe animate-pulse' : 'bg-status-offline'}`} />
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide uppercase">
                {hasResult ? `CCTV ANALYSED FEED (${analysisResult.mediaType.toUpperCase()})` : 'CCTV FEED'}
              </h3>
              <span className="text-[10px] text-brand-muted uppercase font-mono block">
                {hasResult ? 'YOLOv8 Core Computer Vision active' : 'Mode: Pool Visualization Fallback'}
              </span>
            </div>
          </div>
          
          {hasResult && (
            <button
              onClick={clearAnalysis}
              className="flex items-center gap-1.5 bg-red-950/40 hover:bg-status-critical/20 text-status-critical text-[10px] font-bold px-3 py-1.5 rounded uppercase tracking-wider transition-all border border-status-critical/30 shadow-md"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear Analysis</span>
            </button>
          )}
        </div>

        {/* Video Canvas Container */}
        <div className="flex-1 bg-black relative flex items-center justify-center overflow-hidden cctv-scanline radar-grid p-6">
          <div className="relative w-full h-full flex items-center justify-center">
            {hasResult && !isVideo ? (
              <img 
                src={mediaUrl} 
                alt="YOLOv8 Analyzed Snapshot" 
                className="max-w-full max-h-[70vh] object-contain rounded-lg border border-brand-border/50 shadow-2xl" 
              />
            ) : (
              <video 
                key={mediaUrl || '/sample-pool.mp4'}
                src={mediaUrl || '/sample-pool.mp4'} 
                controls 
                autoPlay 
                muted 
                className="max-w-full max-h-[70vh] object-contain rounded-lg border border-brand-border/50 shadow-2xl" 
              />
            )}
          </div>
        </div>
      </div>

      {/* Surveillance Controls & Analytics Sidebar */}
      <div className="flex flex-col gap-5 overflow-y-auto">
        {/* Monitoring Metrics Card */}
        <div className="bg-brand-card border border-brand-border rounded-xl p-4 flex flex-col gap-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-brand-muted border-b border-brand-border pb-2 flex items-center gap-2">
            <Shield className="w-4 h-4 text-status-safe" />
            <span>Monitoring Info</span>
          </h4>
          
          <div className="space-y-4">
            {/* Occupants Count */}
            <div className="flex flex-col">
              <span className="text-[10px] font-mono uppercase tracking-widest text-brand-muted">People Detected</span>
              <strong className="text-3xl font-black text-white mt-1">
                {hasResult ? analysisResult.occupancy : '0'}
              </strong>
            </div>

            {/* Zone Breakdowns */}
            <div className="grid grid-cols-3 gap-2 border-t border-b border-brand-border/60 py-3">
              <div className="flex flex-col">
                <span className="text-[9px] font-bold text-status-safe tracking-wider">LEVEL 1</span>
                <span className="text-xl font-black text-white">{hasResult ? analysisResult.zones.zone1 : 0}</span>
              </div>
              <div className="flex flex-col border-l border-r border-brand-border/60 px-2">
                <span className="text-[9px] font-bold text-status-warning tracking-wider">LEVEL 2</span>
                <span className="text-xl font-black text-white">{hasResult ? analysisResult.zones.zone2 : 0}</span>
              </div>
              <div className="flex flex-col pl-1">
                <span className="text-[9px] font-bold text-status-critical tracking-wider">LEVEL 3</span>
                <span className="text-xl font-black text-white">{hasResult ? analysisResult.zones.zone3 : 0}</span>
              </div>
            </div>

            {/* Current Alarm Status */}
            <div className="flex flex-col">
              <span className="text-[10px] font-mono uppercase tracking-widest text-brand-muted">Current Risk Status</span>
              <div className={`mt-2 py-2 px-3 border rounded text-xs font-bold text-center uppercase tracking-widest ${statusColorClass}`}>
                {statusText}
              </div>
            </div>
          </div>
        </div>

        {/* Aggregate Zone Counts Panel */}
        <div className="bg-brand-card border border-brand-border rounded-xl p-4 flex-1 flex flex-col justify-between">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-white border-b border-brand-border pb-3 flex items-center justify-between">
              <span>PEOPLE DETECTED</span>
              <span className="text-[10px] font-mono text-brand-muted">
                TOTAL: {hasResult ? analysisResult.occupancy : 0}
              </span>
            </h4>
            
            <div className="mt-4 space-y-3 font-mono text-xs">
              {/* Level 1 - Green */}
              <div className="p-3 bg-status-safe/10 border border-status-safe/30 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-sm bg-status-safe shrink-0" />
                  <div className="flex flex-col">
                    <span className="font-bold text-white uppercase text-[11px]">ZONE 1 / LEVEL 1 — GREEN</span>
                    <span className="text-[9px] text-brand-muted uppercase">Shallow Zone</span>
                  </div>
                </div>
                <strong className="text-xl font-black text-white">
                  {hasResult ? analysisResult.zones.zone1 : 0}
                </strong>
              </div>

              {/* Level 2 - Yellow */}
              <div className="p-3 bg-status-warning/10 border border-status-warning/30 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-sm bg-status-warning shrink-0" />
                  <div className="flex flex-col">
                    <span className="font-bold text-white uppercase text-[11px]">ZONE 2 / LEVEL 2 — YELLOW</span>
                    <span className="text-[9px] text-brand-muted uppercase">Medium Zone</span>
                  </div>
                </div>
                <strong className="text-xl font-black text-white">
                  {hasResult ? analysisResult.zones.zone2 : 0}
                </strong>
              </div>

              {/* Level 3 - Red */}
              <div className="p-3 bg-status-critical/10 border border-status-critical/30 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-sm bg-status-critical shrink-0" />
                  <div className="flex flex-col">
                    <span className="font-bold text-white uppercase text-[11px]">ZONE 3 / LEVEL 3 — RED</span>
                    <span className="text-[9px] text-brand-muted uppercase">Deep Zone</span>
                  </div>
                </div>
                <strong className="text-xl font-black text-white">
                  {hasResult ? analysisResult.zones.zone3 : 0}
                </strong>
              </div>
            </div>
          </div>

          {/* Total Summary Footer */}
          <div className="mt-4 pt-3 border-t border-brand-border/60 flex items-center justify-between px-1 font-mono">
            <span className="font-bold text-brand-muted uppercase tracking-wider text-[11px]">TOTAL IN POOL</span>
            <strong className="text-2xl font-black text-white">
              {hasResult ? analysisResult.occupancy : 0}
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Monitoring;
