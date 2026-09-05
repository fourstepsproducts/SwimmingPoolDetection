import mongoose from 'mongoose';
import dotenv from 'dotenv';

dotenv.config();

const connectDB = async () => {
  const mongoURI = process.env.MONGODB_URI;
  
  if (!mongoURI) {
    console.warn('\x1b[33m%s\x1b[0m', '⚠️ WARNING: MONGODB_URI is not defined in .env. App will run in mock mode without database saving.');
    return false;
  }

  try {
    const conn = await mongoose.connect(mongoURI, {
      serverSelectionTimeoutMS: 3000 // fail fast if db is not up
    });
    console.log(`\x1b[32m%s\x1b[0m`, `❇️ MongoDB Database Connected: ${conn.connection.host}`);
    return true;
  } catch (error) {
    console.error(`\x1b[31m%s\x1b[0m`, `❌ MongoDB Connection Failed: ${error.message}`);
    console.warn('\x1b[33m%s\x1b[0m', '⚠️ WARNING: Proceeding without MongoDB. System status remains healthy.');
    return false;
  }
};

export default connectDB;
