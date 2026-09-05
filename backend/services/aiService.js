import { spawn } from 'child_process';
import path from 'path';

/**
 * Spawns the Python YOLOv8 analysis process for a given image or video path.
 * @param {string} mediaPath Absolute or relative path to the image or video
 * @param {number} boundary1 Floating percentage marking Shallow-to-Medium boundary
 * @param {number} boundary2 Floating percentage marking Medium-to-Deep boundary
 * @param {object} poolPoints Configurable calibration corner points
 * @param {function} onProgress Callback function invoked on progress updates: (data) => {}
 * @param {function} onSpawn Callback function invoked when the process is spawned: (proc) => {}
 * @returns {Promise<object>} Parsed AI detection results
 */
export const runAIAnalysis = (mediaPath, boundary1 = 33.33, boundary2 = 66.66, poolPoints = null, onProgress = null, onSpawn = null) => {
  return new Promise((resolve, reject) => {
    // Relative path to script from backend/ folder
    const scriptPath = path.resolve('services/analyze.py');
    const pythonExecutable = process.env.PYTHON_PATH || 'python';

    console.log(`📡 Starting AI analysis on media: ${mediaPath}`);
    console.log(`🐍 Using Python executable: ${pythonExecutable}`);

    // Spawn Python in unbuffered (-u) mode using the project environment that has OpenCV and Ultralytics installed.
    const pythonProcess = spawn(pythonExecutable, [
      '-u',
      scriptPath,
      mediaPath,
      boundary1.toString(),
      boundary2.toString(),
      poolPoints ? JSON.stringify(poolPoints) : ''
    ]);
    
    if (onSpawn) {
      onSpawn(pythonProcess);
    }
    
    let stdoutAccumulator = '';
    let stderrAccumulator = '';
    let lineBuffer = '';
    
    pythonProcess.stdout.on('data', (chunk) => {
      lineBuffer += chunk.toString();
      const lines = lineBuffer.split('\n');
      lineBuffer = lines.pop(); // keep the last partial line
      
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('PROGRESS:')) {
          try {
            const dataStr = trimmed.substring('PROGRESS:'.length).trim();
            const progressData = JSON.parse(dataStr);
            if (onProgress) {
              onProgress(progressData);
            }
          } catch (e) {
            console.error(`⚠️ Error parsing progress line: ${trimmed}. Error: ${e.message}`);
          }
        } else {
          // Accumulate line for final result parsing (which could be prefixed with RESULT:)
          stdoutAccumulator += line + '\n';
        }
      }
    });
    
    pythonProcess.stderr.on('data', (chunk) => {
      stderrAccumulator += chunk.toString();
    });
    
    pythonProcess.on('close', (exitCode) => {
      // Append any remaining data in the lineBuffer
      if (lineBuffer.trim()) {
        stdoutAccumulator += lineBuffer + '\n';
      }

      if (exitCode !== 0 && exitCode !== null) {
        // Node.js process.kill() may result in exit code null, which is not an error if cancelled
        console.error(`❌ Python script exited with code ${exitCode}. Stderr: ${stderrAccumulator}`);
        return reject(new Error(`AI Analysis failed with exit code ${exitCode}: ${stderrAccumulator || 'Unknown error'}`));
      }
      
      try {
        let jsonStr = stdoutAccumulator.trim();
        const lines = stdoutAccumulator.split('\n');
        
        // Find line starting with RESULT:
        const resultLine = lines.reverse().find(l => l.trim().startsWith('RESULT:'));
        if (resultLine) {
          jsonStr = resultLine.trim().substring('RESULT:'.length).trim();
        } else {
          // Fallback: look for the first JSON-like line
          const fallbackLine = lines.find(l => l.trim().startsWith('{'));
          if (fallbackLine) {
            jsonStr = fallbackLine.trim();
          }
        }

        const parsed = JSON.parse(jsonStr);
        if (!parsed.success) {
          return reject(new Error(parsed.error || 'AI detection script reported failure.'));
        }
        console.log(`❇️ AI analysis completed. Occupancy: ${parsed.occupancy}`);
        resolve(parsed);
      } catch (err) {
        console.error(`❌ Failed to parse Python stdout: ${stdoutAccumulator}`);
        reject(new Error(`Failed to parse AI output JSON: ${err.message}`));
      }
    });
    
    pythonProcess.on('error', (err) => {
      console.error(`❌ Failed to spawn Python process: ${err.message}`);
      reject(new Error(`Spawn Error: Ensure Python is in your PATH. Details: ${err.message}`));
    });
  });
};

