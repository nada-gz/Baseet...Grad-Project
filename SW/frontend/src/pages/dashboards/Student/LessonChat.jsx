import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Send } from "lucide-react";

export default function LessonChat() {
  const { lessonId } = useParams();
  const { user: student } = useAuth();

  const [lesson, setLesson] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loadingAI, setLoadingAI] = useState(false);

  const messagesEndRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load lesson + start explanation
  useEffect(() => {
    if (!student) return;

    const startLesson = async () => {
      try {
        const res = await api.get(
          `/students/${student.id}/lessons/${lessonId}`
        );
        setLesson(res.data);

        // Ask backend to start explanation
        const aiRes = await api.post("/ai/lesson/start", {
          lesson_id: lessonId,
          student_id: student.id,
        });

        setMessages([
          {
            role: "ai",
            text: aiRes.data.message,
          },
        ]);
      } catch (err) {
        console.error("Failed to load lesson chat", err);
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

      setMessages((prev) => [
        ...prev,
        { role: "ai", text: res.data.message },
      ]);
    } catch (err) {
      console.error("AI chat error", err);
    } finally {
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

      {/* Right Side Floating Asset */}
      <img
        src={require("../../../assets/crazy_baseet.png")}
        alt="falling Baseet"
        className="floating-asset right-side"
      />

      {/* Header */}
      <div className="lesson-chat-header">
        <h1>
          <span className="lesson-number">{lesson?.number}</span>{" "}
          {lesson?.title}
        </h1>
        <span className="chat-helper">Baseet is here to help 💜</span>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-bubble ${msg.role === "ai" ? "ai" : "user"}`}
          >
            {msg.text}
          </div>
        ))}

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
          placeholder="Type your answer or question here ✨"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />

        <button
          className="btn btn-primary"
          onClick={sendMessage}
          disabled={loadingAI}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
