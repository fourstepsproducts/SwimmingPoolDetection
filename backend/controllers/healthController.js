import mongoose from 'mongoose';

export const checkHealth = (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'Swimming Pool Safety AI API Server',
    timestamp: new Date().toISOString(),
    uptime: `${Math.round(process.uptime())}s`,
    database: mongoose.connection.readyState === 1 ? 'CONNECTED' : 'DISCONNECTED / RUNNING IN MOCK MODE',
    connections: req.io ? req.io.engine.clientsCount : 0
  });
};
