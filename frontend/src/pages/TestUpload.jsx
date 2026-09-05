import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../context/AnalysisContext';
import api from '../services/api';
import { Video, Image, Upload, Play, RefreshCw, CheckCircle, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const TestUpload = () => {
  const navigate = useNavigate();
  const { setAnalysisResult } = useAnalysis();

  const [selectedVideo, setSelectedVideo] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeType, setAnalyzeType] = useState(null); // 'video' or 'image'

  // Progress and job state
  const [uploadState, setUploadState] = useState('IDLE'); // 'IDLE' | 'UPLOADING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  const [uploadPercent, setUploadPercent] = useState(0);
  const [uploadedBytes, setUploadedBytes] = useState(0);
  const [totalBytes, setTotalBytes] = useState(0);
  const [jobInfo, setJobInfo] = useState({
    progress: 0,
    framesProcessed: 0,
    peopleDetected: 0,
    jobId: null
  });

  const videoInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const abortControllerRef = useRef(null);
  const pollingIntervalRef = useRef(null);

  // Dynamic limits from environment variables
  const maxUploadSizeGb = parseFloat(import.meta.env.VITE_MAX_UPLOAD_SIZE_GB || '5');
  const maxUploadSizeBytes = maxUploadSizeGb * 1024 * 1024 * 1024;

  const poolPoints = {
    A: { x: parseFloat(import.meta.env.VITE_POOL_POINT_A_X || '600'), y: parseFloat(import.meta.env.VITE_POOL_POINT_A_Y || '300') },
    B: { x: parseFloat(import.meta.env.VITE_POOL_POINT_B_X || '1320'), y: parseFloat(import.meta.env.VITE_POOL_POINT_B_Y || '300') },
    C: { x: parseFloat(import.meta.env.VITE_POOL_POINT_C_X || '1800'), y: parseFloat(import.meta.env.VITE_POOL_POINT_C_Y || '950') },
    D: { x: parseFloat(import.meta.env.VITE_POOL_POINT_D_X || '120'), y: parseFloat(import.meta.env.VITE_POOL_POINT_D_Y || '950') }
  };

  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleVideoFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedMimeTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm'];
    const ext = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['mp4', 'mov', 'avi', 'mkv', 'webm'];

    if (!allowedMimeTypes.includes(file.type) && !allowedExtensions.includes(ext)) {
      toast.error('Unsupported video type. Upload .mp4, .mov, .avi, .mkv, or .webm.', {
        style: { background: '#141b2d', color: '#ef4444', border: '1px solid #ef4444' }
      });
      return;
    }

    if (file.size > maxUploadSizeBytes) {
      toast.error(
        `File is too large.\nMaximum supported size: ${maxUploadSizeGb} GB\nSelected file: ${(file.size / (1024 * 1024 * 1024)).toFixed(2)} GB`,
        {
          style: { background: '#141b2d', color: '#ef4444', border: '1px solid #ef4444' }
        }
      );
      return;
    }

    setSelectedVideo(file);
  };

  const handleImageFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    const ext = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp'];

    if (!allowedMimeTypes.includes(file.type) && !allowedExtensions.includes(ext)) {
      toast.error('Unsupported image type. Upload .jpg, .jpeg, .png, or .webp.', {
        style: { background: '#141b2d', color: '#ef4444', border: '1px solid #ef4444' }
      });
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image size exceeds 10MB limit.', {
        style: { background: '#141b2d', color: '#ef4444', border: '1px solid #ef4444' }
      });
      return;
    }

    setSelectedImage(file);
  };

  const startPollingJob = (jobId) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${jobId}`);
        const job = response.data;
        if (job) {
          setJobInfo({
            progress: job.progress,
            framesProcessed: job.framesProcessed,
            peopleDetected: job.peopleDetected,
            jobId: job.jobId
          });

          if (job.status === 'COMPLETED') {
            clearInterval(interval);
            setUploadState('COMPLETED');
            setIsAnalyzing(false);
            
            setAnalysisResult({
              type: 'video',
              ...job.result
            });
            
            toast.success('Video analysis complete!', {
              style: { background: '#141b2d', color: '#10b981', border: '1px solid #10b981' }
            });
            navigate('/monitoring');
          } else if (job.status === 'FAILED') {
            clearInterval(interval);
            setUploadState('FAILED');
            setIsAnalyzing(false);
            toast.error(job.error || 'Video analysis failed.', {
              style: { background: '#141b2d', color: '#ef4444', border: '1px solid #ef4444' }
            });
          }
        }
      } catch (err) {
        console.error('Error polling job status:', err);
      }
    }, 1500);

    pollingIntervalRef.current = interval;
  };

  const handleStartVideoAnalysis = async () => {
    if (!selectedVideo) return;

    const formData = new FormData();
    formData.append('video', selectedVideo);
    formData.append('poolPoints', JSON.stringify(poolPoints));

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setUploadState('UPLOADING');
    setUploadPercent(0);
    setUploadedBytes(0);
    setTotalBytes(selectedVideo.size);
    setAnalyzeType('video');
    setIsAnalyzing(true);

    setJobInfo({
      progress: 0,
      framesProcessed: 0,
      peopleDetected: 0,
      jobId: null
    });

    try {
      const response = await api.post('/analyze-video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        signal: controller.signal,
        onUploadProgress: (progressEvent) => {
          const total = progressEvent.total || selectedVideo.size;
          const current = progressEvent.loaded;
          const percent = Math.min(99, Math.round((current * 100) / total));
          setUploadPercent(percent);
          setUploadedBytes(current);
          setTotalBytes(total);
        }
      });

      if (response.data && response.data.success) {
        const { jobId } = response.data;
        setUploadPercent(100);
        setUploadState('PROCESSING');
        setJobInfo(prev => ({ ...prev, jobId }));
        startPollingJob(jobId);
      } else {
        throw new Error(response.data.error || 'Video upload failed.');
      }
    } catch (err) {
      if (err.name === 'CanceledError' || axios.isCancel(err) || controller.signal.aborted) {
        toast.error('Upload cancelled.', {
          style: { background: '#141b2d', color: '#f59e0b', border: '1px solid #f59e0b' }
        });
        resetUploadState();
      } else {
        console.error(err);
        toast.error(err.response?.data?.error || err.message || 'Error occurred during video upload.', {
          style: { background: '#141b2d', color: '#ef4444', border: '1px solid #ef4444' }
        });
        setUploadState('FAILED');
        setIsAnalyzing(false);
      }
    }
  };

  const handleStartImageAnalysis = async () => {
    if (!selectedImage) return;

    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('poolPoints', JSON.stringify(poolPoints));

    setIsAnalyzing(true);
    setAnalyzeType('image');
    const loadToastId = toast.loading('Uploading and analyzing image (YOLOv8)...', {
      style: { background: '#141b2d', color: '#fff', border: '1px solid #1f293d' }
    });

    try {
      const response = await api.post('/analyze-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data && response.data.success) {
        setAnalysisResult({
          type: 'image',
          ...response.data
        });
        toast.dismiss(loadToastId);
        toast.success('Image analysis complete!', {
          style: { background: '#141b2d', color: '#10b981', border: '1px solid #10b981' }
        });
        navigate('/monitoring');
      } else {
        throw new Error(response.data.error || 'Image analysis failed.');
      }
    } catch (err) {
      console.error(err);
      toast.dismiss(loadToastId);
      toast.error(err.response?.data?.error || err.message || 'Error occurred during image analysis.', {
        style: { background: '#141b2d', color: '#ef4444', border: '1px solid #ef4444' }
      });
    } finally {
      setIsAnalyzing(false);
      setAnalyzeType(null);
    }
  };

  const handleCancel = async () => {
    if (uploadState === 'UPLOADING') {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    } else if (uploadState === 'PROCESSING') {
      const jobId = jobInfo.jobId;
      if (jobId) {
        try {
          await api.post(`/jobs/${jobId}/cancel`);
        } catch (err) {
          console.error('Error cancelling background job:', err);
        }
      }
      toast.error('Analysis cancelled by user.', {
        style: { background: '#141b2d', color: '#f59e0b', border: '1px solid #f59e0b' }
      });
      resetUploadState();
    }
  };

  const resetUploadState = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
    setUploadState('IDLE');
    setUploadPercent(0);
    setUploadedBytes(0);
    setTotalBytes(0);
    setJobInfo({ progress: 0, framesProcessed: 0, peopleDetected: 0, jobId: null });
    setIsAnalyzing(false);
    setAnalyzeType(null);
  };

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-4">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h2 className="text-xl font-extrabold text-white uppercase tracking-wider">AI TEST & UPLOAD CONSOLE</h2>
        <p className="text-xs text-brand-muted uppercase">Upload sample swimming pool footage or snapshots to verify computer vision detection and safety boundary classifications.</p>
      </div>

      {isAnalyzing && analyzeType === 'image' && (
        /* Image scanning overlay */
        <div className="bg-brand-card/90 border border-status-safe/30 rounded-xl p-6 flex flex-col items-center justify-center gap-4 relative overflow-hidden animate-pulse">
          <RefreshCw className="w-8 h-8 text-status-safe animate-spin" />
          <div className="text-center">
            <h4 className="text-sm font-bold text-white uppercase tracking-widest">
              Analyzing CCTV Image Scan
            </h4>
            <p className="text-[10px] text-brand-muted uppercase mt-1">Please keep this window open. YOLOv8 is running static snapshot scan...</p>
          </div>
          <div className="absolute left-0 right-0 h-[2px] bg-status-safe shadow-[0_0_15px_#10b981] w-full top-1/2 animate-bounce" />
        </div>
      )}

      {isAnalyzing && analyzeType === 'video' && (
        /* Detailed Video Upload and Processing panel */
        <div className="bg-brand-card border border-brand-border rounded-xl p-6 flex flex-col gap-6 relative overflow-hidden">
          <div className="flex flex-col gap-1">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-status-warning animate-spin" />
              <span>CCTV Video Processing Console</span>
            </h4>
            <span className="text-[10px] text-brand-muted uppercase font-mono">
              Job ID: {jobInfo.jobId || 'Generating...'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* File info and state */}
            <div className="flex flex-col gap-4">
              <div className="p-4 bg-brand-dark/40 border border-brand-border rounded-lg flex flex-col gap-2">
                <span className="text-[10px] text-brand-muted uppercase font-mono">Selected File</span>
                <strong className="text-xs text-white font-mono truncate">{selectedVideo?.name}</strong>
                <span className="text-xs text-brand-muted font-mono">
                  Size: {formatSize(selectedVideo?.size || 0)}
                </span>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] text-brand-muted uppercase font-mono">State</span>
                <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded border self-start ${
                  uploadState === 'UPLOADING' ? 'text-status-warning bg-status-warning/10 border-status-warning/30' :
                  uploadState === 'PROCESSING' ? 'text-blue-400 bg-blue-400/10 border-blue-400/30' :
                  'text-brand-muted bg-brand-border/40 border-brand-border'
                }`}>
                  {uploadState}
                </span>
              </div>
            </div>

            {/* Dynamic Status Metric Counters */}
            <div className="p-4 bg-brand-dark/60 border border-brand-border rounded-lg flex flex-col gap-3 font-mono text-xs">
              <div className="flex justify-between border-b border-brand-border/60 pb-2">
                <span className="text-brand-muted uppercase">Frames Processed:</span>
                <strong className="text-white">{jobInfo.framesProcessed.toLocaleString()}</strong>
              </div>
              <div className="flex justify-between border-b border-brand-border/60 pb-2">
                <span className="text-brand-muted uppercase">People Detected:</span>
                <strong className="text-status-warning font-bold">{jobInfo.peopleDetected}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-brand-muted uppercase">Video Progress:</span>
                <strong className="text-white">{jobInfo.progress}%</strong>
              </div>
            </div>
          </div>

          {/* Progress Bars Section */}
          <div className="flex flex-col gap-4 border-t border-brand-border/60 pt-4">
            {uploadState === 'UPLOADING' && (
              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-[10px] font-mono text-brand-muted uppercase">
                  <span>Uploading CCTV video...</span>
                  <span>{uploadPercent}%</span>
                </div>
                <div className="w-full h-3 bg-brand-dark rounded-full overflow-hidden border border-brand-border">
                  <div 
                    className="h-full bg-status-warning transition-all duration-300 shadow-[0_0_10px_#f59e0b]"
                    style={{ width: `${uploadPercent}%` }}
                  />
                </div>
                <div className="text-[10px] font-mono text-brand-muted text-right">
                  {formatSize(uploadedBytes)} / {formatSize(totalBytes)}
                </div>
              </div>
            )}

            {uploadState === 'PROCESSING' && (
              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-[10px] font-mono text-brand-muted uppercase">
                  <span>Analyzing frames (YOLOv8)...</span>
                  <span>{jobInfo.progress}%</span>
                </div>
                <div className="w-full h-3 bg-brand-dark rounded-full overflow-hidden border border-brand-border">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-300 shadow-[0_0_10px_#3b82f6]"
                    style={{ width: `${jobInfo.progress}%` }}
                  />
                </div>
                <div className="text-[10px] font-mono text-brand-muted">
                  Optimized stride scan in progress. Extracting people detections...
                </div>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <button
            onClick={handleCancel}
            className="self-end px-6 py-2 bg-red-950/40 hover:bg-status-critical/20 text-status-critical border border-status-critical/30 rounded-lg text-xs font-bold uppercase tracking-wider transition-all cursor-pointer"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Upload Cards Grid */}
      <div className={`grid grid-cols-1 md:grid-cols-2 gap-6 ${isAnalyzing ? 'hidden' : ''}`}>
        {/* Card 1: Video Upload */}
        <div className={`bg-brand-card border border-brand-border rounded-xl p-5 flex flex-col justify-between transition-all ${isAnalyzing ? 'opacity-40 pointer-events-none' : ''}`}>
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-status-warning/10 border border-status-warning/30 rounded-lg text-status-warning">
                <Video className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wide">Upload CCTV Video</h3>
                <span className="text-[10px] text-brand-muted uppercase font-mono">
                  Supported: MP4 / MOV / AVI / MKV / WEBM
                </span>
              </div>
            </div>

            {/* Selector box */}
            <div 
              onClick={() => videoInputRef.current.click()}
              className="border-2 border-dashed border-brand-border hover:border-brand-muted/40 rounded-lg p-8 flex flex-col items-center justify-center gap-2 cursor-pointer bg-brand-dark/30 transition hover:bg-brand-dark/50"
            >
              <Upload className="w-6 h-6 text-brand-muted" />
              <span className="text-xs font-semibold text-white">Choose Video File</span>
              <span className="text-[10px] text-brand-muted">Supported: MP4 / MOV / AVI / MKV / WEBM</span>
              <span className="text-[10px] text-status-warning font-mono">Maximum: {maxUploadSizeGb} GB</span>
              <input 
                type="file" 
                ref={videoInputRef}
                accept=".mp4,.mov,.avi,.mkv,.webm"
                onChange={handleVideoFileChange}
                className="hidden"
              />
            </div>

            {/* Selected File Details */}
            {selectedVideo && (
              <div className="p-3 bg-brand-dark/60 border border-brand-border rounded-lg flex flex-col gap-2">
                <div className="flex items-center gap-2 text-xs">
                  <FileText className="w-4 h-4 text-status-warning shrink-0" />
                  <span className="text-white font-mono truncate">{selectedVideo.name}</span>
                </div>
                
                <div className="border-t border-brand-border/60 pt-2 flex flex-col gap-1 text-[10px] font-mono text-brand-muted">
                  <div className="flex justify-between">
                    <span>Analysis Type:</span>
                    <span className="text-status-warning font-bold">Stride Frame Scan</span>
                  </div>
                  <div className="flex justify-between">
                    <span>File size:</span>
                    <span>{formatSize(selectedVideo.size)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleStartVideoAnalysis}
            disabled={!selectedVideo || isAnalyzing}
            className={`w-full mt-6 flex items-center justify-center gap-2 py-3 rounded-lg text-xs font-bold uppercase tracking-wider border transition-all ${
              selectedVideo && !isAnalyzing
                ? 'bg-status-warning hover:bg-amber-600 active:bg-amber-700 text-brand-dark border-status-warning cursor-pointer shadow-lg shadow-status-warning/10'
                : 'bg-brand-border border-brand-border text-brand-muted cursor-not-allowed'
            }`}
          >
            <Play className="w-4 h-4" />
            <span>Start Video Analysis</span>
          </button>
        </div>

        {/* Card 2: Image Upload */}
        <div className={`bg-brand-card border border-brand-border rounded-xl p-5 flex flex-col justify-between transition-all ${isAnalyzing ? 'opacity-40 pointer-events-none' : ''}`}>
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-status-safe/10 border border-status-safe/30 rounded-lg text-status-safe">
                <Image className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wide">Upload Snapshot Image</h3>
                <span className="text-[10px] text-brand-muted uppercase font-mono">Supported: JPG / JPEG / PNG / WEBP</span>
              </div>
            </div>

            {/* Selector box */}
            <div 
              onClick={() => imageInputRef.current.click()}
              className="border-2 border-dashed border-brand-border hover:border-brand-muted/40 rounded-lg p-8 flex flex-col items-center justify-center gap-2 cursor-pointer bg-brand-dark/30 transition hover:bg-brand-dark/50"
            >
              <Upload className="w-6 h-6 text-brand-muted" />
              <span className="text-xs font-semibold text-white">Choose Image File</span>
              <span className="text-[10px] text-brand-muted">Supported: .jpg, .jpeg, .png, .webp</span>
              <span className="text-[10px] text-status-safe font-mono">Maximum: 10 MB</span>
              <input 
                type="file" 
                ref={imageInputRef}
                accept=".jpg,.jpeg,.png,.webp"
                onChange={handleImageFileChange}
                className="hidden"
              />
            </div>

            {/* Selected File Details */}
            {selectedImage && (
              <div className="p-3 bg-brand-dark/60 border border-brand-border rounded-lg flex flex-col gap-2">
                <div className="flex items-center gap-2 text-xs">
                  <FileText className="w-4 h-4 text-status-safe shrink-0" />
                  <span className="text-white font-mono truncate">{selectedImage.name}</span>
                </div>
                
                <div className="border-t border-brand-border/60 pt-2 flex flex-col gap-1 text-[10px] font-mono text-brand-muted">
                  <div className="flex justify-between">
                    <span>Analysis Type:</span>
                    <span className="text-status-safe font-bold">Static Snapshot Scan</span>
                  </div>
                  <div className="flex justify-between">
                    <span>File size:</span>
                    <span>{formatSize(selectedImage.size)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleStartImageAnalysis}
            disabled={!selectedImage || isAnalyzing}
            className={`w-full mt-6 flex items-center justify-center gap-2 py-3 rounded-lg text-xs font-bold uppercase tracking-wider border transition-all ${
              selectedImage && !isAnalyzing
                ? 'bg-status-safe hover:bg-emerald-600 active:bg-emerald-700 text-white border-status-safe cursor-pointer shadow-lg shadow-status-safe/10'
                : 'bg-brand-border border-brand-border text-brand-muted cursor-not-allowed'
            }`}
          >
            <Play className="w-4 h-4" />
            <span>Start Image Analysis</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestUpload;
