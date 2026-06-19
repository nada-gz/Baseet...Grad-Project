import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import api from "../../../../services/api";
import useAuth from "../../../../hooks/useAuth";
import { Sparkles, ArrowRight, RefreshCcw, Brain } from "lucide-react";
import Manipulatives from "./Manipulatives";
import VisualNumberLine from "./VisualNumberLine";
import StepIndicator from "./StepIndicator";

const NODE_ORDER = ["subitizing", "number_line", "place_value", "fact_retrieval", "word_problems"];

const MathTutor = () => {
  const { user: student } = useAuth();
  const studentId = student?.student_id || student?.id;
  const [session, setSession] = useState(null);
  const [currentProblem, setCurrentProblem] = useState(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [isVictory, setIsVictory] = useState(false);

  // For "Single Demand" flow
  const [currentStep, setCurrentStep] = useState(0); 
  // Step 0: Observe Visual
  // Step 1: Hear/Read Instruction
  // Step 2: Input Answer

  useEffect(() => {
    if (studentId) {
      loadNextProblem();
    }
  }, [studentId]);

  const loadNextProblem = async () => {
    setLoading(true);
    setFeedback(null);
    setUserAnswer("");
    setCurrentStep(0);
    try {
      const res = await api.get(`/api/math/next/${studentId}`);
      
      // Check if finished entire adventure
      if (res.data.mastery.current_node === 'word_problems' && res.data.mastery.word_problems >= 1.0) {
        setIsVictory(true);
      }

      setCurrentProblem(res.data.problem);
      setSession(res.data.mastery);
    } catch (err) {
      console.error("Failed to load math problem:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!userAnswer) return;
    setSubmitting(true);
    try {
      const res = await api.post("/api/math/submit", {
        student_id: studentId,
        answer: parseFloat(userAnswer),
        correct_answer: currentProblem?.answer
      });
      setFeedback(res.data);
      setSession(res.data.updated_mastery);
      
      // Check for victory after submission
      if (res.data.updated_mastery.current_node === 'word_problems' && res.data.updated_mastery.word_problems >= 1.0) {
        setIsVictory(true);
      }
    } catch (err) {
      console.error("Submission failed:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const renderVisualAid = () => {
    if (!currentProblem) return null;
    
    switch (currentProblem.mode) {
      case "manipulatives":
        return <Manipulatives count={currentProblem.data.count} />;
      case "number_line":
        return (
          <VisualNumberLine 
            target={currentProblem.data.target} 
            current={parseFloat(userAnswer) || 0}
            onSelect={(val) => {
              if (currentStep >= 1) setUserAnswer(val.toString());
            }}
            range={currentProblem.data.range}
          />
        );
      case "place_value":
        return (
          <div className="flex gap-4 items-end">
            <Manipulatives count={10} color="#94A3B8" />
            <div className="text-3xl font-bold">+</div>
            <Manipulatives count={currentProblem.data.total - 10} />
          </div>
        );
      default:
        return <div className="p-8 bg-slate-100 rounded-xl text-4xl">🔢</div>;
    }
  };

  if (loading) return <div className="flex items-center justify-center min-h-[400px]">Thinking... ✨</div>;

  const steps = ["بص على الصورة", "افهم السؤال", "جاوب"];

  return (
    <div className="math-tutor-page kid-friendly-vibe p-6" style={styles.container}>
      <header style={styles.header}>
        <div style={{ display: 'flex', flexDirection: 'row-reverse', alignItems: 'center', gap: '20px' }}>
          <div className="bg-indigo-100 p-3 rounded-xl">
            <Brain className="text-indigo-600" size={36} />
          </div>
          <div style={{ textAlign: 'right' }}>
            <h1 style={styles.title}>مغامرة الرياضيات</h1>
            <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: '8px', fontSize: '1.1rem', fontWeight: 'bold', color: '#64748B' }}>
              <span>مستوى</span>
              <span style={{ direction: 'ltr' }}>{session?.current_node || '...'}</span>
            </div>
          </div>
        </div>
        
        <div style={styles.masteryPills}>
          {NODE_ORDER.map(key => {
            const val = session?.[key] || 0;
            return (
              <div key={key} style={styles.pill}>
                <span className="capitalize" style={{ direction: 'ltr', display: 'inline-block' }}>
                  {key.replace('_', ' ')}
                </span>
                <div style={styles.pillBar}>
                  <div style={{...styles.pillFill, width: `${val * 100}%`}} />
                </div>
              </div>
            );
          })}
        </div>
      </header>

      <StepIndicator steps={steps} currentStep={currentStep} />

      <main style={styles.main}>
        <AnimatePresence mode="wait">
          {/* STEP 0: THE VISUAL */}
          {currentStep === 0 && (
            <motion.div 
              key="step0"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center gap-6"
            >
              {renderVisualAid()}
              <div style={{ marginTop: '30px' }}>
                <button 
                  className="btn btn-primary btn-lg flex items-center gap-2"
                  onClick={() => setCurrentStep(1)}
                >
                   <ArrowRight size={20} /> المزيد
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 1: THE QUESTION */}
          {currentStep === 1 && (
            <motion.div 
              key="step1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="flex flex-col items-center gap-8 text-center"
            >
              <div style={styles.questionCard}>
                <h2 style={styles.questionText}>{currentProblem?.question || 'جاري تحميل السؤال...'}</h2>
                {currentProblem?.hint && (
                  <p className="text-indigo-500 font-medium bg-indigo-50 p-3 rounded-lg mt-4">
                    💡 {currentProblem.hint}
                  </p>
                )}
              </div>
              <div style={{ marginTop: '40px' }}>
                <button 
                  className="btn btn-primary btn-lg"
                  onClick={() => setCurrentStep(2)}
                >
                  جاهز أجاوب
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 2: THE INPUT */}
          {currentStep === 2 && (
            <motion.div 
              key="step2"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center gap-8 w-full max-w-md"
            >
              {renderVisualAid()}
              
              {!feedback ? (
                <div className="flex flex-col w-full gap-4">
                  <input
                    type="number"
                    style={styles.input}
                    placeholder="اكتب الرقم هنا..."
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    autoFocus
                  />
                  <div style={{ marginTop: '30px', width: '100%' }}>
                    <button 
                      className="btn btn-primary btn-lg w-full py-4 text-xl"
                      onClick={handleSubmit}
                      disabled={submitting || !userAnswer}
                    >
                      {submitting ? "بيفكر..." : "يلا بينا"}
                    </button>
                  </div>
                </div>
              ) : (
                <motion.div 
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  style={{
                    ...styles.feedbackCard,
                    backgroundColor: feedback.success ? "#F0FDF4" : "#FEF2F2",
                    borderColor: feedback.success ? "#22C55E" : "#EF4444"
                  }}
                >
                  <div className="text-5xl mb-4">{feedback.success ? "🎉" : "💪"}</div>
                  <h3 className="text-2xl font-bold mb-2">{feedback.feedback}</h3>
                  <button 
                    className="btn btn-primary mt-6 flex items-center gap-2"
                    onClick={loadNextProblem}
                  >
                    السؤال ال بعده <RefreshCcw size={18} />
                  </button>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Victory Overlay */}
      {isVictory && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={styles.victoryOverlay}
        >
          <motion.div 
            initial={{ scale: 0.5, y: 50 }}
            animate={{ scale: 1, y: 0 }}
            className="kid-friendly-vibe"
            style={styles.victoryCard}
          >
            <motion.div
              animate={{ 
                y: [0, -40, 0],
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              style={{ marginBottom: '20px' }}
            >
              <img
                src={require("../../../../assets/hi_baseet.png")}
                alt="Celebrating Baseet"
                style={{ width: '180px' }}
              />
            </motion.div>
            
            <h1 style={{ fontSize: '2.5rem', fontWeight: '900', color: '#4F46E5', marginBottom: '1rem' }}>
              ✨ مبروك يا بطل!
            </h1>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1E293B', marginBottom: '2rem' }}>
              أنت خلصت كل مستويات مغامرة الحساب مع بسيط! بنجاح
            </h2>
            
            <p style={{ fontSize: '1.2rem', color: '#64748B', lineHeight: '1.6', marginBottom: '2.5rem', direction: 'rtl' }}>
              بسيط فخور بيك جداً يا شاطر! 💪 أنت دلوقتي بقيت عبقري في الحساب.. يلا بينا نرجع للدروس عشان نكمل باقي المغامرات التعليمية مع بعض.
            </p>

            <button 
              className="btn btn-primary btn-lg"
              style={{ padding: '15px 60px', fontSize: '1.3rem', borderRadius: '20px' }}
              onClick={() => window.history.back()}
            >
             ✨ يلا بينا
            </button>
          </motion.div>
        </motion.div>
      )}

      {/* Floating Asset */}
      <img
        src={require("../../../../assets/hi_baseet.png")}
        alt="Baseet"
        style={styles.baseet}
      />
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "1000px",
    margin: "0 auto",
    minHeight: "80vh",
    position: "relative",
  },
  header: {
    display: "flex",
    flexDirection: "row-reverse",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "30px",
    flexWrap: "wrap",
    gap: "20px"
  },
  title: {
    fontSize: "2rem",
    fontWeight: "900",
    color: "#1E293B",
  },
  masteryPills: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap"
  },
  pill: {
    background: "white",
    padding: "8px 12px",
    borderRadius: "12px",
    fontSize: "0.75rem",
    boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
    width: "120px"
  },
  pillBar: {
    height: "4px",
    background: "#E2E8F0",
    borderRadius: "2px",
    marginTop: "4px",
    overflow: "hidden"
  },
  pillFill: {
    height: "100%",
    background: "#4F46E5",
    transition: "width 0.5s ease"
  },
  main: {
    background: "white",
    borderRadius: "30px",
    padding: "40px",
    boxShadow: "0 10px 25px -5px rgba(0,0,0,0.1)",
    minHeight: "500px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center"
  },
  questionCard: {
    background: "#F1F5F9",
    padding: "30px",
    borderRadius: "20px",
    width: "100%",
    maxWidth: "600px"
  },
  questionText: {
    fontSize: "1.8rem",
    fontWeight: "bold",
    color: "#1E293B",
    direction: "rtl"
  },
  input: {
    width: "100%",
    padding: "20px",
    fontSize: "2rem",
    textAlign: "center",
    borderRadius: "15px",
    border: "3px solid #E2E8F0",
    color: "#4F46E5",
    fontWeight: "bold"
  },
  feedbackCard: {
    padding: "40px",
    borderRadius: "25px",
    border: "4px solid",
    textAlign: "center",
    width: "100%"
  },
  baseet: {
    position: "fixed",
    bottom: "20px",
    right: "20px",
    width: "120px",
    zIndex: 10,
    pointerEvents: "none"
  },
  victoryOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    background: "rgba(99, 102, 241, 0.9)",
    backdropFilter: "blur(10px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    padding: "20px"
  },
  victoryCard: {
    background: "white",
    padding: "50px",
    borderRadius: "40px",
    textAlign: "center",
    maxWidth: "600px",
    width: "100%",
    boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  }
};

export default MathTutor;
