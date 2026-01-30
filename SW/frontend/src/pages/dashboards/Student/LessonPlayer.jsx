import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth"; // <-- added
import { Play, Pause, Mic, Send, HelpCircle } from "lucide-react";

export default function LessonPlayer() {
  const { lessonId } = useParams();
  const { user: student, loading: authLoading } = useAuth(); // <-- get logged-in student
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLesson = async () => {
      if (!student) return; // wait until student info is loaded

      try {
        // Call backend to get a single lesson for this student
        const res = await api.get(`/students/${student.id}/lessons/${lessonId}`);
        console.log("Lesson loaded:", res.data);
        setLesson(res.data);
      } catch (error) {
        console.error("Failed to load lesson:", error);
        setLesson(null);
      } finally {
        setLoading(false);
      }
    };

    loadLesson();
  }, [lessonId, student]);

  if (authLoading || loading) return <div>Loading lesson...</div>;
  if (!lesson) return <div>Lesson not found.</div>;

  return (
    <div className="lesson-player">
      {/* Floating Asset */}
      <img
        src={require("../../../assets/hi_baseet.png")}
        alt="Baseet"
        className="chat-floating-baseet"
      />

      {/* Header */}
      <div className="hero-blob-container compact" style={{ marginBottom: '30px', width: '100%' }}>
        <div className="hero-blob-bg" style={{ background: 'linear-gradient(135deg, #FFF9E6 0%, #FFF1C1 100%)' }}></div>
        <div className="hero-blob-content">
          <div className="hero-blob-text">
            <h1 style={{ fontSize: '2.2rem', marginBottom: '10px' }}>
              <span className="lesson-number">{lesson.number}</span>{" "}
              {lesson.title}
            </h1>
            <div className="lesson-helper">
              <img
                src={require("../../../assets/BASEET-smiling.png")}
                alt="Baseet helper"
                style={{ width: '50px' }}
              />
              <span style={{ fontWeight: 800 }}>أهلاً! أنا بسيط</span>
            </div>
          </div>
        </div>
      </div>

      {/* ================= VIDEO ================= */}
      <div className="lesson-video">
        <div className="video-placeholder">
          <div className="animate-bounce text-4xl">🎬</div>
          ! فيديو الدرس هيكون هنا يا بطل
        </div>

        <img
          src={require("../../../assets/eyes_baseet.png")}
          alt="Eyes on border"
          className="eyes-border-chat"
          style={{ width: '60px', top: '-30px', left: '-10px' }}
        />
      </div>

      {/* ================= CONTROLS ================= */}
      <div className="lesson-controls">
        <button className="lesson-btn primary">
          <Play size={24} /> تشغيل
        </button>

        <button className="lesson-btn secondary">
          <Pause size={24} /> إيقاف مؤقت
        </button>

        <button className="lesson-btn outline">
          <Mic size={24} /> سجل ملاحظة
        </button>
      </div>

      {/* ================= Q&A ================= */}
      <div className="chat-messages" style={{ minHeight: '150px', maxHeight: '300px' }}>
        <div className="chat-bubble ai">
          <div className="ai-avatar-msg">
            <img src={require("../../../assets/BASEET-smiling.png")} alt="Baseet" />
          </div>
          <div className="ai-text">
            ✨ ! عندك أي سؤال عن الفيديو؟ أنا هنا عشان أساعدك
          </div>
        </div>
      </div>

      <div className="chat-input-wrapper">
        <div className="chat-input">
          <textarea
            dir="rtl"
            placeholder="اسأل بسيط أي حاجة... ✨"
            style={{ textAlign: "right" }}
          />
          <button className="btn btn-primary send-btn">
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
