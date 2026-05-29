import React, { useState, useEffect } from "react"; 
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../services/api";
import {
    BookOpen,
    CheckCircle2,
    Clock,
    Lock,
    ArrowLeft,
    FileText,
    Star,
    MessageCircle,
    Download,
    Eye,
    Mic,
    MessageSquare,
    Send,
    X,
    AlertTriangle,
    TrendingUp
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function StudentEducationalProgress() {
    const { studentId } = useParams();
    const navigate = useNavigate();
    const [progressData, setProgressData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Feedback interaction states
    const [evaluatingId, setEvaluatingId] = useState(null);
    const [feedback, setFeedback] = useState("");
    const [rating, setRating] = useState(5);
    const [hoverRating, setHoverRating] = useState(0);

    const [errorMessage, setErrorMessage] = useState(null);

    // Lesson Comment Modal State
    const [showCommentModal, setShowCommentModal] = useState(false);
    const [selectedLesson, setSelectedLesson] = useState(null);
    const [commentData, setCommentData] = useState({ title: "", message: "", is_urgent: false });
    const [commentStatus, setCommentStatus] = useState({ loading: false, error: null, success: false });

    useEffect(() => {
        fetchProgress();
    }, [studentId]);

    const fetchProgress = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/teacher/students/${studentId}/progress`);
            setProgressData(res.data);
            setError(null);
        } catch (err) {
            console.error("Error fetching progress:", err);
            setError("Failed to load student progress. Make sure the student has assigned lessons.");
        } finally {
            setLoading(false);
        }
    };

    const handleEvaluate = async (submissionId) => {
        setErrorMessage(null);
        try {
            const formData = new FormData();
            formData.append("comment", feedback);
            formData.append("rating", rating);

            await api.postForm(`/teacher/submissions/${submissionId}/feedback`, formData);

            setEvaluatingId(null);
            setFeedback("");
            fetchProgress(); // Refresh data
        } catch (err) {
            console.error("Evaluation error:", err);
            const msg = err.response?.data?.detail || "Error saving feedback";
            setErrorMessage(typeof msg === 'string' ? msg : JSON.stringify(msg));
        }
    };

    const handleSendComment = async (e) => {
        e.preventDefault();
        if (!selectedLesson) return;
        setCommentStatus({ loading: true, error: null, success: false });
        
        try {
            await api.post(`/teacher/students/${studentId}/lessons/${selectedLesson.id}/comment`, {
                title: commentData.title,
                message: commentData.message,
                is_urgent: commentData.is_urgent
            });

            setCommentStatus({ loading: false, error: null, success: true });
            setTimeout(() => {
                setShowCommentModal(false);
                setCommentData({ title: "", message: "", is_urgent: false });
                setCommentStatus({ loading: false, error: null, success: false });
            }, 2000);
        } catch (err) {
            setCommentStatus({ 
                loading: false, 
                error: err.response?.data?.detail || "Could not send comment.", 
                success: false 
            });
        }
    };

    if (loading) return <div className="loading-state">Loading educational journey...</div>;
    if (error) return (
        <div className="page-container">
            <button className="back-button back-btn-progress" onClick={() => navigate(-1)}>
                <ArrowLeft size={18} /> Back
            </button>
            <div className="empty-placeholder">{error}</div>
        </div>
    );

    const { student, milestones } = progressData;

    return (
        <div className="page-container">
            <div className="progress-dashboard">
                {/* 1. Fixed Left Sidebar */}
                <aside className="student-info-sidebar">
                    <header className="mb-4">
                        <button className="back-button back-btn-progress" onClick={() => navigate(-1)}>
                            <ArrowLeft size={18} /> Back
                        </button>
                        <div className="mt-4">
                            <h1 className="page-title mb-1" style={{ fontSize: '1.4rem' }}>Educational Progress</h1>
                            <p className="text-secondary-text" style={{ fontSize: '0.9rem' }}>
                                For <strong>{student.username}</strong>
                            </p>
                        </div>
                    </header>

                    {errorMessage && (
                        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded relative text-sm">
                            <strong className="font-bold block">Error: </strong>
                            <span className="block">{errorMessage}</span>
                            <button className="absolute top-0 right-0 p-2 font-bold" onClick={() => setErrorMessage(null)}>×</button>
                        </div>
                    )}

                    <div className="student-monitoring-card">
                        <div className="card-student-header">
                            <div className="card-avatar">
                                {student.username[0].toUpperCase()}
                            </div>
                            <div className="card-student-info">
                                <h3>{student.username}</h3>
                                <p style={{ fontSize: '0.75rem', opacity: 0.7 }}>{student.email}</p>
                            </div>
                        </div>

                        <div className="card-details-grid">
                            <div className="detail-item">
                                <span className="detail-label">Class</span>
                                <span className="detail-value">{student.classroom_name || "N/A"}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Level</span>
                                <span className="detail-value">{student.level_name || "N/A"}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">State</span>
                                <span className={`detail-value ${student.state === 'Stressed' ? 'state-stressed' : 'state-relaxed'}`}>
                                    {student.state}
                                </span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Age</span>
                                <span className="detail-value">{student.age} yrs</span>
                            </div>
                        </div>

                        <div className="mt-4 p-4 bg-slate-50 rounded-xl">
                            <div className="prog">
                                <span className="text-sm font-bold">
                                    Overall <span className="font-black">Progress</span>
                                </span>

                                <span className="text-highlight font-black">
                                    {Math.round(
                                        milestones.reduce(
                                            (acc, m) =>
                                                acc +
                                                m.lessons.reduce((lacc, l) => lacc + l.progress, 0) /
                                                (m.lessons.length || 1),
                                            0
                                        ) / (milestones.length || 1)
                                    )}
                                    %
                                </span>
                            </div>

                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{ width: `${Math.round(milestones.reduce((acc, m) => acc + (m.lessons.reduce((lacc, l) => lacc + l.progress, 0) / (m.lessons.length || 1)), 0) / (milestones.length || 1))}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </aside>

                {/* 2. Main Timeline Area (Scrollable) */}
                <main className="milestone-timeline">
                    {milestones.length === 0 ? (
                        <div className="empty-placeholder">No milestones assigned yet.</div>
                    ) : (
                        milestones.map((milestone, index) => (
                            <div key={`${milestone.id || index}-${milestone.milestone_number}`} className="milestone-node">
                                {index === 0 || milestones[index - 1].course_id !== milestone.course_id ? (
                                    <h3 className="course-divider-label">
                                        Course {milestone.course_id}
                                    </h3>
                                ) : null}
                                <div className="milestone-marker">
                                    {milestone.milestone_number}
                                </div>
                                {/* <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-4 ml-14">
                                    Milestone {milestone.milestone_number}
                                </h3> */}
                                <div className="lesson-progress-grid">
                                    {milestone.lessons.map((lesson) => (
                                        <div key={lesson.id} className={`lesson-progress-card status-${lesson.status}`}>
                                            <div className="lesson-card-header">
                                                <div className="flex items-center justify-between w-full">
                                                    {/* Left: Info */}
                                                    <div>
                                                        <h4 style={{ margin: 0, fontSize: "1.1rem" }}>{lesson.title}</h4>
                                                        <div className="progress-status-group mt-1">
                                                            {lesson.status === 'completed' && <CheckCircle2 size={16} className="text-emerald-500" />}
                                                            {lesson.status === 'in-progress' && <Clock size={16} className="text-amber-500" />}
                                                            {lesson.status === 'locked' && <Lock size={16} className="text-slate-400" />}
                                                            <span className="text-sm capitalize font-medium text-slate-500">{lesson.status}</span>
                                                        </div>
                                                    </div>
                                                    
                                                    {/* Right: Button and Percentage below */}
                                                    <div className="flex flex-col items-end gap-2">
                                                        <button 
                                                            title="Feedback for Parent"
                                                            onClick={() => {
                                                                setSelectedLesson(lesson);
                                                                setShowCommentModal(true);
                                                                setCommentData({ title: `Feedback on ${lesson.title}`, message: "", is_urgent: false });
                                                            }}
                                                            className="feedback-btn"
                                                            style={{
                                                                background: "var(--primary-bg)",
                                                                border: "2px solid var(--neutral)",
                                                                borderRadius: "10px",
                                                                padding: "6px 12px",
                                                                color: "var(--highlight)",
                                                                cursor: "pointer",
                                                                display: "flex",
                                                                alignItems: "center",
                                                                gap: "6px",
                                                                fontSize: "0.75rem",
                                                                fontWeight: "800",
                                                                transition: "all 0.2s"
                                                            }}
                                                        >
                                                            <MessageSquare size={14} />
                                                            <span>Feedback to Parent</span>
                                                        </button>

                                                        <div className="flex items-center" style={{ background: "var(--primary-bg)", padding: "5px 12px", borderRadius: "10px", border: "1px solid var(--neutral)", marginTop: "2px" }}>
                                                            <TrendingUp size={14} style={{ color: "var(--highlight)", marginRight: "8px" }} />
                                                            <span style={{ fontSize: "0.85rem", fontWeight: "950", color: "var(--highlight)", display: "flex", alignItems: "center" }}>
                                                                {lesson.progress}% 
                                                                <span style={{ fontSize: "0.65rem", opacity: 0.6, fontWeight: "900", marginLeft: "8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                                                                    Progress
                                                                </span>
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Assignments List */}
                                            {lesson.assignments.length > 0 && (
                                                <div className="assignments-section">
                                                    <h5 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-4 ml-1 ass-feed">Assignments & Feedback</h5>
                                                    {lesson.assignments.map((assign) => (
                                                        <div key={assign.id} className="assignment-item-block">
                                                            {/* 1. File & View Part */}
                                                            <div className="assignment-file-row">
                                                                <div className="flex items-center gap-3">
                                                                    <FileText size={20} className="icon-st text-slate-400" />
                                                                    <div>
                                                                        <p className="font-bold text-slate-700 text-sm">{assign.title}</p>
                                                                        <div className="flex items-center gap-2">
                                                                            <span className={`status-badge-mini ${assign.status === 'evaluated' ? 'badge-evaluated' :
                                                                                assign.status === 'resubmitted' ? 'badge-resubmitted' :
                                                                                    assign.status === 'submitted' ? 'badge-submitted' : 'badge-not-submitted'
                                                                                }`}>
                                                                                {assign.status}
                                                                            </span>
                                                                            {assign.timing && (
                                                                                <span className="text-[10px] text-slate-400">
                                                                                    {assign.status === 'resubmitted' ? 'Resubmitted' : 'Submitted'} at: {new Date(assign.timing).toLocaleString()}
                                                                                </span>
                                                                            )}
                                                                        </div>
                                                                    </div>
                                                                </div>

                                                                <div className="file-actions-group">
                                                                    {assign.assignment_file_url && (
                                                                        <a
                                                                            href={`${api.defaults.baseURL}${assign.assignment_file_url}`}
                                                                            target="_blank"
                                                                            rel="noreferrer"
                                                                            className="btn-view-file"
                                                                        >
                                                                            <Eye size={16} />
                                                                            <span>View Assignment</span>
                                                                        </a>
                                                                    )}
                                                                    {(assign.status === 'submitted' || assign.status === 'resubmitted' || assign.status === 'evaluated') && assign.file_url && (
                                                                        <a
                                                                            href={`${api.defaults.baseURL}${assign.file_url}`}
                                                                            target="_blank"
                                                                            rel="noreferrer"
                                                                            className="btn-view-file submission"
                                                                        >
                                                                            <Eye size={16} />
                                                                            <span>View Submission</span>
                                                                        </a>
                                                                    )}
                                                                </div>
                                                            </div>

                                                            {/* Narrative Discovery Metrics (Using fixed CSS classes) */}
                                                            {assign.submission_method === 'voice' && (
                                                                <div className="narrative-analysis-card-fixed">
                                                                    <div className="flex flex-col gap-4">
                                                                        {/* Top Row: Info & AI Badge */}
                                                                        <div className="flex items-center justify-between">
                                                                            <span className="flex items-center gap-1.5 text-[11px] font-extrabold text-indigo-700 bg-white px-3 py-1.5 rounded-full border border-indigo-100 shadow-sm">
                                                                                <Mic size={14} className="text-indigo-500" /> Voice Submission
                                                                            </span>
                                                                            <div className="ai-badge flex items-center gap-1.5 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-100 px-2 py-1 rounded-md">
                                                                                <Star size={12} className="fill-amber-400 text-amber-400" /> AI Assisted Analysis
                                                                            </div>
                                                                        </div>

                                                                        {/* Story Grammar Discovery removed as per request */}

                                                                        {/* Bottom Row: Audio Player (Narrowed via class) */}
                                                                        {assign.audio_url && (
                                                                            <div className="audio-review-section pt-3 border-t border-indigo-50/50">
                                                                                <span className="text-[10px] uppercase font-black text-slate-400 block mb-2 text-center">Oral Submission Recording</span>
                                                                                <div className="audio-player-narrow-container">
                                                                                    <div className="shrink-0 bg-indigo-600 p-2 rounded-full shadow-lg">
                                                                                        <Mic size={14} className="text-white" />
                                                                                    </div>
                                                                                    <audio 
                                                                                        src={`${api.defaults.baseURL}${assign.audio_url}`} 
                                                                                        controls 
                                                                                        className="w-full h-8 custom-audio-player"
                                                                                    />
                                                                                </div>
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            )}

                                                            {/* 2. Evaluation Part (Underneath) */}
                                                            <div className="evaluation-row">
                                                                <div className="eval-top-section">
                                                                    <div className="eval-left-content">
                                                                        {/* Rating Section */}
                                                                        <div>
                                                                            <span className="text-[10px] font-black uppercase text-slate-400 block mb-1">Rating</span>
                                                                            {assign.status === 'evaluated' && evaluatingId !== assign.id ? (
                                                                                <div className="flex items-center gap-1">
                                                                                    {[1, 2, 3, 4, 5].map((s) => (
                                                                                        <Star
                                                                                            key={s}
                                                                                            size={16}
                                                                                            className={`star ${assign.rating >= s ? 'active' : 'inactive'}`}
                                                                                        />
                                                                                    ))}
                                                                                </div>
                                                                            ) : (
                                                                                <div className="text-xs text-slate-400 italic">No rating yet</div>
                                                                            )}
                                                                        </div>

                                                                        {/* Feedback Section */}
                                                                        <div>
                                                                            <span className="text-[10px] font-black uppercase text-slate-400 block mb-1">Teacher Feedback</span>
                                                                            {assign.status === 'evaluated' && evaluatingId !== assign.id ? (
                                                                                <p className="text-sm italic text-slate-600">
                                                                                    {assign.feedback || "No comment provided."}
                                                                                </p>
                                                                            ) : (
                                                                                <p className="text-xs text-slate-400 italic">No comment yet...</p>
                                                                            )}
                                                                        </div>
                                                                    </div>

                                                                    <div className="eval-right-actions">
                                                                        {(assign.status === 'submitted' || assign.status === 'resubmitted') && (
                                                                            <button
                                                                                className="btn btn-primary btn-small"
                                                                                onClick={() => {
                                                                                    if (!assign.submission_id) {
                                                                                        alert("Error: Missing submission ID");
                                                                                        return;
                                                                                    }
                                                                                    setEvaluatingId(assign.id); // View state based on assignment ID
                                                                                    setFeedback(assign.feedback || "");
                                                                                    setRating(assign.rating || 5);
                                                                                }}
                                                                            >
                                                                                Evaluate
                                                                            </button>
                                                                        )}
                                                                        {assign.status === 'evaluated' && evaluatingId !== assign.id && (
                                                                            <button
                                                                                className="btn-reevaluate"
                                                                                onClick={() => {
                                                                                    setEvaluatingId(assign.id);
                                                                                    setFeedback(assign.feedback || "");
                                                                                    setRating(assign.rating || 5);
                                                                                }}
                                                                            >
                                                                                Re-evaluate
                                                                            </button>
                                                                        )}
                                                                    </div>
                                                                </div>

                                                                {/* Full evaluation form if active */}
                                                                {evaluatingId === assign.id && (
                                                                    <div className="eval-form mt-2 border-t pt-4">
                                                                        <div className="flex flex-col gap-4">
                                                                            <div>
                                                                                <span className="text-sm font-bold block mb-2">Assign Rating</span>
                                                                                <div className="rating-stars" onMouseLeave={() => setHoverRating(0)}>
                                                                                    {[1, 2, 3, 4, 5].map((s) => (
                                                                                        <Star
                                                                                            key={s}
                                                                                            size={24}
                                                                                            className={`star ${(hoverRating || rating) >= s ? 'active' : 'inactive'}`}
                                                                                            onMouseEnter={() => setHoverRating(s)}
                                                                                            onClick={() => setRating(s)}
                                                                                        />
                                                                                    ))}
                                                                                </div>
                                                                            </div>
                                                                            <div>
                                                                                <span className="text-sm font-bold block mb-2">Comments</span>
                                                                                <textarea
                                                                                    placeholder="Provide constructive feedback..."
                                                                                    value={feedback}
                                                                                    onChange={(e) => setFeedback(e.target.value)}
                                                                                />
                                                                            </div>
                                                                            <div className="eval-footer-btns">
                                                                                <button className="btn btn-outline btn-small" onClick={() => setEvaluatingId(null)}>Cancel</button>
                                                                                <button className="btn btn-primary btn-small" onClick={() => handleEvaluate(assign.submission_id)}>Save Evaluation</button>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))
                    )}
                </main>
            </div>

            {/* Lesson Comment Modal */}
            {showCommentModal && (
                <div 
                    style={{ 
                        position: "fixed", top: 0, left: 0, width: "100%", height: "100%", 
                        background: "rgba(0,0,0,0.7)", zIndex: 1000, display: "flex", 
                        alignItems: "center", justifyContent: "center", padding: "20px",
                        backdropFilter: "blur(12px)"
                    }}
                >
                    <div 
                            className="teacher-modal-box" 
                            style={{ 
                                width: "100%", 
                                maxWidth: "700px", 
                                minHeight: "500px",
                                padding: "60px", 
                                position: "relative", 
                                background: "white", 
                                borderRadius: "40px", 
                                border: "10px solid var(--neutral)",
                                boxShadow: "0 40px 80px rgba(0,0,0,0.3)",
                                textAlign: "left",
                                display: "flex",
                                flexDirection: "column"
                            }}
                        >
                            <button 
                                onClick={() => setShowCommentModal(false)}
                                style={{ position: "absolute", right: "25px", top: "25px", background: "var(--primary-bg)", border: "none", borderRadius: "15px", padding: "12px", cursor: "pointer", color: "var(--secondary-text)", transition: "all 0.2s" }}
                            >
                                <X size={24} />
                            </button>

                            <div style={{ marginBottom: "40px" }}>
                                <h2 style={{ fontSize: "2.2rem", fontWeight: "950", color: "var(--highlight)", margin: "0 0 10px 0" }}>Lesson Feedback</h2>
                                <p style={{ color: "var(--secondary-text)", fontSize: "1.1rem" }}>
                                    Message for <strong>{student.username}</strong>'s parent regarding <strong>{selectedLesson?.title}</strong>.
                                </p>
                            </div>

                            {/* Using display toggle instead of conditional rendering to prevent DOM removal crashes */}
                            <div style={{ display: commentStatus.success ? 'none' : 'block', flex: 1 }}>
                                <form 
                                    onSubmit={handleSendComment}
                                    style={{ display: "flex", flexDirection: "column", height: "100%" }}
                                >
                                    <div style={{ marginBottom: "25px" }}>
                                        <label style={{ fontWeight: "800", display: "block", marginBottom: "12px", fontSize: "1rem", color: "var(--primary-text)" }}>Title</label>
                                        <input 
                                            type="text" 
                                            placeholder="e.g. Lesson Performance" 
                                            value={commentData.title}
                                            onChange={(e) => setCommentData({ ...commentData, title: e.target.value })}
                                            required
                                            style={{ width: "100%", padding: "18px", borderRadius: "18px", border: "4px solid var(--neutral)", fontSize: "1.1rem", outline: "none" }}
                                        />
                                    </div>

                                    <div style={{ marginBottom: "25px" }}>
                                        <label style={{ fontWeight: "800", display: "block", marginBottom: "12px", fontSize: "1rem", color: "var(--primary-text)" }}>Comment Message</label>
                                        <textarea 
                                            placeholder="What would you like to share with the parent?" 
                                            rows={6}
                                            value={commentData.message}
                                            onChange={(e) => setCommentData({ ...commentData, message: e.target.value })}
                                            style={{ width: "100%", padding: "20px", borderRadius: "20px", border: "4px solid var(--neutral)", fontFamily: "inherit", fontSize: "1.1rem", outline: "none", resize: "none" }}
                                            required
                                        />
                                    </div>

                                    <div style={{ 
                                        marginBottom: "35px", 
                                        display: "flex", 
                                        alignItems: "center", 
                                        gap: "15px", 
                                        background: commentData.is_urgent ? "rgba(255, 71, 87, 0.05)" : "var(--primary-bg)", 
                                        padding: "20px", 
                                        borderRadius: "20px", 
                                        border: `2px solid ${commentData.is_urgent ? 'rgba(255, 71, 87, 0.2)' : 'transparent'}`,
                                        transition: "all 0.3s" 
                                    }}>
                                        <input 
                                            type="checkbox" 
                                            id="urgent-comment" 
                                            checked={commentData.is_urgent}
                                            onChange={(e) => setCommentData({ ...commentData, is_urgent: e.target.checked })}
                                            style={{ width: "24px", height: "24px", margin: 0, cursor: "pointer" }}
                                        />
                                        <label htmlFor="urgent-comment" style={{ fontWeight: "900", color: commentData.is_urgent ? "#FF4757" : "var(--primary-text)", display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "1rem" }}>
                                            {commentData.is_urgent && <AlertTriangle size={20} />}
                                            Mark as Urgent
                                        </label>
                                    </div>

                                    {commentStatus.error && (
                                        <p style={{ color: "#FF4757", fontSize: "0.95rem", fontWeight: "800", marginBottom: "25px", textAlign: "center", padding: "10px", background: "rgba(255, 71, 87, 0.1)", borderRadius: "10px" }}>
                                            {commentStatus.error}
                                        </p>
                                    )}

                                    <button 
                                        type="submit" 
                                        className="btn btn-primary" 
                                        style={{ width: "100%", padding: "20px", fontSize: "1.2rem", borderRadius: "20px" }}
                                        disabled={commentStatus.loading}
                                    >
                                        {commentStatus.loading ? "Sending..." : <><Send size={22} style={{ marginRight: "12px" }} /> Send Feedback</>}
                                    </button>
                                </form>
                            </div>

                            <div style={{ display: commentStatus.success ? 'flex' : 'none', textAlign: "center", padding: "60px 0", flex: 1, flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
                                <CheckCircle2 size={80} color="#00F5D4" style={{ marginBottom: "25px" }} />
                                <h3 style={{ color: "var(--primary-text)", fontSize: "2rem", fontWeight: "900" }}>Feedback Sent!</h3>
                                <p style={{ color: "var(--secondary-text)", fontSize: "1.1rem", marginTop: "10px" }}>The guardian has been notified about this lesson.</p>
                            </div>
                    </div>
                </div>
            )}
        </div>
    );
}
