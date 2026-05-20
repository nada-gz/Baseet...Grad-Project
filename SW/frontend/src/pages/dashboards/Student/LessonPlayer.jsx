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

  // Video State
  const [videoUrl, setVideoUrl] = useState(null);
  const [isLoadingVideo, setIsLoadingVideo] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("بسيط بيفكر...");
  const videoRef = useState(null)[1] || require("react").useRef(null); // Simple useRef since we are inside a function component

  const loadingMessages = [
    "بسيط بيفكر...",
    "بسيط بيجهز الفيديو...",
    "بسيط قرب يوصل...",
    "ثواني ويكون جاهز..."
  ];

  // Fetch Lesson & Generate Video
  useEffect(() => {
    const loadLessonAndVideo = async () => {
      if (!student) return;

      try {
        // 1. Load Lesson Details
        const res = await api.get(`/students/${student.id}/lessons/${lessonId}`);
        console.log("Lesson loaded:", res.data);
        setLesson(res.data);

        // 2. Generate Video (Unlocks sync generation)
        setIsLoadingVideo(true);
        try {
          // This endpoint now waits for generation to complete (~1 min)
          const videoRes = await api.post("/ai/video/generate", {
            lesson_id: parseInt(lessonId),
            student_id: student.id,
            duration: 1.0 // Default duration
          });

          if (videoRes.data && videoRes.data.video_url) {
            // Prepend base URL if it's a relative path
            const url = videoRes.data.video_url.startsWith("http")
              ? videoRes.data.video_url
              : `http://127.0.0.1:8000${videoRes.data.video_url}`;
            setVideoUrl(url);
          }
        } catch (videoError) {
          console.error("Video generation failed:", videoError);
          // Optional: Set an error state or keeping placeholder
        } finally {
          setIsLoadingVideo(false);
        }

      } catch (error) {
        console.error("Failed to load lesson:", error);
        setLesson(null);
      } finally {
        setLoading(false);
      }
    };

    loadLessonAndVideo();
  }, [lessonId, student]);

  // Cycle Loading Messages
  useEffect(() => {
    if (!isLoadingVideo) return;

    let msgIndex = 0;
    const interval = setInterval(() => {
      msgIndex = (msgIndex + 1) % loadingMessages.length;
      setLoadingMessage(loadingMessages[msgIndex]);
    }, 3000);

    return () => clearInterval(interval);
  }, [isLoadingVideo]);

  // Video Controls
  const handlePlay = () => {
    if (videoRef.current) videoRef.current.play();
  };

  const handlePause = () => {
    if (videoRef.current) videoRef.current.pause();
  };

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
      {/* ================= VIDEO ================= */}
      <div className="lesson-video">
        {isLoadingVideo ? (
          <div className="video-placeholder" style={{ flexDirection: 'column', gap: '1rem' }}>
            <div className="animate-spin text-4xl">⏳</div>
            <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{loadingMessage}</p>
          </div>
        ) : videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            controls={false} // We typically use custom controls, but can enable native ones too
            className="video-element"
            style={{ width: '100%', height: '100%', borderRadius: '20px', objectFit: 'cover' }}
            autoPlay
          />
        ) : (
          <div className="video-placeholder">
            <div className="text-4xl">⚠️</div>
            <p>عفواً، لم نتمكن من تحميل الفيديو</p>
          </div>
        )}

        <img
          src={require("../../../assets/eyes_baseet.png")}
          alt="Eyes on border"
          className="eyes-border-chat"
          style={{ width: '60px', top: '-30px', left: '-10px' }}
        />
      </div>

      {/* ================= CONTROLS ================= */}
      <div className="lesson-controls">
        <button className="lesson-btn primary" onClick={handlePlay}>
          <Play size={24} /> تشغيل
        </button>

        <button className="lesson-btn secondary" onClick={handlePause}>
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
