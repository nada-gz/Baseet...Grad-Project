import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../../../hooks/useAuth";
import api from "../../../services/api";
import { Users, BookOpen, ChartBar, Bell, MessageSquare, Clock } from "lucide-react"; // icons

export default function TeacherDashboard() {
  const { user, loading, error } = useAuth();
  const [messages, setMessages] = useState([]);
  const [msgLoading, setMsgLoading] = useState(true);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await api.get("/teacher/messages");
        setMessages(response.data);
      } catch (err) {
        console.error("Error fetching supervisor messages:", err);
      } finally {
        setMsgLoading(false);
      }
    };
    if (user && user.role === "teacher") {
      fetchMessages();
    }
  }, [user]);

  if (loading) return <div className="supervisor-dashboard-container"><p>Loading...</p></div>;
  if (error) return <div className="supervisor-dashboard-container"><p style={{ color: 'var(--error-bg)' }}>Error loading user.</p></div>;

  return (
    <div className="supervisor-dashboard-container">

      <div className="teacher-cards-row">

        {/* Lesson Preparation Card */}
        <div className="teacher-card">
          <div className="card-icon">
            <BookOpen className="h-12 w-12 text-primary" />
          </div>
          <div className="card-title text-primary">Prepare Lessons</div>
          <div className="card-description">
            Design courses, build structured milestones, and create detailed lessons with learning materials and exercises.
          </div>
          <div className="card-buttons">
            <Link to="/dashboard/teacher/lessons-prep" className="btn btn-primary">
              Go to Lesson Preparation
            </Link>
          </div>
        </div>

        {/* Class Management Card */}
        <div className="teacher-card">
          <div className="card-icon">
            <Users className="h-12 w-12 text-primary" />
          </div>
          <div className="card-title text-primary">Manage Your Class</div>
          <div className="card-description">
            Organize learning levels, create classes, assign students, and link relevant courses to each class.
          </div>
          <div className="card-buttons">
            <Link to="/dashboard/teacher/classrooms" className="btn btn-primary">
              Go to Class Management
            </Link>
          </div>
        </div>

        {/* Student Monitoring Card */}
        <div className="teacher-card">
          <div className="card-icon">
            <ChartBar className="h-12 w-12 text-primary" />
          </div>
          <div className="card-title text-primary">Monitor Students</div>
          <div className="card-description">
            View all students in one place, track their academic progress, and monitor their real-time psychological state through biometric sensors.
          </div>
          <div className="card-buttons">
            <Link to="/dashboard/teacher/students" className="btn btn-primary">
              Go to Student Monitoring
            </Link>
          </div>
        </div>

        
        

        

        
      </div>

      {/* Supervisor Messages Section */}
      <div style={{ marginTop: '60px' }}>
        <h2 className="supervisor-title" style={{ fontSize: '1.8rem', marginBottom: '30px' }}>
          Supervisor <span>Instructions</span>
        </h2>
        
        {msgLoading ? (
          <div style={{ padding: '60px', textAlign: 'center', border: '3px dashed var(--neutral)', borderRadius: '24px' }}>
            <p className="stat-label">Checking for messages...</p>
          </div>
        ) : messages.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '25px' }}>
            {messages.map((msg) => (
              <div key={msg.id} className="alert-item" style={{ background: 'white', border: '3px solid var(--neutral)', color: 'var(--primary-text)', padding: '25px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                  <div style={{ padding: '8px', background: 'var(--primary-bg)', borderRadius: '12px', color: 'var(--highlight)' }}>
                    <MessageSquare size={20} />
                  </div>
                  <span className="stat-label" style={{ fontSize: '9px' }}>
                    <Clock size={10} /> {new Date(msg.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p style={{ fontWeight: 700, lineHeight: '1.6', marginBottom: '15px', fontSize: '0.95rem' }}>
                  {msg.content}
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'var(--neutral)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '9px', fontWeight: 900 }}>
                    S
                  </div>
                  <span className="stat-label" style={{ fontSize: '9px' }}>Supervisor Note</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '60px', textAlign: 'center', border: '3px dashed var(--neutral)', borderRadius: '24px' }}>
            <MessageSquare style={{ opacity: 0.1, margin: '0 auto 15px' }} size={48} />
            <p className="stat-label">No messages from the supervisor yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
