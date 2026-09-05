import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import connectDB from './config/db.js';
import healthRoutes from './routes/health.js';
import { runAIAnalysis } from './services/aiService.js';

dotenv.config();

const app = express();

// Enable Cross-Origin Resource Sharing
const corsOrigin = process.env.CORS_ORIGIN || '*';
app.use(cors({
  origin: corsOrigin,
  methods: ['GET', 'POST'],
  credentials: true
}));

app.use(express.json());

// Prepare static serving for uploaded CCTV images and videos
const uploadDir = 'uploads';
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}
app.use('/uploads', express.static(uploadDir));

// Multer Storage Configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, `pool-${uniqueSuffix}${ext}`);
  }
});

// Image Filter
const imageFileFilter = (req, file, cb) => {
  const allowedExtensions = ['.png', '.jpg', '.jpeg', '.webp'];
  const ext = path.extname(file.originalname).toLowerCase();
  if (allowedExtensions.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error('Invalid image type. Only .jpg, .jpeg, .png, and .webp are accepted.'), false);
  }
};

const uploadImage = multer({
  storage: storage,
  fileFilter: imageFileFilter,
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Video Filter
const maxUploadSizeGb = parseFloat(process.env.MAX_UPLOAD_SIZE_GB || '5');
const maxUploadSizeBytes = maxUploadSizeGb * 1024 * 1024 * 1024;

const videoFileFilter = (req, file, cb) => {
  const allowedExtensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm'];
  const ext = path.extname(file.originalname).toLowerCase();
  if (allowedExtensions.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error('Invalid video type. Only .mp4, .mov, .avi, .mkv, and .webm are accepted.'), false);
  }
};

const uploadVideo = multer({
  storage: storage,
  fileFilter: videoFileFilter,
  limits: { fileSize: maxUploadSizeBytes }
});

// Job tracking state in-memory
const jobs = new Map();

// Register API routes
app.use('/api', healthRoutes);

// Endpoint to fetch current pool calibration
app.get('/api/calibration', (req, res) => {
  const configPath = path.join(process.cwd(), 'config', 'poolCalibration.json');
  if (fs.existsSync(configPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      return res.status(200).json(data);
    } catch (e) {
      return res.status(500).json({ success: false, error: e.message });
    }
  }
  return res.status(200).json({
    waterBoundary: [
      { x: 660.0, y: 80.0 },
      { x: 1080.0, y: 80.0 },
      { x: 1455.0, y: 350.0 },
      { x: 460.0, y: 400.0 }
    ]
  });
});

// Endpoint to list uploaded/processed media files for video playback
app.get('/api/latest-media', (req, res) => {
  const dirPath = path.join(process.cwd(), uploadDir);
  if (!fs.existsSync(dirPath)) {
    return res.status(200).json({ success: false, media: [] });
  }

  try {
    const files = fs.readdirSync(dirPath)
      .filter(f => f.startsWith('processed-') && (f.endsWith('.mp4') || f.endsWith('.jpg') || f.endsWith('.png')))
      .map(f => {
        const stat = fs.statSync(path.join(dirPath, f));
        return {
          filename: f,
          url: `/uploads/${f}`,
          mediaType: f.endsWith('.mp4') ? 'video' : 'image',
          mtime: stat.mtimeMs
        };
      })
      .sort((a, b) => b.mtime - a.mtime);

    return res.status(200).json({
      success: true,
      latest: files.length > 0 ? files[0] : null,
      mediaList: files
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
});

// Endpoint to analyze uploaded pool image
app.post('/api/analyze-image', (req, res) => {
  uploadImage.single('image')(req, res, async (err) => {
    if (err) {
      console.error(`❌ Multer Image Upload Error: ${err.message}`);
      return res.status(400).json({ success: false, error: err.message });
    }

    if (!req.file) {
      return res.status(400).json({ success: false, error: 'No image file uploaded.' });
    }

    try {
      const boundary1 = req.body.boundary1 ? parseFloat(req.body.boundary1) : 33.33;
      const boundary2 = req.body.boundary2 ? parseFloat(req.body.boundary2) : 66.66;

      // Run computer vision YOLO process
      let poolPoints = null;
      if (req.body.poolPoints) {
        try {
          poolPoints = JSON.parse(req.body.poolPoints);
        } catch (parseErr) {
          console.warn('⚠️ Failed to parse poolPoints from request body:', parseErr.message);
        }
      }
      const analysisResult = await runAIAnalysis(req.file.path, boundary1, boundary2, poolPoints);

      res.status(200).json(analysisResult);
    } catch (analysisError) {
      console.error(`❌ AI Analysis Failure: ${analysisError.message}`);
      res.status(500).json({ success: false, error: analysisError.message });
    }
  });
});

// Endpoint to analyze uploaded pool video
app.post('/api/analyze-video', (req, res) => {
  uploadVideo.single('video')(req, res, async (err) => {
    if (err) {
      console.error(`❌ Multer Video Upload Error: ${err.message}`);
      return res.status(400).json({ success: false, error: err.message });
    }

    if (!req.file) {
      return res.status(400).json({ success: false, error: 'No video file uploaded.' });
    }

    const jobId = `job-${Date.now()}-${Math.round(Math.random() * 1e5)}`;
    const boundary1 = req.body.boundary1 ? parseFloat(req.body.boundary1) : 33.33;
    const boundary2 = req.body.boundary2 ? parseFloat(req.body.boundary2) : 66.66;
    const filePath = req.file.path;

    let poolPoints = null;
    if (req.body.poolPoints) {
      try {
        poolPoints = JSON.parse(req.body.poolPoints);
      } catch (parseErr) {
        console.warn('⚠️ Failed to parse poolPoints from request body:', parseErr.message);
      }
    }

    // Create background job state
    const jobState = {
      jobId,
      status: 'PROCESSING',
      progress: 0,
      framesProcessed: 0,
      peopleDetected: 0,
      fileName: req.file.originalname,
      fileSize: req.file.size,
      result: null,
      error: null,
      createdAt: new Date(),
      process: null
    };

    jobs.set(jobId, jobState);

    // Spawn processing in background
    runAIAnalysis(
      filePath,
      boundary1,
      boundary2,
      poolPoints,
      (progressData) => {
        const job = jobs.get(jobId);
        if (job && job.status === 'PROCESSING') {
          job.progress = progressData.progress;
          job.framesProcessed = progressData.framesProcessed;
          job.peopleDetected = progressData.peopleDetected;
        }
      },
      (proc) => {
        const job = jobs.get(jobId);
        if (job) {
          job.process = proc;
        }
      }
    )
    .then((result) => {
      const job = jobs.get(jobId);
      if (job && job.status === 'PROCESSING') {
        job.status = 'COMPLETED';
        job.progress = 100;
        job.result = result;
        job.process = null;
      }
      
      // Clean up raw uploaded file
      fs.unlink(filePath, (unlinkErr) => {
        if (unlinkErr) console.error(`Error deleting raw uploaded file ${filePath}:`, unlinkErr);
      });
    })
    .catch((err) => {
      console.error(`❌ Background AI Analysis Failure for job ${jobId}: ${err.message}`);
      const job = jobs.get(jobId);
      if (job && job.status === 'PROCESSING') {
        job.status = 'FAILED';
        job.error = err.message;
        job.process = null;
      }
      
      // Clean up raw uploaded file
      fs.unlink(filePath, (unlinkErr) => {
        if (unlinkErr) console.error(`Error deleting raw uploaded file ${filePath}:`, unlinkErr);
      });
    });

    res.status(202).json({ success: true, jobId, status: 'PROCESSING' });
  });
});

// Endpoint to poll background job status
app.get('/api/jobs/:jobId', (req, res) => {
  const { jobId } = req.params;
  const job = jobs.get(jobId);
  if (!job) {
    return res.status(404).json({ success: false, error: 'Job not found.' });
  }
  
  // Exclude process reference from JSON response
  const { process, ...safeJob } = job;
  res.status(200).json(safeJob);
});

// Endpoint to cancel a background job
app.post('/api/jobs/:jobId/cancel', (req, res) => {
  const { jobId } = req.params;
  const job = jobs.get(jobId);
  if (!job) {
    return res.status(404).json({ success: false, error: 'Job not found.' });
  }

  if (job.status === 'PROCESSING') {
    if (job.process) {
      console.log(`Killing python process for job ${jobId}`);
      try {
        job.process.kill();
      } catch (killErr) {
        console.error(`Error killing python process: ${killErr.message}`);
      }
    }
    job.status = 'FAILED';
    job.error = 'Job cancelled by user.';
    job.process = null;
  }

  res.status(200).json({ success: true });
});

const PORT = process.env.PORT || 5000;

const startServer = async () => {
  // Connect to Database (handles offline scenario gracefully)
  await connectDB();
  
  const server = app.listen(PORT, () => {
    console.log(`🚀 Swimming Pool Safety AI Server listening on port ${PORT}`);
    console.log(`🔗 API Health: http://localhost:${PORT}/api/health`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.warn(`⚠️ Port ${PORT} is busy. Retrying in 1.5 seconds...`);
      setTimeout(() => {
        server.close();
        startServer();
      }, 1500);
    } else {
      console.error('❌ Server startup error:', err);
    }
  });
};

startServer();
