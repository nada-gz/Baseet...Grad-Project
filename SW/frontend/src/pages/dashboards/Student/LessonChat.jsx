import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Send, Volume2, Pause, Play, Square, Mic, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function LessonChat() {
  const { lessonId } = useParams();
  const { user: student } = useAuth();

  const [lesson, setLesson] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loadingAI, setLoadingAI] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [audioState, setAudioState] = useState({ idx: null, playing: false, paused: false });
  const [lessonProgress, setLessonProgress] = useState(0);
  const audioRef = useRef(null);

  const messagesEndRef = useRef(null);
  const hasStarted = useRef(false);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loadingAI]);

  // Load lesson + start explanation
  useEffect(() => {
    if (!student || hasStarted.current) return;
    hasStarted.current = true;

    const startLesson = async () => {
      try {
        setLoadingAI(true);

        const res = await api.get(
          `/students/${student.id}/lessons/${lessonId}`
        );
        setLesson(res.data);

        const aiRes = await api.post("/ai/lesson/start", {
          lesson_id: lessonId,
          student_id: student.id,
        });

        if (aiRes.data.progress !== undefined) {
          setLessonProgress(aiRes.data.progress);
        }
        addAIPulses(aiRes.data.message);
      } catch (err) {
        console.error("Failed to load lesson chat", err);
      } finally {
        setLoadingAI(false);
      }
    };

    startLesson();
  }, [lessonId, student]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoadingAI(true);

    try {
      const res = await api.post("/ai/lesson/chat", {
        lesson_id: lessonId,
        student_id: student.id,
        message: input,
      });

      if (res.data.progress !== undefined) {
        setLessonProgress(res.data.progress);
      }
      addAIPulses(res.data.message);
    } catch (err) {
      console.error("AI chat error", err);
    } finally {
      setLoadingAI(false);
    }
  };

  const addAIPulses = (text) => {
    if (!text || text.trim() === "") return;
    // Split by newlines or meaningful markers
    // Dividing into chunks where people usually take a breath
    const chunks = text.split(/\n\n+/).filter(c => c.trim().length > 0);

    chunks.forEach((chunk, i) => {
      setTimeout(() => {
        setMessages((prev) => [...prev, { role: "ai", text: chunk.trim() }]);
      }, i * 2000); // 2 second delay between bubbles
    });
  };

  const handleSpeak = async (text, idx) => {
    // If clicking same message and it's already playing/paused
    if (audioState.idx === idx) {
      if (audioState.playing && audioRef.current) {
        audioRef.current.pause();
        setAudioState(prev => ({ ...prev, playing: false, paused: true }));
      } else if (audioState.paused && audioRef.current) {
        audioRef.current.play();
        setAudioState(prev => ({ ...prev, playing: true, paused: false }));
      }
      return;
    }

    // New message playback
    try {
      if (audioRef.current) {
        audioRef.current.pause();
      }

      setAudioState({ idx, playing: true, paused: false });
      const res = await api.post("/ai/speak", { text });

      if (res.data.success && res.data.audio_base64) {
        const audioSrc = `data:audio/mp3;base64,${res.data.audio_base64}`;
        audioRef.current = new Audio(audioSrc);
        audioRef.current.onended = () => {
          setAudioState({ idx: null, playing: false, paused: false });
        };
        audioRef.current.play();
      } else {
        throw new Error("TTS failed");
      }
    } catch (err) {
      console.error("TTS error", err);
      if (err.response && (err.response.status === 401 || err.response.status === 400)) {
        alert("بسيط صوته تعبان شوية دلوقتي (خلصنا الكريديتس)، تقدر تقرأ الكلام المكتوب! 💜");
      }
      setAudioState({ idx: null, playing: false, paused: false });
    }
  };

  const stopSpeak = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setAudioState({ idx: null, playing: false, paused: false });
  };

  const handleRecord = async () => {
    try {
      setIsRecording(true);
      setLoadingAI(true);
      const res = await api.post("/ai/voice", { session_id: `student_${student.id}_lesson_${lessonId}` });

      if (res.data.success && res.data.transcription) {
        setInput(res.data.transcription);
        // Automatically send the message if desired, or let user review
        // For now, let's just put it in the input so they can edit/confirm
      }
    } catch (err) {
      console.error("STT error", err);
    } finally {
      setIsRecording(false);
      setLoadingAI(false);
    }
  };

  return (
    <div className="lesson-chat">
      <img
        src={require("../../../assets/eyes_baseet.png")}
        alt="Eyes on border"
        className="eyes-border-chat"
      />

      <img
        src={require("../../../assets/crazy_baseet.png")}
        alt="falling Baseet"
        className="floating-asset right-side"
      />

      {/* Header */}
      <div className="lesson-chat-header">
        <div className="header-top">
          <h1>
            <span className="lesson-number">{lesson?.number}</span>{" "}
            {lesson?.title}
          </h1>
          <div className="lesson-progress-container">
            <div className="progress-text">تقدّم الدرس: {lessonProgress}%</div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: `${lessonProgress}%` }}></div>
            </div>
          </div>
        </div>
        <span className="chat-helper">Baseet is here to help 💜</span>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-bubble ${msg.role === "ai" ? "ai" : "user"}`}
          >
            {msg.role === "ai" ? (
              <div className="ai-message-content" dir="rtl">
                <div className="ai-actions">
                  <button
                    className={`btn-icon tts-btn ${audioState.idx === idx && audioState.playing ? "playing" : ""}`}
                    onClick={() => handleSpeak(msg.text, idx)}
                    title={audioState.idx === idx && audioState.playing ? "إيقاف مؤقت" : "استمع"}
                  >
                    {audioState.idx === idx && audioState.playing ? (
                      <Pause size={16} />
                    ) : audioState.idx === idx && audioState.paused ? (
                      <Play size={16} />
                    ) : (
                      <Volume2 size={16} />
                    )}
                  </button>
                  {audioState.idx === idx && (
                    <button
                      className="btn-icon stop-btn"
                      onClick={stopSpeak}
                      title="توقف"
                    >
                      <Square size={14} fill="currentColor" />
                    </button>
                  )}
                </div>
                <div className="ai-text">
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
              </div>
            ) : (
              msg.text
            )}
          </div>
        ))}

        {/* ✅ SHOW THINKING EVEN BEFORE FIRST MESSAGE */}
        {loadingAI && (
          <div className="chat-bubble ai typing">
            Baseet is thinking...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        <textarea
          dir="rtl"
          style={{ textAlign: "right" }}
          placeholder="اكتب إجابتك أو سؤالك هنا ✨"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
        />

        <button
          className={`btn btn-record ${isRecording ? 'recording' : ''}`}
          onClick={handleRecord}
          disabled={loadingAI || isRecording}
          title="سجل صوتك"
        >
          {isRecording ? <Loader2 size={18} className="animate-spin" /> : <Mic size={18} />}
        </button>

        <button
          className="btn btn-primary"
          onClick={sendMessage}
          disabled={loadingAI || isRecording}
        >
          <Send size={18} />
        </button>
      </div>
    </div >
  );
}
