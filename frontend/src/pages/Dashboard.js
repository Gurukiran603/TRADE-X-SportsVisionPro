import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Upload, 
  Video, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Trophy,
  Activity,
  TrendingUp,
  Users,
  Play
} from 'lucide-react';
import { videoAPI } from '../services/api';
import toast from 'react-hot-toast';
import './Dashboard.css';

function Dashboard() {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    processing: 0,
    failed: 0
  });

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await videoAPI.getAll();
      const videoData = response.data;
      setVideos(videoData);
      
      // Calculate stats
      const stats = {
        total: videoData.length,
        completed: videoData.filter(v => v.status === 'completed').length,
        processing: videoData.filter(v => v.status === 'processing').length,
        failed: videoData.filter(v => v.status === 'failed').length
      };
      setStats(stats);
    } catch (error) {
      toast.error('Failed to fetch videos');
      console.error('Error fetching videos:', error);
    } finally {
      setLoading(false);
    }
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
        return 'Completed';
      case 'processing':
        return 'Processing';
      case 'failed':
        return 'Failed';
      default:
        return 'Processing';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading your videos...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <motion.div
        className="dashboard-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="header-content">
          <h1 className="dashboard-title">
            <img src="/logo.png" alt="SportsVision Pro" className="title-logo" />
            Welcome to SportsVision Pro
          </h1>
          <p className="dashboard-subtitle">
            AI-powered sports video analysis and player tracking
          </p>
        </div>
        <Link to="/upload" className="upload-button">
          <Upload size={20} />
          Upload Video
        </Link>
      </motion.div>

      <motion.div
        className="stats-grid"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="stat-card">
          <div className="stat-icon total">
            <Video size={24} />
          </div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.total}</h3>
            <p className="stat-label">Total Videos</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon completed">
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.completed}</h3>
            <p className="stat-label">Completed</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon processing">
            <Clock size={24} />
          </div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.processing}</h3>
            <p className="stat-label">Processing</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon failed">
            <XCircle size={24} />
          </div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.failed}</h3>
            <p className="stat-label">Failed</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="videos-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="section-header">
          <h2 className="section-title">
            <Activity size={24} />
            Recent Videos
          </h2>
          {videos.length > 0 && (
            <Link to="/upload" className="view-all-link">
              Upload More
            </Link>
          )}
        </div>

        {videos.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <Video size={48} />
            </div>
            <h3>No videos yet</h3>
            <p>Upload your first sports video to get started with AI analysis</p>
            <Link to="/upload" className="empty-upload-button">
              <Upload size={20} />
              Upload Video
            </Link>
          </div>
        ) : (
          <div className="videos-grid">
            {videos.map((video, index) => (
              <motion.div
                key={video.id}
                className="video-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <div className="video-thumbnail">
                  <div className="video-overlay">
                    {video.status === 'completed' ? (
                      <Link to={`/results/${video.id}`} className="play-button">
                        <Play size={32} />
                      </Link>
                    ) : (
                      <div className="processing-overlay">
                        <div className="spinner"></div>
                        <span>Processing...</span>
                      </div>
                    )}
                  </div>
                  <div className="video-status">
                    {getStatusIcon(video.status)}
                    <span>{getStatusText(video.status)}</span>
                  </div>
                </div>
                
                <div className="video-info">
                  <h3 className="video-title">{video.original_filename}</h3>
                  <p className="video-date">{formatDate(video.created_at)}</p>
                  {video.processing_time && (
                    <p className="video-duration">
                      Processed in {video.processing_time}s
                    </p>
                  )}
                </div>

                {video.status === 'completed' && (
                  <Link to={`/results/${video.id}`} className="view-results-button">
                    View Results
                  </Link>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default Dashboard;
