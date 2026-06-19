import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../../../services/api";
import { API_BASE_URL } from "../../../config";
import useAuth from "../../../hooks/useAuth"; // <-- added
import { Play, Pause, Mic, Send, HelpCircle } from "lucide-react";

export default function LessonPlayer() {
  const { lessonId } = useParams();
  const { user: student, loading: authLoading } = useAuth(); // <-- get logged-in student
  const studentId = student?.student_id || student?.id;
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);

  // Video State
  const [videoUrl, setVideoUrl] = useState(null);
  const [isLoadingVideo, setIsLoadingVideo] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("بسيط بيفكر... ✨");
  const videoRef = useState(null)[1] || require("react").useRef(null); // Simple useRef since we are inside a function component

  const loadingMessages = [
    "بسيط بيجهز الفيديو الجميل... 🎬",
    "ثواني وجاي يا بطل بالفيديو! 🏃‍♂️",
    "فيديو بسيط قرب يوصل، جاهز يا بطل؟ 🌟",
    "بجري بأقصى سرعة عشان أجيب الفيديو! 🚀",
    "صبرك عليا يا بطل، الفيديو في الطريق... ✨",
    "حاضر يا بطل، بحضرلك مفاجأة حلوة أوي... 🍯",
    "جايلك في السكة، استناني ثواني... 🚶‍♂️"
  ];

  // Fetch Lesson & Generate Video
  useEffect(() => {
    const loadLessonAndVideo = async () => {
      if (!studentId) return;

      try {
        // 1. Load Lesson Details
        const res = await api.get(`/students/${studentId}/lessons/${lessonId}`);
        console.log("Lesson loaded:", res.data);
        setLesson(res.data);

        // 2. Generate Video (Unlocks sync generation)
        setIsLoadingVideo(true);
        try {
          // This endpoint now waits for generation to complete (~1 min)
          const videoRes = await api.post("/ai/video/generate", {
            lesson_id: parseInt(lessonId),
            student_id: studentId,
            duration: 1.0 // Default duration
          });

          if (videoRes.data && videoRes.data.video_url) {
            // Prepend base URL if it's a relative path
            const url = videoRes.data.video_url.startsWith("http")
              ? videoRes.data.video_url
              : `${API_BASE_URL}${videoRes.data.video_url}`;
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
  }, [lessonId, studentId]);

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
          <div className="video-placeholder" style={{ 
            flexDirection: 'column', 
            gap: '2rem',
            background: 'linear-gradient(135deg, #FFF9E6 0%, #FFF1C1 100%)',
            border: '6px dashed #FFA726',
            boxShadow: 'inset 0 0 20px rgba(255, 167, 38, 0.15)',
            borderRadius: '24px',
            padding: '3rem',
            height: '500px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Soft decorative background circles */}
            <div style={{
              position: 'absolute',
              top: '-50px',
              right: '-50px',
              width: '150px',
              height: '150px',
              background: 'rgba(255, 255, 255, 0.4)',
              borderRadius: '50%',
              filter: 'blur(10px)',
              pointerEvents: 'none'
            }} />
            <div style={{
              position: 'absolute',
              bottom: '-30px',
              left: '-30px',
              width: '120px',
              height: '120px',
              background: 'rgba(255, 255, 255, 0.4)',
              borderRadius: '50%',
              filter: 'blur(10px)',
              pointerEvents: 'none'
            }} />

            {/* Glowing/Pulsing character avatar container */}
            <div style={{
              position: 'relative',
              width: '160px',
              height: '160px',
              borderRadius: '50%',
              background: 'white',
              border: '6px solid #4F46E5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 15px 30px rgba(79, 70, 229, 0.15)',
              animation: 'loading-pulse 2s infinite ease-in-out'
            }}>
              <img
                src={require("../../../assets/BASEET-smiling.png")}
                alt="Baseet loading"
                style={{
                  width: '110px',
                  height: 'auto',
                  animation: 'loading-float 3s infinite ease-in-out'
                }}
              />
              {/* Spinner surrounding the avatar */}
              <div className="loader-spinner" style={{
                position: 'absolute',
                inset: '-12px',
                border: '4px solid transparent',
                borderTopColor: '#FFA726',
                borderBottomColor: '#4F46E5',
                borderRadius: '50%',
                animation: 'spin 1.5s linear infinite'
              }} />
            </div>

            {/* Custom keyframes injection inside a style tag to keep it clean */}
            <style>{`
              @keyframes loading-pulse {
                0% { transform: scale(1); box-shadow: 0 15px 30px rgba(79, 70, 229, 0.15); }
                50% { transform: scale(1.05); box-shadow: 0 20px 40px rgba(255, 167, 38, 0.3); }
                100% { transform: scale(1); box-shadow: 0 15px 30px rgba(79, 70, 229, 0.15); }
              }
              @keyframes loading-float {
                0% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-8px) rotate(3deg); }
                100% { transform: translateY(0px) rotate(0deg); }
              }
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>

            <div style={{
              background: 'rgba(255, 255, 255, 0.9)',
              padding: '12px 30px',
              borderRadius: '40px',
              border: '3px solid #FFA726',
              boxShadow: '0 8px 0 #FFF1C1',
              maxWidth: '90%',
              textAlign: 'center'
            }}>
              <p style={{ 
                fontSize: '1.4rem', 
                fontWeight: '900', 
                color: '#2D3748',
                margin: 0,
                direction: 'rtl'
              }}>
                {loadingMessage}
              </p>
            </div>
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
