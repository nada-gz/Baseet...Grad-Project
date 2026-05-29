import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import useAuth from "../../../hooks/useAuth";
import api from "../../../services/api";
import { 
  User, Mail, Calendar, Activity, BrainCircuit, 
  Settings, BookOpen, Layers, ShieldAlert, ArrowLeft 
} from "lucide-react";

export default function StudentProfile() {
  const { studentId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get(`/students/${studentId}/profile`);
        setProfile(response.data);
      } catch (err) {
        console.error("Error fetching profile:", err);
        setError("Failed to load student profile. They might not exist or you lack permission.");
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [studentId]);

  if (loading) {
    return (
      <div className="supervisor-dashboard-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="status-checking">Loading Student Profile...</div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="supervisor-dashboard-container">
        <button onClick={() => navigate(-1)} className="back-btn" style={{ marginBottom: '20px' }}>
          <ArrowLeft size={16} /> Back
        </button>
        <div style={{ background: 'var(--error-bg)', color: 'white', padding: '20px', borderRadius: '15px', display: 'flex', alignItems: 'center', gap: '15px' }}>
          <ShieldAlert size={24} />
          <h3 style={{ margin: 0 }}>{error || "Profile not found"}</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="supervisor-dashboard-container student-profile-container">
      {/* Navigation */}
      <button onClick={() => navigate(-1)} className="back-btn">
        <ArrowLeft size={16} /> Back to Directory
      </button>

      {/* Header Profile Card */}
      <div className="profile-header-card">
        <div className="profile-header-content">
          <div className="profile-avatar-large">
            {profile.username.charAt(0).toUpperCase()}
          </div>
          <div className="profile-titles">
            <div className="profile-title-wrapper">
              <h1 className="profile-name">{profile.username}</h1>
              {profile.is_flagged && (
                <span className="flag-badge-pulse flag-badge">
                  <ShieldAlert size={14} /> FLAGGED
                </span>
              )}
            </div>
            <p className="profile-status">
              <span className={`indicator-dot ${profile.online ? "online" : "offline"}`}></span>
              {profile.online ? "Currently Online" : "Offline"}
            </p>
          </div>
        </div>
      </div>

      {/* Grid Layout for details */}
      <div className="profile-details-grid">
        
        {/* Contact & Basics */}
        <div className="profile-info-card">
          <h2 className="supervisor-card-title"><User size={20} /> Personal Information</h2>
          <div className="info-list">
            <div className="info-item">
              <Mail className="info-icon" size={18} />
              <div>
                <span className="info-label">Email Address</span>
                <span className="info-value">{profile.email}</span>
              </div>
            </div>
            <div className="info-item">
              <Calendar className="info-icon" size={18} />
              <div>
                <span className="info-label">Age</span>
                <span className="info-value">{profile.age || "Not specified"} years old</span>
              </div>
            </div>
            <div className="info-item">
              <Activity className="info-icon" size={18} />
              <div>
                <span className="info-label">System Role</span>
                <span className="info-value" style={{ textTransform: 'capitalize' }}>{profile.role}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Learning Profile */}
        <div className="profile-info-card learning-profile-card">
          <h2 className="supervisor-card-title learning-title"><BrainCircuit size={20} /> Learning Profile</h2>
          <div className="info-list">
            <div className="info-item">
              <Settings className="info-icon" size={18} />
              <div>
                <span className="info-label">Learning Style</span>
                <span className="info-value">{profile.learning_style || "Default / Unassessed"}</span>
              </div>
            </div>
            <div className="info-item">
              <Activity className="info-icon" size={18} />
              <div>
                <span className="info-label">Autism Type / Needs</span>
                <span className="info-value">{profile.autism_type || "None recorded"}</span>
              </div>
            </div>
            <div className="info-item">
              <Layers className="info-icon" size={18} />
              <div>
                <span className="info-label">Sensory Profile</span>
                <span className="info-value">{profile.sensitivities || "No special sensitivities"}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Academic Placement */}
        <div className="profile-info-card">
          <h2 className="supervisor-card-title"><BookOpen size={20} /> Academic Placement</h2>
          <div className="info-list">
            <div className="info-item">
              <Layers className="info-icon" size={18} />
              <div>
                <span className="info-label">Class Level</span>
                <span className="info-value">{profile.level_name || "Unassigned"}</span>
              </div>
            </div>
            <div className="info-item">
              <BookOpen className="info-icon" size={18} />
              <div>
                <span className="info-label">Classroom</span>
                <span className="info-value">{profile.classroom_name || "Unassigned"}</span>
              </div>
            </div>
            <div className="progress-btn-wrapper">
              <button onClick={() => navigate(`/students/${studentId}/insights`)} className="btn btn-outline progress-btn">
                View Full Academic Progress
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
