import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import { 
  User, 
  Mail, 
  Phone, 
  Calendar, 
  Edit3, 
  Save, 
  X,
  Trophy,
  Video,
  Activity,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import './Profile.css';

function Profile() {
  const { user, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    phone: user?.phone || ''
  });

  const handleEdit = () => {
    setIsEditing(true);
    setEditData({
      full_name: user?.full_name || '',
      email: user?.email || '',
      phone: user?.phone || ''
    });
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditData({
      full_name: user?.full_name || '',
      email: user?.email || '',
      phone: user?.phone || ''
    });
  };

  const handleSave = async () => {
    // In a real app, you would make an API call to update the user
    toast.success('Profile updated successfully!');
    setIsEditing(false);
  };

  const handleChange = (e) => {
    setEditData({
      ...editData,
      [e.target.name]: e.target.value
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="profile">
      <motion.div
        className="profile-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="profile-title">
          <img src="/logo.png" alt="SportsVision Pro" className="profile-logo" />
          Profile Settings
        </h1>
        <p className="profile-subtitle">
          Manage your account information and preferences
        </p>
      </motion.div>

      <div className="profile-content">
        <motion.div
          className="profile-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="card-header">
            <h2 className="card-title">Personal Information</h2>
            {!isEditing ? (
              <button className="edit-button" onClick={handleEdit}>
                <Edit3 size={18} />
                Edit Profile
              </button>
            ) : (
              <div className="edit-actions">
                <button className="save-button" onClick={handleSave}>
                  <Save size={18} />
                  Save
                </button>
                <button className="cancel-button" onClick={handleCancel}>
                  <X size={18} />
                  Cancel
                </button>
              </div>
            )}
          </div>

          <div className="profile-info">
            <div className="info-section">
              <label className="info-label">
                <User size={18} />
                Full Name
              </label>
              {isEditing ? (
                <input
                  type="text"
                  name="full_name"
                  value={editData.full_name}
                  onChange={handleChange}
                  className="info-input"
                />
              ) : (
                <span className="info-value">{user?.full_name}</span>
              )}
            </div>

            <div className="info-section">
              <label className="info-label">
                <Mail size={18} />
                Email Address
              </label>
              {isEditing ? (
                <input
                  type="email"
                  name="email"
                  value={editData.email}
                  onChange={handleChange}
                  className="info-input"
                />
              ) : (
                <span className="info-value">{user?.email}</span>
              )}
            </div>

            <div className="info-section">
              <label className="info-label">
                <Phone size={18} />
                Phone Number
              </label>
              {isEditing ? (
                <input
                  type="tel"
                  name="phone"
                  value={editData.phone}
                  onChange={handleChange}
                  className="info-input"
                />
              ) : (
                <span className="info-value">{user?.phone}</span>
              )}
            </div>

            <div className="info-section">
              <label className="info-label">
                <Calendar size={18} />
                Member Since
              </label>
              <span className="info-value">{formatDate(user?.created_at)}</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="stats-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h2 className="card-title">Account Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-icon">
                <Video size={24} />
              </div>
              <div className="stat-content">
                <h3 className="stat-number">12</h3>
                <p className="stat-label">Videos Analyzed</p>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">
                <Activity size={24} />
              </div>
              <div className="stat-content">
                <h3 className="stat-number">8.5</h3>
                <p className="stat-label">Avg Processing Time (min)</p>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">
                <CheckCircle size={24} />
              </div>
              <div className="stat-content">
                <h3 className="stat-number">95%</h3>
                <p className="stat-label">Success Rate</p>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">
                <Trophy size={24} />
              </div>
              <div className="stat-content">
                <h3 className="stat-number">3</h3>
                <p className="stat-label">Analysis Features</p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="preferences-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <h2 className="card-title">Preferences</h2>
          <div className="preferences-list">
            <div className="preference-item">
              <div className="preference-info">
                <h4>Email Notifications</h4>
                <p>Receive updates about video processing status</p>
              </div>
              <label className="toggle-switch">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="preference-item">
              <div className="preference-info">
                <h4>Auto-download Results</h4>
                <p>Automatically download processed videos</p>
              </div>
              <label className="toggle-switch">
                <input type="checkbox" />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="preference-item">
              <div className="preference-info">
                <h4>High Quality Processing</h4>
                <p>Use higher quality settings for analysis</p>
              </div>
              <label className="toggle-switch">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="danger-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <h2 className="card-title">Danger Zone</h2>
          <div className="danger-content">
            <div className="danger-info">
              <h4>Sign Out</h4>
              <p>Sign out of your account on this device</p>
            </div>
            <button className="danger-button" onClick={logout}>
              Sign Out
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default Profile;
