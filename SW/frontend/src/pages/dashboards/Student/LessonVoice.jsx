import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Mic, Volume2, ArrowRight, Loader2 } from "lucide-react";

const LOADING_MESSAGES = [
    "بسيط بيفكر...",
    "بسيط قرب يوصل...",
    "بسيط جاي في الطريق...",
    "لحظة واحدة يا بطل...",
];

export default function LessonVoice() {
    const { lessonId } = useParams();
    const { user: student } = useAuth();
    const navigate = useNavigate();

    const [lesson, setLesson] = useState(null);
    const [status, setStatus] = useState("idle"); // idle, listening, processing, speaking
    const [loadingMsg, setLoadingMsg] = useState(LOADING_MESSAGES[0]);
    const [lessonProgress, setLessonProgress] = useState(0);
    const [responseText, setResponseText] = useState("");
    const [voiceUnavailable, setVoiceUnavailable] = useState(false);

    const audioRef = useRef(null);
    const msgIntervalRef = useRef(null);
    const hasStarted = useRef(false);

    useEffect(() => {
        // Load lesson info
        const loadLesson = async () => {
            try {
                const res = await api.get(`/students/${student.id}/lessons/${lessonId}`);
                setLesson(res.data);

                // Start lesson automatically in Voice mode
                startVoiceInteraction();
            } catch (err) {
                console.error("Failed to load lesson", err);
            }
        };

        if (student && lessonId && !hasStarted.current) {
            hasStarted.current = true;
            loadLesson();
        }

        return () => {
            if (msgIntervalRef.current) clearInterval(msgIntervalRef.current);
            if (audioRef.current) audioRef.current.pause();
        };
    }, [lessonId, student]);

    const startVoiceInteraction = async () => {
        setStatus("processing");
        updateLoadingMessage();

        try {
            const res = await api.post("/ai/interactive-lesson", {
                lesson_id: lessonId,
                student_id: student.id,
                user_input: null, // First call to start
                enable_tts: true,
                enable_stt: false // We just want the initial greeting
            });

            handleAIResponse(res.data);
        } catch (err) {
            console.error("Voice start error", err);
            setStatus("idle");
        }
    };

    const updateLoadingMessage = () => {
        if (msgIntervalRef.current) clearInterval(msgIntervalRef.current);
        let i = 0;
        msgIntervalRef.current = setInterval(() => {
            i = (i + 1) % LOADING_MESSAGES.length;
            setLoadingMsg(LOADING_MESSAGES[i]);
        }, 6000);
    };

    const handleAIResponse = async (data) => {
        if (msgIntervalRef.current) clearInterval(msgIntervalRef.current);

        console.log("Baseet Voice: AI Response received:", data);

        if (data.progress !== undefined) {
            setLessonProgress(data.progress);
        }

        if (data.message && data.message.trim()) {
            const chunks = data.message.split(/\n\n+/).filter(c => c.trim().length > 0);
            console.log("Baseet Voice: Splitting response into pulses:", chunks.length);
            playNextPulse(chunks, 0);
        } else {
            console.log("Baseet Voice: Empty message, skipping TTS.");
            setStatus("listening");
            startListeningLoop();
        }
    };

    const playNextPulse = async (chunks, index) => {
        if (index >= chunks.length) {
            console.log("Baseet Voice: All pulses finished, moving to listening...");
            setStatus("listening");
            startListeningLoop();
            return;
        }

        const chunkText = chunks[index].trim();
        setResponseText(chunkText);
        setStatus("speaking");

        // Friendly error detection: "بسيط بياخد استراحة قصيرة"
        const isFriendlyError = chunkText.includes("بسيط بياخد استراحة قصيرة");

        if (chunkText.startsWith("❌") || isFriendlyError) {
            console.warn("Baseet Voice: Resting/Error message detected, skipping TTS but showing text.");
            setVoiceUnavailable(true);
            finishPulseEarly(chunks, index, chunkText);
            return;
        }

        console.log(`Baseet Voice: Playing pulse ${index + 1}/${chunks.length}:`, chunkText);

        try {
            const speakRes = await api.post("/ai/speak", { text: chunkText });
            if (speakRes.data.success && speakRes.data.audio_base64) {
                setVoiceUnavailable(false);
                const audioSrc = `data:audio/mp3;base64,${speakRes.data.audio_base64}`;
                audioRef.current = new Audio(audioSrc);
                audioRef.current.onended = () => {
                    // Small delay between pulses for natural feel
                    setTimeout(() => playNextPulse(chunks, index + 1), 800);
                };
                audioRef.current.play().catch(e => {
                    console.error("Baseet Voice: Error playing audio pulse:", e);
                    finishPulseEarly(chunks, index, chunkText);
                });
            } else {
                console.warn("Baseet Voice: TTS generation failed for pulse, falling back to reading time.");
                setVoiceUnavailable(true);
                finishPulseEarly(chunks, index, chunkText);
            }
        } catch (err) {
            console.error("Baseet Voice: TTS API error for pulse:", err);
            setVoiceUnavailable(true);
            finishPulseEarly(chunks, index, chunkText);
        }
    };

    const finishPulseEarly = (chunks, index, text = "") => {
        // Calculate reading time per chunk
        const readingTime = Math.max(3000, (text.length / 15) * 1000 + 1500);
        console.log(`Baseet Voice: Finishing pulse early, reading time: ${readingTime}ms`);
        setTimeout(() => {
            playNextPulse(chunks, index + 1);
        }, readingTime);
    };

    const startListeningLoop = async () => {
        // This would ideally be a continuous loop where we listen, send, speak.
        setStatus("listening");

        try {
            // Call the voice recognition endpoint
            const voiceRes = await api.post("/ai/voice", {
                session_id: `student_${student.id}_lesson_${lessonId}`
            });

            if (voiceRes.data.success && voiceRes.data.transcription) {
                setStatus("processing");
                updateLoadingMessage();

                const res = await api.post("/ai/interactive-lesson", {
                    lesson_id: lessonId,
                    student_id: student.id,
                    user_input: voiceRes.data.transcription,
                    enable_tts: true,
                    enable_stt: false
                });
                handleAIResponse(res.data);
            } else {
                // If silent or no transcription, just restart the loop quietly
                console.log("Baseet Voice: Silence detected, listening again...");
                setTimeout(startListeningLoop, 500);
            }
        } catch (err) {
            console.error("Baseet Voice: Listening error:", err);
            // Handle 400 (Silence) gracefully
            if (err.response && err.response.status === 400) {
                console.log("Baseet Voice: Silence/400 error, retrying...");
                setTimeout(startListeningLoop, 1000);
            } else {
                setStatus("idle");
            }
        }
    };

    return (
        <div className="lesson-voice-page underwater">
            <div className="underwater-deco"></div>
            <div className="underwater-rays"></div>

            <div className="hero-blob-container compact" style={{ margin: '20px 40px', width: 'auto' }}>
                <div className="hero-blob-bg" style={{ background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)' }}></div>
                <div className="hero-blob-content">
                    <div className="hero-blob-text">
                        <h1 style={{ fontSize: '2rem', color: 'white' }}>
                           ✨ ! مغامرة الصوت مع بسيط
                        </h1>
                    </div>
                </div>
                <button className="btn-back" onClick={() => navigate(-1)} style={{ position: 'absolute', top: '15px', left: '15px', zIndex: 10 }}>
                    <ArrowRight size={22} />
                    <span>الرجوع</span>
                </button>
            </div>

            <div className="voice-main-content">
                <div className={`baseet-avatar-container ${status}`}>
                    {status !== 'idle' && (
                        <div className="pulse-rings">
                            <div className="ring ring-1"></div>
                            <div className="ring ring-2"></div>
                            <div className="ring ring-3"></div>
                        </div>
                    )}

                    <img
                        src={require(`../../../assets/${status === 'idle' ? 'hii_baseet.png' :
                            status === 'listening' ? 'hi_baseet.png' :
                                status === 'processing' ? 'ask_baseet.png' :
                                    'hi_baseet.png'}`)}
                        alt="Baseet"
                        className={`baseet-voice-img ${status === 'speaking' ? 'bounce' : ''}`}
                    />

                    {status === 'processing' && (
                        <div className="loading-cloud">
                            <p>{loadingMsg}</p>
                        </div>
                    )}
                </div>

                <div className="status-indicator">
                    {status === 'listening' && (
                        <div className="listening-badge">
                            <Mic size={30} className="mic-icon pulse" />
                            <span>بسيط ببيسمعك يا بطل... ✨</span>
                        </div>
                    )}
                    {status === 'speaking' && (
                        <div className="speaking-badge">
                            {voiceUnavailable ? (
                                <>
                                    <Volume2 size={30} className="speaker-icon opacity-50" />
                                    <span style={{ color: 'var(--secondary-text)' }}>بسيط صوته مجهد شوية، اقرأ الكلام! 😴</span>
                                </>
                            ) : (
                                <>
                                    <Volume2 size={30} className="speaker-icon animate-bounce" />
                                    <span>بسيط بيتكلم... ✨</span>
                                </>
                            )}
                        </div>
                    )}
                </div>

                <div className="response-preview-container">
                    {responseText && (
                        <div className="response-card animate-fade-in text-right" dir="rtl">
                            <p>{responseText}</p>
                        </div>
                    )}
                </div>
            </div>
        </div >
    );
}
