import { useState, useEffect, useRef, useCallback } from "react";
import useAuth from "../../../hooks/useAuth";
import api from "../../../services/api";

const GREETING = "ايه الأخبار .. محتاج ايه وأنا أساعدك يا بطل 🌟";
const LETTER_SPEED = 45; // ms per character

/* ─────────────────────────── Stars ─────────────────────────── */
const STARS = Array.from({ length: 60 }, (_, i) => ({
  id: i,
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 2.5 + 1,
  opacity: Math.random() * 0.7 + 0.2,
  delay: Math.random() * 3,
}));

/* ─────────────────────────── Styles ─────────────────────────── */
const S = {
  page: {
    display: "flex",
    height: "calc(100vh - 120px)",
    overflow: "hidden",
    fontFamily: "'Segoe UI', 'Cairo', Arial, sans-serif",
    borderRadius: 20,
    boxShadow: "0 8px 60px rgba(108,99,255,0.25)",
  },

  /* LEFT PANEL */
  left: {
    width: "38%",
    background: "linear-gradient(160deg, #130025 0%, #0a0018 60%, #0d001f 100%)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "30px 24px 0",
    position: "relative",
    overflow: "hidden",
    flexShrink: 0,
  },
  leftHeader: {
    position: "absolute",
    top: 24,
    left: 0,
    right: 0,
    textAlign: "center",
    zIndex: 2,
  },
  leftTitle: {
    fontSize: "1.05rem",
    fontWeight: 700,
    color: "#c4b5fd",
    letterSpacing: 2,
    textTransform: "uppercase",
  },
  leftDot: {
    display: "inline-block",
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "#6C63FF",
    margin: "0 4px",
    boxShadow: "0 0 8px #6C63FF",
  },
  baseetWrap: {
    position: "relative",
    zIndex: 2,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  baseetImg: {
    width: 240,
    height: "auto",
    animation: "baseetFloat 3.5s ease-in-out infinite",
    filter: "drop-shadow(0 12px 30px rgba(108,99,255,0.5))",
    userSelect: "none",
  },
  bubbleWrap: {
    position: "absolute",
    top: -50,
    right: "-30%",
    zIndex: 10,
    width: 220,
  },
  bubble: {
    background: "#ffffff",
    borderRadius: "18px 18px 18px 4px",
    padding: "14px 18px",
    boxShadow: "0 8px 30px rgba(108,99,255,0.3)",
    position: "relative",
    minHeight: 60,
  },
  bubbleTriangle: {
    position: "absolute",
    bottom: 16,
    left: -12,
    width: 0,
    height: 0,
    borderTop: "10px solid transparent",
    borderBottom: "10px solid transparent",
    borderRight: "12px solid #ffffff",
  },
  bubbleText: {
    fontSize: "0.92rem",
    color: "#1A0533",
    lineHeight: 1.6,
    direction: "rtl",
    textAlign: "right",
    fontWeight: 600,
    minHeight: 24,
  },
  cursor: {
    display: "inline-block",
    width: 2,
    height: "1em",
    background: "#6C63FF",
    marginLeft: 2,
    verticalAlign: "middle",
    animation: "blinkCursor 0.8s step-end infinite",
  },

  /* RIGHT PANEL */
  right: {
    flex: 1,
    background: "#0f0f1a",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    borderLeft: "1px solid rgba(108,99,255,0.15)",
  },
  rightHeader: {
    padding: "18px 24px 14px",
    borderBottom: "1px solid rgba(108,99,255,0.12)",
    display: "flex",
    alignItems: "center",
    gap: 12,
    background: "rgba(108,99,255,0.05)",
    flexShrink: 0,
  },
  rightHeaderAvatar: {
    width: 38,
    height: 38,
    borderRadius: "50%",
    border: "2px solid #6C63FF",
    background: "#1e1b3a",
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  rightHeaderInfo: {
    flex: 1,
  },
  rightHeaderName: {
    fontSize: "0.95rem",
    fontWeight: 700,
    color: "#e2e0ff",
  },
  rightHeaderStatus: {
    fontSize: "0.75rem",
    color: "#6C63FF",
    display: "flex",
    alignItems: "center",
    gap: 5,
  },
  onlineDot: {
    width: 7,
    height: 7,
    borderRadius: "50%",
    background: "#4ade80",
    boxShadow: "0 0 6px #4ade80",
  },

  /* MESSAGES */
  messagesArea: {
    flex: 1,
    overflowY: "auto",
    padding: "24px 20px",
    display: "flex",
    flexDirection: "column",
    gap: 18,
    scrollbarWidth: "thin",
    scrollbarColor: "rgba(108,99,255,0.3) transparent",
  },
  msgRow: (role) => ({
    display: "flex",
    flexDirection: role === "user" ? "row-reverse" : "row",
    alignItems: "flex-end",
    gap: 10,
    animation: "fadeSlideIn 0.35s ease",
  }),
  msgAvatar: {
    width: 32,
    height: 32,
    borderRadius: "50%",
    flexShrink: 0,
    overflow: "hidden",
    border: "2px solid rgba(108,99,255,0.4)",
  },
  bubble_ai: {
    maxWidth: "72%",
    background: "#1e1b3a",
    border: "1px solid rgba(108,99,255,0.25)",
    borderRadius: "18px 18px 18px 4px",
    padding: "13px 17px",
    color: "#e2e0ff",
    fontSize: "0.93rem",
    lineHeight: 1.7,
    direction: "rtl",
    textAlign: "right",
    wordBreak: "break-word",
    boxShadow: "0 4px 20px rgba(108,99,255,0.12)",
  },
  bubble_user: {
    maxWidth: "72%",
    background: "linear-gradient(135deg, #6C63FF 0%, #9f7aea 100%)",
    borderRadius: "18px 18px 4px 18px",
    padding: "13px 17px",
    color: "#fff",
    fontSize: "0.93rem",
    lineHeight: 1.7,
    direction: "rtl",
    textAlign: "right",
    wordBreak: "break-word",
    boxShadow: "0 4px 20px rgba(108,99,255,0.3)",
  },

  /* TYPING INDICATOR */
  typingRow: {
    display: "flex",
    alignItems: "flex-end",
    gap: 10,
    animation: "fadeSlideIn 0.3s ease",
  },
  typingBubble: {
    background: "#1e1b3a",
    border: "1px solid rgba(108,99,255,0.25)",
    borderRadius: "18px 18px 18px 4px",
    padding: "14px 20px",
    display: "flex",
    alignItems: "center",
    gap: 6,
  },
  dot: (i) => ({
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "#6C63FF",
    animation: `typingDot 1.2s ease-in-out ${i * 0.2}s infinite`,
  }),

  /* INPUT */
  inputArea: {
    padding: "16px 20px",
    borderTop: "1px solid rgba(108,99,255,0.12)",
    background: "#0f0f1a",
    flexShrink: 0,
  },
  inputRow: {
    display: "flex",
    gap: 10,
    alignItems: "flex-end",
    background: "#1a1a2e",
    border: "1.5px solid rgba(108,99,255,0.3)",
    borderRadius: 16,
    padding: "8px 12px",
    transition: "border-color 0.2s",
  },
  textarea: {
    flex: 1,
    background: "transparent",
    border: "none",
    outline: "none",
    resize: "none",
    color: "#e2e0ff",
    fontSize: "0.93rem",
    lineHeight: 1.6,
    direction: "rtl",
    textAlign: "right",
    fontFamily: "'Segoe UI', 'Cairo', Arial, sans-serif",
    minHeight: 22,
    maxHeight: 120,
    padding: "4px 0",
  },
  sendBtn: (active) => ({
    width: 40,
    height: 40,
    borderRadius: "50%",
    border: "none",
    cursor: active ? "pointer" : "not-allowed",
    background: active
      ? "linear-gradient(135deg, #6C63FF 0%, #FF006E 100%)"
      : "rgba(108,99,255,0.15)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "1.1rem",
    transition: "all 0.2s",
    flexShrink: 0,
    transform: active ? "scale(1)" : "scale(0.9)",
    boxShadow: active ? "0 4px 16px rgba(108,99,255,0.4)" : "none",
  }),
  emptyState: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    color: "rgba(196,181,253,0.35)",
    textAlign: "center",
    gap: 12,
    padding: 40,
  },
  emptyIcon: {
    fontSize: "3.5rem",
    opacity: 0.4,
  },
  emptyText: {
    fontSize: "0.95rem",
    lineHeight: 1.6,
    direction: "rtl",
    maxWidth: 260,
  },
};

/* ─────────────────────────── Component ─────────────────────────── */
export default function AskBaseet() {
  const { user: student } = useAuth();
  const studentId = student?.student_id || student?.id;

  const [messages, setMessages] = useState([]);      // { id, role, text }
  const [revealed, setRevealed] = useState({});      // { [id]: visibleLength }
  const [greetingText, setGreetingText] = useState("");
  const [greetingDone, setGreetingDone] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const msgCounter = useRef(0);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  /* Auto-scroll */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, revealed]);

  /* Greeting typewriter on mount */
  useEffect(() => {
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setGreetingText(GREETING.slice(0, i));
      if (i >= GREETING.length) {
        clearInterval(iv);
        setGreetingDone(true);
      }
    }, LETTER_SPEED);
    return () => clearInterval(iv);
  }, []);

  /* Typewriter for any AI message */
  const animateMessage = useCallback((id, text) => {
    let i = 0;
    setRevealed((prev) => ({ ...prev, [id]: 0 }));
    const iv = setInterval(() => {
      i++;
      setRevealed((prev) => ({ ...prev, [id]: i }));
      if (i >= text.length) clearInterval(iv);
    }, LETTER_SPEED);
  }, []);

  /* Send message */
  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const uid = ++msgCounter.current;
    setMessages((prev) => [...prev, { id: uid, role: "user", text: trimmed }]);
    setInput("");
    setIsLoading(true);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    try {
      const res = await api.post("/ai/general-chat", {
        student_id: studentId,
        message: trimmed,
      });
      const reply = res.data.reply || "آسف، مش قادر أرد دلوقتي 😅";
      const aid = ++msgCounter.current;
      setMessages((prev) => [...prev, { id: aid, role: "baseet", text: reply }]);
      animateMessage(aid, reply);
    } catch (err) {
      const eid = ++msgCounter.current;
      const errText = "حصل مشكلة صغيرة.. حاول تاني بعد شوية! 🙈";
      setMessages((prev) => [...prev, { id: eid, role: "baseet", text: errText }]);
      animateMessage(eid, errText);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  const canSend = input.trim().length > 0 && !isLoading;

  return (
    <>
      {/* Keyframe animations */}
      <style>{`
        @keyframes baseetFloat {
          0%, 100% { transform: translateY(0px); }
          50%       { transform: translateY(-14px); }
        }
        @keyframes blinkCursor {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0; }
        }
        @keyframes typingDot {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30%            { transform: translateY(-8px); opacity: 1; }
        }
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes starTwinkle {
          0%, 100% { opacity: 0.2; }
          50%       { opacity: 0.9; }
        }
        .ask-messages-area::-webkit-scrollbar { width: 4px; }
        .ask-messages-area::-webkit-scrollbar-thumb { background: rgba(108,99,255,0.35); border-radius: 4px; }
        .ask-send-btn:hover { filter: brightness(1.15); transform: scale(1.08) !important; }
        .ask-input-row:focus-within { border-color: rgba(108,99,255,0.7) !important; box-shadow: 0 0 0 3px rgba(108,99,255,0.12); }
      `}</style>

      <div style={S.page}>
        {/* ──── LEFT PANEL ──── */}
        <div style={S.left}>
          {/* Stars background */}
          {STARS.map((s) => (
            <span
              key={s.id}
              style={{
                position: "absolute",
                top: s.top,
                left: s.left,
                width: s.size,
                height: s.size,
                borderRadius: "50%",
                background: "#fff",
                opacity: s.opacity,
                animation: `starTwinkle ${2 + s.delay}s ease-in-out ${s.delay}s infinite`,
              }}
            />
          ))}

          {/* Header label */}
          <div style={S.leftHeader}>
            <div style={S.leftTitle}>
              <span style={S.leftDot} />
              اسأل بسيط
              <span style={S.leftDot} />
            </div>
          </div>

          {/* Baseet + speech bubble */}
          <div style={S.baseetWrap}>
            {/* Speech bubble
            <div style={S.bubbleWrap}>
              <div style={S.bubble}>
                <div style={S.bubbleTriangle} />
                <p style={S.bubbleText}>
                  {greetingText}
                  {!greetingDone && <span style={S.cursor} />}
                </p>
              </div>
            </div> */}

            {/* Main Baseet image */}
            <img
              src={require("../../../assets/BASEET-smiling.png")}
              alt="Baseet"
              style={S.baseetImg}
              draggable={false}
            />
          </div>
        </div>

        {/* ──── RIGHT PANEL ──── */}
        <div style={S.right}>
          {/* Right header */}
          <div style={S.rightHeader}>
            <div style={S.rightHeaderAvatar}>
              <img
                src={require("../../../assets/ask_baseet.png")}
                alt="Baseet"
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            </div>
            <div style={S.rightHeaderInfo}>
              <div style={S.rightHeaderName}> بسيط </div>
              <div style={S.rightHeaderStatus}>
                <span style={S.onlineDot} />
                  مستعد يساعدك في أي وقت 
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="ask-messages-area" style={S.messagesArea}>
            {messages.length === 0 && !isLoading && (
              <div style={S.emptyState}>
                <div style={S.emptyIcon}>💬</div>
                <div style={S.emptyText}>
                  ابدأ المحادثة مع بسيط!
                  <br />
                  اسأله عن أي حاجة في العلوم، الرياضيات، أو أي فضول عندك ✨
                </div>
              </div>
            )}

            {messages.map((msg) => {
              const isBaseet = msg.role === "baseet";
              const visLen = revealed[msg.id];
              const displayText =
                isBaseet && visLen !== undefined && visLen < msg.text.length
                  ? msg.text.slice(0, visLen)
                  : msg.text;

              return (
                <div key={msg.id} style={S.msgRow(msg.role)}>
                  {isBaseet && (
                    <div style={S.msgAvatar}>
                      <img
                        src={require("../../../assets/ask_baseet.png")}
                        alt="Baseet"
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                    </div>
                  )}
                  <div style={isBaseet ? S.bubble_ai : S.bubble_user}>
                    {displayText}
                    {isBaseet &&
                      visLen !== undefined &&
                      visLen < msg.text.length && (
                        <span style={S.cursor} />
                      )}
                  </div>
                </div>
              );
            })}

            {/* Typing indicator */}
            {isLoading && (
              <div style={S.typingRow}>
                <div style={S.msgAvatar}>
                  <img
                    src={require("../../../assets/BASEET-smiling-hat.png")}
                    alt="Baseet thinking"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                </div>
                <div style={S.typingBubble}>
                  {[0, 1, 2].map((i) => (
                    <span key={i} style={S.dot(i)} />
                  ))}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div style={S.inputArea}>
            <div className="ask-input-row" style={S.inputRow}>
              <textarea
                ref={textareaRef}
                style={S.textarea}
                placeholder="اسأل بسيط أي حاجة..."
                value={input}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                rows={1}
                dir="rtl"
              />
              <button
                className="ask-send-btn"
                style={S.sendBtn(canSend)}
                onClick={sendMessage}
                disabled={!canSend}
                title="إرسال"
              >
                ✈
              </button>
            </div>
            <div
              style={{
                textAlign: "center",
                marginTop: 8,
                fontSize: "0.72rem",
                color: "rgba(196,181,253,0.3)",
              }}
            >
              اضغط Enter للإرسال • Shift+Enter لسطر جديد
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
