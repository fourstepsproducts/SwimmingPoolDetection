import React, { useState, useEffect } from 'react';
import { useAnalysis } from '../context/AnalysisContext';
import { 
  Layers, 
  Eye, 
  EyeOff, 
  Sliders, 
  Target, 
  RefreshCw, 
  PlayCircle
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const DEFAULT_POOL_VIDEO = '/sample-pool.mp4';

const PoolMarkings = () => {
  const { analysisResult } = useAnalysis();
  const host = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

  const [activeMediaUrl, setActiveMediaUrl] = useState(DEFAULT_POOL_VIDEO);
  const [activeMediaType, setActiveMediaType] = useState('video');
  const [mediaList, setMediaList] = useState([]);

  // Calibration corner state (4 actual water-surface corners)
  const [corners, setCorners] = useState([
    { x: 745.0, y: 75.0, label: 'TL (Top-Left)' },
    { x: 1275.0, y: 75.0, label: 'TR (Top-Right)' },
    { x: 1775.0, y: 405.0, label: 'BR (Bottom-Right)' },
    { x: 560.0, y: 430.0, label: 'BL (Bottom-Left)' },
  ]);

  const [showBoundary, setShowBoundary] = useState(true);
  const [showZones, setShowZones] = useState(true);
  const [showCorners, setShowCorners] = useState(false);
  const [showDetections, setShowDetections] = useState(false);

  const isAnyMarkingVisible = showBoundary || showZones || showCorners || showDetections;

  const toggleAllMarkings = () => {
    if (isAnyMarkingVisible) {
      setShowBoundary(false);
      setShowZones(false);
      setShowCorners(false);
      setShowDetections(false);
      toast.success('All contour overlays hidden.');
    } else {
      setShowBoundary(true);
      setShowZones(true);
      setShowCorners(false);
      setShowDetections(false);
      toast.success('Blue pool boundary and zones enabled.');
    }
  };

  useEffect(() => {
    axios.get(`${host}/api/calibration`)
      .then((res) => {
        if (res.data && Array.isArray(res.data.waterBoundary) && res.data.waterBoundary.length >= 4) {
          const wb = res.data.waterBoundary;
          const labels = ['TL (Top-Left)', 'TR (Top-Right)', 'BR (Bottom-Right)', 'BL (Bottom-Left)'];
          setCorners(wb.slice(0, 4).map((pt, idx) => ({
            x: pt.x,
            y: pt.y,
            label: labels[idx]
          })));
        }
      })
      .catch(() => {});

    axios.get(`${host}/api/latest-media`)
      .then((res) => {
        if (res.data && res.data.success && Array.isArray(res.data.mediaList)) {
          setMediaList(res.data.mediaList);
          
          if (analysisResult && analysisResult.processedUrl) {
            setActiveMediaUrl(`${host}${analysisResult.processedUrl}`);
            setActiveMediaType(analysisResult.mediaType || 'video');
          } else if (res.data.latest) {
            setActiveMediaUrl(`${host}${res.data.latest.url}`);
            setActiveMediaType(res.data.latest.mediaType);
          }
        }
      })
      .catch(() => {
        if (analysisResult && analysisResult.processedUrl) {
          setActiveMediaUrl(`${host}${analysisResult.processedUrl}`);
          setActiveMediaType(analysisResult.mediaType || 'video');
        }
      });
  }, [host, analysisResult]);

  const refW = 1920.0;
  const refH = 1080.0;

  const pTL = { x: (corners[0].x / refW) * 100, y: (corners[0].y / refH) * 100 };
  const pTR = { x: (corners[1].x / refW) * 100, y: (corners[1].y / refH) * 100 };
  const pBR = { x: (corners[2].x / refW) * 100, y: (corners[2].y / refH) * 100 };
  const pBL = { x: (corners[3].x / refW) * 100, y: (corners[3].y / refH) * 100 };

  const outerPoolPolygon = `${pTL.x},${pTL.y} ${pTR.x},${pTR.y} ${pBR.x},${pBR.y} ${pBL.x},${pBL.y}`;

  const leftDivider1 = { x: pTL.x + (1 / 3) * (pBL.x - pTL.x), y: pTL.y + (1 / 3) * (pBL.y - pTL.y) };
  const rightDivider1 = { x: pTR.x + (1 / 3) * (pBR.x - pTR.x), y: pTR.y + (1 / 3) * (pBR.y - pTR.y) };
  const leftDivider2 = { x: pTL.x + (2 / 3) * (pBL.x - pTL.x), y: pTL.y + (2 / 3) * (pBL.y - pTL.y) };
  const rightDivider2 = { x: pTR.x + (2 / 3) * (pBR.x - pTR.x), y: pTR.y + (2 / 3) * (pBR.y - pTR.y) };

  const redZonePolygon = `${pTL.x},${pTL.y} ${pTR.x},${pTR.y} ${rightDivider1.x},${rightDivider1.y} ${leftDivider1.x},${leftDivider1.y}`;
  const yellowZonePolygon = `${leftDivider1.x},${leftDivider1.y} ${rightDivider1.x},${rightDivider1.y} ${rightDivider2.x},${rightDivider2.y} ${leftDivider2.x},${leftDivider2.y}`;
  const greenZonePolygon = `${leftDivider2.x},${leftDivider2.y} ${rightDivider2.x},${rightDivider2.y} ${pBR.x},${pBR.y} ${pBL.x},${pBL.y}`;

  const currentMediaSrc = activeMediaUrl || DEFAULT_POOL_VIDEO;

  return (
    <div className="flex flex-col xl:flex-row gap-6 h-[calc(100vh-120px)] overflow-hidden">
      {/* Main Video Viewport (Left Column - 3/4 Width) */}
      <div className="flex-1 flex flex-col bg-brand-card border border-brand-border rounded-xl overflow-hidden relative shadow-2xl">
        {/* Header toolbar */}
        <div className="bg-brand-dark/90 px-4 py-3 border-b border-brand-border flex items-center justify-between z-20">
          <div className="flex items-center gap-3">
            <Layers className="w-4 h-4 text-cyan-400" />
            <div>
              <h3 className="text-xs font-extrabold text-white uppercase tracking-wider">
                SWIMMING POOL WATER BOUNDARY OUTLINE
              </h3>
              <span className="text-[10px] text-brand-muted font-mono block">
                Single Continuous Blue Waterline Outline
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {mediaList.length > 0 && (
              <div className="flex items-center gap-2 font-mono text-[10px]">
                <PlayCircle className="w-3.5 h-3.5 text-status-safe" />
                <select
                  value={activeMediaUrl || ''}
                  onChange={(e) => {
                    const selected = mediaList.find(m => `${host}${m.url}` === e.target.value);
                    if (selected) {
                      setActiveMediaUrl(`${host}${selected.url}`);
                      setActiveMediaType(selected.mediaType);
                      toast.success(`Loaded video: ${selected.filename}`);
                    }
                  }}
                  className="bg-brand-dark border border-brand-border text-white text-[10px] font-mono rounded px-2.5 py-1 focus:outline-none focus:border-cyan-400 uppercase font-bold"
                >
                  {mediaList.map((m, idx) => (
                    <option key={m.filename} value={`${host}${m.url}`}>
                      {`Pool Recording #${idx + 1} (${m.mediaType})`}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Master Toggle Button */}
            <button
              onClick={toggleAllMarkings}
              className={`px-3 py-1.5 rounded text-[10px] font-extrabold uppercase tracking-wider flex items-center gap-1.5 border shadow-md transition-all ${
                showBoundary
                  ? 'bg-blue-950/40 text-blue-300 border-blue-500/40 hover:bg-blue-900/60'
                  : 'bg-brand-border/40 text-brand-muted border-brand-border hover:bg-brand-border'
              }`}
            >
              {showBoundary ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
              <span>{showBoundary ? 'BLUE OUTLINE ON' : 'BLUE OUTLINE OFF'}</span>
            </button>
          </div>
        </div>

        {/* Video Canvas Container */}
        <div className="flex-1 bg-black relative flex items-center justify-center overflow-hidden radar-grid p-4">
          <div className="relative max-w-full max-h-[72vh] aspect-video w-full flex items-center justify-center rounded-lg overflow-hidden border border-brand-border/60 shadow-2xl bg-brand-dark/80">
            {activeMediaType === 'video' ? (
              <video 
                key={currentMediaSrc}
                src={currentMediaSrc} 
                controls 
                autoPlay 
                loop 
                muted 
                className="w-full h-full object-contain" 
              />
            ) : (
              <img 
                src={currentMediaSrc} 
                alt="Pool CCTV Frame" 
                className="w-full h-full object-contain" 
              />
            )}

            <svg 
              className="absolute inset-0 w-full h-full pointer-events-none z-10" 
              viewBox="0 0 100 100" 
              preserveAspectRatio="none"
            >
              {showZones && (
                <>
                  <polygon points={redZonePolygon} fill="rgba(239,68,68,0.25)" stroke="rgba(239,68,68,0.7)" strokeWidth="0.25" />
                  <polygon points={yellowZonePolygon} fill="rgba(245,158,11,0.25)" stroke="rgba(245,158,11,0.7)" strokeWidth="0.25" />
                  <polygon points={greenZonePolygon} fill="rgba(34,197,94,0.25)" stroke="rgba(34,197,94,0.7)" strokeWidth="0.25" />
                </>
              )}

              {showBoundary && (
                <polygon 
                  points={outerPoolPolygon} 
                  fill="none" 
                  stroke="#0284c7" 
                  strokeWidth="0.75" 
                  strokeLinejoin="round"
                />
              )}

              {showCorners && (
                <>
                  {[pTL, pTR, pBR, pBL].map((point, index) => (
                    <g key={index}>
                      <circle cx={point.x} cy={point.y} r="1.2" fill="#f8fafc" />
                    </g>
                  ))}
                </>
              )}

              {showDetections && analysisResult?.detections && analysisResult.detections.map((person, index) => (
                <g key={`${person.zone}-${index}`}>
                  <circle
                    cx={person.position?.x ?? 0}
                    cy={person.position?.y ?? 0}
                    r="0.8"
                    fill={person.zone === 'ZONE_3' ? '#f87171' : person.zone === 'ZONE_2' ? '#fbbf24' : '#4ade80'}
                    opacity="0.9"
                  />
                </g>
              ))}
            </svg>
          </div>
        </div>
      </div>

      {/* Boundary Controls Sidebar */}
      <div className="w-full xl:w-80 flex flex-col gap-5 overflow-y-auto shrink-0">
        <div className="bg-brand-card border border-brand-border rounded-xl p-4 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-brand-border pb-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <span>Boundary Overlay</span>
            </h4>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <label className="flex items-center justify-between p-2.5 bg-brand-dark/60 rounded-lg border border-brand-border/60 cursor-pointer hover:bg-brand-dark transition">
              <span className="text-brand-text font-medium">Blue Pool Boundary</span>
              <input 
                type="checkbox" 
                checked={showBoundary} 
                onChange={(e) => setShowBoundary(e.target.checked)}
                className="w-4 h-4 rounded accent-cyan-400"
              />
            </label>

            <label className="flex items-center justify-between p-2.5 bg-brand-dark/60 rounded-lg border border-brand-border/60 cursor-pointer hover:bg-brand-dark transition">
              <span className="text-brand-text font-medium">Three Depth Zones</span>
              <input 
                type="checkbox" 
                checked={showZones} 
                onChange={(e) => setShowZones(e.target.checked)}
                className="w-4 h-4 rounded accent-green-400"
              />
            </label>

            <label className="flex items-center justify-between p-2.5 bg-brand-dark/60 rounded-lg border border-brand-border/60 cursor-pointer hover:bg-brand-dark transition">
              <span className="text-brand-text font-medium">4-Corner Anchors</span>
              <input 
                type="checkbox" 
                checked={showCorners} 
                onChange={(e) => setShowCorners(e.target.checked)}
                className="w-4 h-4 rounded accent-violet-400"
              />
            </label>

            <label className="flex items-center justify-between p-2.5 bg-brand-dark/60 rounded-lg border border-brand-border/60 cursor-pointer hover:bg-brand-dark transition">
              <span className="text-brand-text font-medium">Person Tracking Dots</span>
              <input 
                type="checkbox" 
                checked={showDetections} 
                onChange={(e) => setShowDetections(e.target.checked)}
                className="w-4 h-4 rounded accent-orange-400"
              />
            </label>
          </div>
        </div>

        {/* 4-Corner Waterline Coordinates Panel */}
        <div className="bg-brand-card border border-brand-border rounded-xl p-4 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-brand-border pb-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-purple-400" />
              <span>Waterline Corners (1920x1080)</span>
            </h4>
          </div>

          <div className="space-y-2 font-mono text-[11px]">
            {corners.map((c, i) => (
              <div key={i} className="p-2.5 rounded-lg border border-brand-border/60 bg-brand-dark/40 flex items-center justify-between">
                <span className="font-bold text-white">{c.label}</span>
                <span className="font-bold text-cyan-300">X: {c.x} Y: {c.y}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PoolMarkings;
