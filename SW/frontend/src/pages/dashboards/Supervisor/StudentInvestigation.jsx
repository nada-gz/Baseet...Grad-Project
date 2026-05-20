import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  ShieldAlert, 
  Activity, 
  MessageSquare, 
  FileText,
  Download,
  CheckCircle2,
  AlertTriangle,
  History
} from "lucide-react";
import api from "../../../services/api";

export default function StudentInvestigation() {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState("");
  const [reportTitle, setReportTitle] = useState("Academic & Behavioral Investigation");
  const [isResolving, setIsResolving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showMsgModal, setShowMsgModal] = useState(false);
  const [msgContent, setMsgContent] = useState("");
  const [isSendingMsg, setIsSendingMsg] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [studentRes, flagsRes] = await Promise.all([
          api.get(`/supervisor/students/all`),
          api.get(`/supervisor/students/flagged`)
        ]);
        
        const currentStudent = studentRes.data.find(s => s.id === parseInt(studentId));
        setStudent(currentStudent);
        setFlags(flagsRes.data.filter(f => f.student_id === parseInt(studentId)));
      } catch (err) {
        console.error("Error fetching investigation data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [studentId]);

  const handleResolve = async () => {
    setIsResolving(true);
    try {
      const latestFlag = flags[0];
      if (latestFlag) {
        await api.post(`/supervisor/flags/${latestFlag.id}/resolve`, {
          notes: notes,
          status: "resolved"
        });
      }
      
      await api.post("/supervisor/reports", {
        student_id: parseInt(studentId),
        title: reportTitle,
        content: notes
      });

      setSuccess(true);
      setTimeout(() => navigate("/dashboard/supervisor"), 2000);
    } catch (err) {
      console.error("Error resolving flag:", err);
    } finally {
      setIsResolving(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleSendMessage = async () => {
    if (!msgContent || isSendingMsg) return;
    setIsSendingMsg(true);
    try {
      const teacherRes = await api.get(`/supervisor/teachers`);
      const assignedTeacher = teacherRes.data.find(t => t.id === student?.teacher_id) || teacherRes.data[0];
      
      if (!assignedTeacher) {
        alert("No teacher assigned to this student.");
        return;
      }

      await api.post("/supervisor/messages", {
        teacher_id: assignedTeacher.id,
        student_id: parseInt(studentId),
        content: msgContent
      });

      alert("Message sent successfully to " + assignedTeacher.username);
      setShowMsgModal(false);
      setMsgContent("");
    } catch (err) {
      console.error("Error sending message:", err);
      alert("Failed to send message.");
    } finally {
      setIsSendingMsg(false);
    }
  };

  if (loading) {
    return (
      <div className="supervisor-dashboard-container">
        <div className="status-checking">Gathering Evidence...</div>
      </div>
    );
  }

  return (
    <div className="supervisor-dashboard-container" style={{ maxWidth: '1200px' }}>
      <header className="supervisor-header" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
        <button 
          onClick={() => navigate(-1)}
          className="back-btn"
        >
          <ArrowLeft size={16} /> Back
        </button>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div className="student-initials-box" style={{ width: '70px', height: '70px', fontSize: '1.8rem' }}>
              {student?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="supervisor-title" style={{ fontSize: '2rem' }}>Case Investigation: <span>{student?.username}</span></h1>
              <p className="stat-label" style={{ textTransform: 'none', marginTop: '5px' }}>Investigating urgent triggers and behavioral alerts.</p>
            </div>
          </div>
          <div className="online-indicator" style={{ background: 'var(--error-bg)', color: 'white', padding: '8px 20px', borderRadius: '30px' }}>
            <AlertTriangle size={14} /> ACTIVE CASE
          </div>
        </div>
      </header>

      <div className="supervisor-layout-grid">
        {/* Left Column: Alerts History */}
        <div className="investigation-sidebar">
          <section className="supervisor-card">
            <h2 className="supervisor-card-title" style={{ fontSize: '1.1rem', marginBottom: '30px' }}>
              <History size={20} /> Alert Timeline
            </h2>
            <div className="timeline-wrapper">
              {flags.map((flag, idx) => (
                <div key={flag.id} className={`timeline-item ${idx === 0 ? 'active' : ''}`}>
                  <div className="timeline-dot"></div>
                  <div>
                    <span className="stat-label" style={{ fontSize: '9px' }}>
                      {new Date(flag.created_at).toLocaleString()}
                    </span>
                    <h4 style={{ margin: '5px 0', fontSize: '0.9rem', fontWeight: 800, textTransform: 'capitalize' }}>{flag.source} Flag</h4>
                    <p className="stat-label" style={{ textTransform: 'none', fontSize: '0.8rem', lineHeight: '1.4' }}>{flag.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="supervisor-alert-sidebar" style={{ background: '#1E293B' }}>
            <h3 className="supervisor-card-title" style={{ color: 'white', fontSize: '1rem', marginBottom: '20px' }}>
              <Activity size={18} /> IoT Context
            </h3>
            <p className="stat-label" style={{ color: 'rgba(255,255,255,0.6)', textTransform: 'none', marginBottom: '20px' }}>
              Biometric peaks detected 5 minutes prior to flag.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '15px' }}>
                <span className="stat-label" style={{ fontSize: '8px', color: 'rgba(255,255,255,0.4)' }}>Heart Rate</span>
                <span className="stat-value" style={{ color: 'white', fontSize: '1.2rem', display: 'block' }}>115 <span style={{ fontSize: '10px' }}>BPM</span></span>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '15px' }}>
                <span className="stat-label" style={{ fontSize: '8px', color: 'rgba(255,255,255,0.4)' }}>GSR Peak</span>
                <span className="stat-value" style={{ color: 'white', fontSize: '1.2rem', display: 'block' }}>4.2 <span style={{ fontSize: '10px' }}>μS</span></span>
              </div>
            </div>
          </section>
        </div>

        {/* Right Column: Decision & Report */}
        <div className="investigation-main">
          <section className="supervisor-card">
            <div className="supervisor-card-header">
              <h2 className="supervisor-card-title">
                <FileText size={24} /> Decision & Report
              </h2>
            </div>
            
            <div style={{ marginTop: '30px' }}>
              <div className="investigation-form-group">
                <label className="investigation-label">Report Title</label>
                <input 
                  type="text" 
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                  className="investigation-input"
                />
              </div>
              <div className="investigation-form-group">
                <label className="investigation-label">Investigation Notes</label>
                <textarea 
                  rows={8}
                  placeholder="Describe your findings and the cause of the flag..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="investigation-textarea"
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '20px', marginTop: '30px' }}>
              <button 
                onClick={handleResolve}
                disabled={isResolving || !notes || success}
                className="alert-btn"
                style={{ flex: 2, background: 'var(--highlight)', color: 'white', marginTop: 0, padding: '18px' }}
              >
                {success ? (
                  <CheckCircle2 size={20} />
                ) : isResolving ? (
                  "Processing..."
                ) : (
                  "SUBMIT & CLOSE CASE"
                )}
              </button>
              <button 
                onClick={handlePrint}
                className="alert-btn"
                style={{ flex: 1, background: 'var(--secondary-bg)', color: 'var(--primary-text)', marginTop: 0, padding: '18px' }}
              >
                <Download size={20} /> PDF
              </button>
            </div>
          </section>

          <section className="supervisor-card" style={{ background: 'var(--primary-bg)', borderColor: 'var(--highlight)', borderStyle: 'dashed' }}>
            <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
              <div className="link-card-icon-box" style={{ background: 'white' }}>
                <MessageSquare size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: 0, fontWeight: 800 }}>Message Teacher</h3>
                <p className="stat-label" style={{ textTransform: 'none', marginTop: '2px' }}>Send direct instructions to the assigned teacher.</p>
              </div>
              <button 
                onClick={() => setShowMsgModal(true)}
                className="alert-btn"
                style={{ width: 'auto', background: 'white', marginTop: 0, padding: '10px 25px' }}
              >
                MESSAGE
              </button>
            </div>
          </section>
        </div>
      </div>

      {/* Message Modal */}
      {showMsgModal && (
        <div className="modal-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(8px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifycenter: 'center', padding: '20px' }}>
          <div className="supervisor-card" style={{ maxWidth: '600px', width: '100%', margin: '0 auto' }}>
            <h2 className="supervisor-title" style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Direct <span>Message</span></h2>
            <p className="stat-label" style={{ textTransform: 'none', marginBottom: '30px' }}>Discuss {student?.username}'s status with their teacher.</p>
            
            <div className="investigation-form-group">
              <textarea 
                rows={6}
                placeholder="Type your instructions here..."
                value={msgContent}
                onChange={(e) => setMsgContent(e.target.value)}
                className="investigation-textarea"
                style={{ background: 'var(--secondary-bg)' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '15px', marginTop: '30px' }}>
              <button 
                onClick={() => setShowMsgModal(false)}
                className="alert-btn"
                style={{ flex: 1, background: 'var(--secondary-bg)', marginTop: 0 }}
              >
                CANCEL
              </button>
              <button 
                onClick={handleSendMessage}
                disabled={!msgContent || isSendingMsg}
                className="alert-btn"
                style={{ flex: 1, background: 'var(--highlight)', color: 'white', marginTop: 0 }}
              >
                {isSendingMsg ? "SENDING..." : "SEND"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Print Styles */}
      <style>{`
        @media print {
          .supervisor-dashboard-container header, 
          .supervisor-dashboard-container .investigation-sidebar,
          .supervisor-dashboard-container .alert-btn,
          .supervisor-dashboard-container .supervisor-card:last-child {
            display: none !important;
          }
          .supervisor-dashboard-container {
            padding: 0 !important;
            max-width: 100% !important;
          }
          .investigation-main {
            width: 100% !important;
          }
          .supervisor-card {
            border: none !important;
            box-shadow: none !important;
          }
          .investigation-input, .investigation-textarea {
            border: none !important;
            background: none !important;
            padding: 0 !important;
          }
        }
      `}</style>
    </div>
  );
}
