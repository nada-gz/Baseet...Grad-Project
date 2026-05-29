import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Lock, RotateCcw, Play, Brain, Sparkles } from "lucide-react";

export default function StudentLessons() {
  const { user: student } = useAuth();
  const { courseId } = useParams();
  const navigate = useNavigate();

  const [milestones, setMilestones] = useState({});
  const [courseSubject, setCourseSubject] = useState("Generic");
  const [confirmLesson, setConfirmLesson] = useState(null);
  const [selectionModal, setSelectionModal] = useState(null); // { lessonId: ... }

  const groupByMilestone = (lessons) => {
    const grouped = {};
    lessons.forEach((lesson) => {
      const key = lesson.milestone_number;
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(lesson);
    });
    Object.values(grouped).forEach(list =>
      list.sort((a, b) => a.lesson_number - b.lesson_number)
    );
    return grouped;
  };

  const loadLessons = async () => {
    if (!student?.id || !courseId) return;
    try {
      const res = await api.get(`/students/${student.id}/lessons`, {
        params: { course_id: courseId }
      });
      const grouped = groupByMilestone(res.data);
      setMilestones(grouped);

      // Fetch course subject
      const coursesRes = await api.get(`/students/${student.id}/assigned-courses`);
      const currentCourse = coursesRes.data.find(c => c.id === parseInt(courseId));
      if (currentCourse) {
        setCourseSubject(currentCourse.subject || 'Generic');
      }
    } catch (err) {
      console.error("Failed to load lessons:", err);
    }
  };

  useEffect(() => {
    loadLessons();
  }, [student?.id, courseId]);

  const resetLesson = async (lessonId) => {
    try {
      await api.patch(`/students/${student.id}/lessons/${lessonId}`, {
        progress: 0
      });
      setConfirmLesson(null);
      // reload lessons
      loadLessons();
      // Show selection modal to pick mode for the retaken lesson
      setSelectionModal({ id: lessonId });
    } catch (err) {
      console.error("Failed to reset lesson:", err);
    }
  };

  return (
    <div className="student-lessons-page kid-friendly-vibe">
      <div className="hero-blob-container assignments-style" style={{ borderColor: '#D6DEFF', boxShadow: '0 12px 0 #D6DEFF' }}>
        <div className="hero-blob-bg" style={{ background: 'radial-gradient(circle, #F1F4FF 0%, #D6DEFF 100%)' }}></div>
        <div className="hero-blob-content">
          <div className="hero-blob-image-wrapper shift-right">
            <img
              src={require("../../../assets/hii_baseet.png")}
              alt="Greeting Baseet"
              className="hero-blob-img"
            />
          </div>
          <div className="hero-blob-text">
            <h1 style={{ color: '#4A90E2' }}>✨ ! مغامرتك التعليمية</h1>
            <p>املى الطريق بالنجوم وكمل دروسك يا بطل</p>
          </div>
        </div>
      </div>

      {/* Math Tutor Card - Immersive & Animated */}
      {courseSubject?.toLowerCase() === 'math' && (
        <motion.div 
          className="math-adventure-promo" 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ 
            width: '100%', 
            margin: '0.5rem 0 2rem 0', 
            padding: '0 1rem' 
          }}
        >
          <div style={{
            background: 'linear-gradient(135deg, #6366F1 0%, #A855F7 100%)',
            borderRadius: '30px',
            padding: '2.5rem',
            color: 'white',
            display: 'flex',
            flexDirection: 'row-reverse', // Arabic friendly layout
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 20px 40px rgba(99, 102, 241, 0.25)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Decorative Background Elements */}
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              style={{
                position: 'absolute',
                top: '-50px',
                right: '-50px',
                width: '150px',
                height: '150px',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '40% 60% 70% 30% / 40% 50% 60% 50%',
                filter: 'blur(20px)'
              }}
            />
            
            <div style={{ flex: 1, textAlign: 'right', position: 'relative', zIndex: 2 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '15px', marginBottom: '1.2rem' }}>
                <h2 style={{ fontSize: '2.2rem', fontWeight: '900', textShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                 ✨ ! مغامرة الحساب مع بسيط 
                </h2>
                <motion.div 
                  animate={{ y: [0, -8, 0], rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 4, repeat: Infinity }}
                  style={{ background: 'rgba(255,255,255,0.25)', padding: '12px', borderRadius: '18px', backdropFilter: 'blur(5px)' }}
                >
                  <Brain size={40} />
                </motion.div>
              </div>
              
              <p style={{ fontSize: '1.25rem', lineHeight: '1.6', opacity: 0.95, marginBottom: '2rem', maxWidth: '600px', marginLeft: 'auto' }}>
                 بسيط مستنيك يا بطل عشان نفهم الأرقام ونلعب مع المكعبات سوا ونخلص كل تحديات الحساب بسهولة جداً 
              </p>
              
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: '0 10px 20px rgba(0,0,0,0.15)' }}
                whileTap={{ scale: 0.95 }}
                onClick={async () => {
                  try {
                    await api.post(`/api/math/reset/${student.id}`);
                    navigate("/dashboard/student/math-tutor");
                  } catch (err) {
                    console.error("Failed to reset math mastery:", err);
                    navigate("/dashboard/student/math-tutor"); // Fallback navigate
                  }
                }}
                className="btn"
                style={{ 
                  background: 'white', 
                  color: '#6366F1', 
                  fontWeight: '800', 
                  padding: '16px 45px', 
                  borderRadius: '16px',
                  fontSize: '1.2rem',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  marginRight: '0',
                  marginLeft: 'auto',
                  cursor: 'pointer'
                }}
              >
                <Brain size={20} />
                يلا بينا نبدأ المغامرة
              </motion.button>
            </div>

            <div style={{ display: 'none' }} className="promo-decorative-icon lg:block lg:flex-1">
               {/* Space reserved for 3D illustration or character */}
            </div>
          </div>
        </motion.div>
      )}

      {Object.keys(milestones).length === 0 ? (
        <div className="empty-milestones">
          <p>لسه مفيش دروس موجودة.. بسيط مستنيك!</p>
        </div>
      ) : (
        <div className="milestones-container">
          {Object.entries(milestones)
            .sort(([a], [b]) => Number(a) - Number(b))
            .map(([milestoneNumberStr, lessons]) => {
              const milestoneNumber = Number(milestoneNumberStr);
              return (
                <div key={milestoneNumber} className="milestone-island">
                  <div className="milestone-header">
                    <div className="milestone-badge">مرحلة {milestoneNumber}</div>
                  </div>

                  <div className="lesson-path">
                    {lessons.map((lesson) => {
                      const status = lesson.status;

                      return (
                        <div key={lesson.id} className={`lesson-bubble ${status}`}>
                          <div className="lesson-icon-outer">
                            <div className="lesson-icon">
                              {status === "locked" ? <Lock size={24} /> : lesson.number}
                            </div>
                          </div>

                          <div className="lesson-info">
                            <h3 className="lesson-title">{lesson.title}</h3>
                            <p className="lesson-desc">{lesson.description}</p>

                            <div className="progress-bar-mini">
                              <div
                                className="progress-fill"
                                style={{ width: `${lesson.progress}%` }}
                              />
                            </div>
                          </div>

                          <div className="lesson-actions">
                            {status === "completed" && (
                              <button
                                className="btn-circle btn-retake"
                                onClick={() => setConfirmLesson(lesson)}
                                title="إعادة الدرس"
                              >
                                <RotateCcw size={18} />
                              </button>
                            )}

                            {status === "in-progress" && (
                              <button
                                className="btn btn-primary btn-sm rounded-full"
                                onClick={() =>
                                  setSelectionModal({ id: lesson.id })
                                }
                              >
                                <Play size={18} /> استكمال
                              </button>
                            )}

                            {status === "locked" && (
                              <div className="locked-badge">مغلق</div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {confirmLesson && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h3>Retake Lesson?</h3>
            <p>This will reset your progress to 0%.</p>

            <div className="modal-actions">
              <button
                type="button"
                className="btn btn-danger"
                onClick={() => resetLesson(confirmLesson.id)}
              >
                Yes, Retake
              </button>

              <button
                type="button"
                className="btn btn-outline"
                onClick={() => setConfirmLesson(null)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {selectionModal && (
        <div className="modal-overlay">
          <div className="modal-card lesson-selection-modal">
            <div className="baseet-selection-header">
              <img
                src={require("../../../assets/hi_baseet.png")}
                alt="Baseet waving"
                className="baseet-selection-img"
              />
              <h3>بسيط مستني يكلمك! ✨</h3>
              <p>تحب تذاكر الدرس ده بـ الشات، الصوت، ولا الفيديو؟</p>
            </div>

            <div className="selection-actions">
              <button
                className="selection-btn video-mode"
                onClick={() => {
                  window.location.href = `/dashboard/student/lesson/${selectionModal.id}/video`;
                  setSelectionModal(null);
                }}
              >
                <div className="mode-icon">🎬</div>
                <span>فيديو</span>
              </button>
              <button
                className="selection-btn chat-mode"
                onClick={() => {
                  window.location.href = `/dashboard/student/lesson/${selectionModal.id}`;
                  setSelectionModal(null);
                }}
              >
                <div className="mode-icon">💬</div>
                <span>شات</span>
              </button>

              <button
                className="selection-btn voice-mode"
                onClick={() => {
                  window.location.href = `/dashboard/student/lesson/${selectionModal.id}/voice`;
                  setSelectionModal(null);
                }}
              >
                <div className="mode-icon">🎙️</div>
                <span>صوت</span>
              </button>
            </div>

            <button
              className="btn btn-outline close-selection"
              onClick={() => setSelectionModal(null)}
            >
              إلغاء
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
