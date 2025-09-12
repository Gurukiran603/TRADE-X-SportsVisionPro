import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { 
  Upload, 
  Video, 
  FileVideo, 
  CheckCircle, 
  AlertCircle,
  X,
  Play,
  Clock
} from 'lucide-react';
import { videoAPI } from '../services/api';
import toast from 'react-hot-toast';
import './VideoUpload.css';

function VideoUpload() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedVideo, setUploadedVideo] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('video/')) {
        toast.error('Please select a video file');
        return;
      }
      
      // Validate file size (max 100MB)
      const maxSize = 100 * 1024 * 1024; // 100MB
      if (file.size > maxSize) {
        toast.error('File size must be less than 100MB');
        return;
      }
      
      setUploadedFile(file);
      setUploadedVideo(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!uploadedFile) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await videoAPI.upload(formData);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setUploadedVideo(response.data);
      setUploadedFile(null);
      
      toast.success('Video uploaded successfully! Processing will begin shortly.');
      
      // Reset after 2 seconds
      setTimeout(() => {
        setUploadProgress(0);
        setUploadedVideo(null);
      }, 2000);
      
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setUploadedVideo(null);
    setUploadProgress(0);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-upload">
      <motion.div
        className="upload-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="upload-title">
          <img src="/logo.png" alt="SportsVision Pro" className="upload-logo" />
          Upload Sports Video
        </h1>
        <p className="upload-subtitle">
          Upload your sports video for AI-powered player and ball tracking analysis
        </p>
      </motion.div>

      <div className="upload-container">
        <motion.div
          className="upload-area"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {!uploadedFile && !uploadedVideo && (
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <div className="dropzone-content">
                <div className="dropzone-icon">
                  <Upload size={48} />
                </div>
                <h3 className="dropzone-title">
                  {isDragActive ? 'Drop your video here' : 'Drag & drop your video here'}
                </h3>
                <p className="dropzone-subtitle">
                  or click to browse files
                </p>
                <div className="supported-formats">
                  <span>Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM</span>
                  <span>Max file size: 100MB</span>
                </div>
              </div>
            </div>
          )}

          {uploadedFile && !uploadedVideo && (
            <div className="file-preview">
              <div className="file-info">
                <div className="file-icon">
                  <FileVideo size={32} />
                </div>
                <div className="file-details">
                  <h3 className="file-name">{uploadedFile.name}</h3>
                  <p className="file-size">{formatFileSize(uploadedFile.size)}</p>
                  <p className="file-type">{uploadedFile.type}</p>
                </div>
                <button className="remove-file" onClick={removeFile}>
                  <X size={20} />
                </button>
              </div>
              
              <div className="upload-actions">
                <button
                  className="upload-button"
                  onClick={handleUpload}
                  disabled={uploading}
                >
                  {uploading ? (
                    <>
                      <div className="spinner"></div>
                      Uploading... {uploadProgress}%
                    </>
                  ) : (
                    <>
                      <Upload size={20} />
                      Upload Video
                    </>
                  )}
                </button>
              </div>

              {uploading && (
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <p className="progress-text">
                    Uploading your video... {uploadProgress}%
                  </p>
                </div>
              )}
            </div>
          )}

          {uploadedVideo && (
            <div className="upload-success">
              <div className="success-icon">
                <CheckCircle size={48} />
              </div>
              <h3 className="success-title">Upload Successful!</h3>
              <p className="success-message">
                Your video has been uploaded and is now being processed.
                You'll be notified when the analysis is complete.
              </p>
              <div className="video-info">
                <div className="info-item">
                  <span className="info-label">File:</span>
                  <span className="info-value">{uploadedVideo.original_filename}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Status:</span>
                  <span className="info-value status-processing">
                    <Clock size={16} />
                    Processing
                  </span>
                </div>
              </div>
              <button className="upload-another" onClick={removeFile}>
                Upload Another Video
              </button>
            </div>
          )}
        </motion.div>

        <motion.div
          className="upload-info"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h3 className="info-title">What happens next?</h3>
          <div className="info-steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Upload</h4>
                <p>Your video is securely uploaded to our servers</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>Analysis</h4>
                <p>AI processes your video to detect players and track the ball</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Results</h4>
                <p>View the analyzed video with tracking overlays and statistics</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default VideoUpload;
