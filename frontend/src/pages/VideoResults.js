import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Play, 
  Pause, 
  Download, 
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  Activity,
  Users,
  Target
} from 'lucide-react';
import ReactPlayer from 'react-player';
import { videoAPI } from '../services/api';
import toast from 'react-hot-toast';
import './VideoResults.css';

function VideoResults() {
  const { videoId } = useParams();
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    fetchVideo();
  }, [videoId]);

  const fetchVideo = async () => {
    try {
      const response = await videoAPI.getById(videoId);
      setVideo(response.data);
    } catch (error) {
      toast.error('Failed to fetch video details');
      console.error('Error fetching video:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPause = () => {
    setPlaying(!playing);
  };

  const handleProgress = (state) => {
    setProgress(state.played);
  };

  const handleDuration = (duration) => {
    setDuration(duration);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="status-icon completed" />;
      case 'processing':
        return <Clock className="status-icon processing" />;
      case 'failed':
        return <XCircle className="status-icon failed" />;
      default:
        return <Clock className="status-icon processing" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Analysis Complete';
      case 'processing':
        return 'Processing...';
      case 'failed':
        return 'Processing Failed';
      default:
        return 'Processing...';
    }
  };

  const handleDownload = () => {
    if (video?.processed_filename) {
      const link = document.createElement('a');
      link.href = `http://localhost:8000/processed/${video.processed_filename}`;
      link.download = `analyzed_${video.original_filename}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  if (loading) {
    return (
      <div className="video-results-loading">
        <div className="spinner"></div>
        <p>Loading video details...</p>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="video-results-error">
        <XCircle size={48} />
        <h3>Video not found</h3>
        <p>The video you're looking for doesn't exist or has been removed.</p>
        <Link to="/" className="back-button">
          <ArrowLeft size={20} />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="video-results">
      <motion.div
        className="results-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Link to="/" className="back-button">
          <ArrowLeft size={20} />
          Back to Dashboard
        </Link>
        
        <div className="video-title-section">
          <h1 className="video-title">{video.original_filename}</h1>
          <div className="video-status">
            {getStatusIcon(video.status)}
            <span>{getStatusText(video.status)}</span>
          </div>
        </div>
      </motion.div>

      <div className="results-content">
        <motion.div
          className="video-player-section"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="video-container">
            {video.status === 'completed' ? (
              <ReactPlayer
                url={`http://localhost:8000/processed/${video.processed_filename}`}
                width="100%"
                height="100%"
                playing={playing}
                onProgress={handleProgress}
                onDuration={handleDuration}
                controls={false}
                config={{
                  file: {
                    attributes: {
                      controlsList: 'nodownload'
                    }
                  }
                }}
              />
            ) : video.status === 'processing' ? (
              <div className="processing-overlay">
                <div className="processing-content">
                  <RefreshCw className="processing-icon" />
                  <h3>Processing Video</h3>
                  <p>AI is analyzing your video for player and ball tracking...</p>
                  <div className="processing-stats">
                    <div className="stat">
                      <Activity size={20} />
                      <span>Detecting players</span>
                    </div>
                    <div className="stat">
                      <Target size={20} />
                      <span>Tracking ball movement</span>
                    </div>
                    <div className="stat">
                      <Users size={20} />
                      <span>Generating trajectories</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="error-overlay">
                <XCircle size={48} />
                <h3>Processing Failed</h3>
                <p>There was an error processing your video. Please try uploading again.</p>
              </div>
            )}

            {video.status === 'completed' && (
              <div className="video-controls">
                <button className="control-button" onClick={handlePlayPause}>
                  {playing ? <Pause size={20} /> : <Play size={20} />}
                </button>
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${progress * 100}%` }}
                    ></div>
                  </div>
                  <div className="time-display">
                    <span>{formatTime(progress * duration)}</span>
                    <span>{formatTime(duration)}</span>
                  </div>
                </div>
                <button className="control-button" onClick={handleDownload}>
                  <Download size={20} />
                </button>
              </div>
            )}
          </div>
        </motion.div>

        <motion.div
          className="video-info-section"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="info-card">
            <h3 className="info-title">Video Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Original File:</span>
                <span className="info-value">{video.original_filename}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Upload Date:</span>
                <span className="info-value">
                  {new Date(video.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
              {video.processing_time && (
                <div className="info-item">
                  <span className="info-label">Processing Time:</span>
                  <span className="info-value">{video.processing_time} seconds</span>
                </div>
              )}
              <div className="info-item">
                <span className="info-label">Status:</span>
                <span className={`info-value status-${video.status}`}>
                  {getStatusText(video.status)}
                </span>
              </div>
            </div>
          </div>

          {video.status === 'completed' && (
            <div className="analysis-card">
              <h3 className="info-title">Analysis Features</h3>
              <div className="features-list">
                <div className="feature-item">
                  <Users size={20} />
                  <div>
                    <h4>Player Detection</h4>
                    <p>AI identifies and tracks all players in the video</p>
                  </div>
                </div>
                <div className="feature-item">
                  <Target size={20} />
                  <div>
                    <h4>Ball Tracking</h4>
                    <p>Precise ball movement tracking with trajectory prediction</p>
                  </div>
                </div>
                <div className="feature-item">
                  <Activity size={20} />
                  <div>
                    <h4>Movement Analysis</h4>
                    <p>Velocity and movement pattern analysis</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {video.status === 'processing' && (
            <div className="processing-card">
              <h3 className="info-title">Processing Status</h3>
              <div className="processing-steps">
                <div className="step active">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h4>Video Upload</h4>
                    <p>Video successfully uploaded</p>
                  </div>
                </div>
                <div className="step active">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h4>AI Analysis</h4>
                    <p>Processing in progress...</p>
                  </div>
                </div>
                <div className="step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h4>Results Ready</h4>
                    <p>Analysis will be available shortly</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

export default VideoResults;
