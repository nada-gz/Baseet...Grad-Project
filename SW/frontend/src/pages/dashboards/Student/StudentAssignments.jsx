import { useEffect, useState, useRef } from "react";
import api from "../../../services/api";
import { API_BASE_URL } from "../../../config";
import useAuth from "../../../hooks/useAuth";
import {
  FileText,
  Image,
  File,
  Lock,
  Eye,
  ChevronDown,
  ChevronRight,
  Frown,
  Upload,
  RefreshCcw,
  Mic,
  Send,
  MessageCircle,
  X,
} from "lucide-react";

const assignmentIcons = {
  pdf: <FileText size={18} />,
  docx: <FileText size={18} />,
  img: <Image size={18} />,
  zip: <File size={18} />,
};

function formatRemaining(deadline) {
  if (!deadline) return "";
  const now = new Date();
  const end = new Date(deadline);
  const diff = end - now;

  const absDiff = Math.abs(diff);
  const days = Math.floor(absDiff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((absDiff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((absDiff / (1000 * 60)) % 60);

  if (diff <= 0) {
    if (days > 0) return `Overdue by ${days} day(s)`;
    if (hours > 0) return `Overdue by ${hours} hour(s)`;
    if (minutes > 0) return `Overdue by ${minutes} minute(s)`;
    return "Due!";
  } else {
    if (days > 0) return `${days} day(s) left`;
    if (hours > 0) return `${hours} hour(s) left`;
    return `${minutes} minute(s) left`;
  }
}

function renderStars(rating) {
  if (!rating) return null;
  const fullStars = "★".repeat(rating);
  const emptyStars = "☆".repeat(5 - rating);
  return (
    <span style={{ color: "#FBBF24", marginLeft: "6px" }}>
      {fullStars}{emptyStars} ({rating}/5)
    </span>
  );
}

export default function StudentAssignments() {
  const { user: student } = useAuth();

  const [milestones, setMilestones] = useState({});
  const [openMilestones, setOpenMilestones] = useState({});
  const [openLessons, setOpenLessons] = useState({});
  const [uploadingFor, setUploadingFor] = useState(null);
  const [files, setFiles] = useState([]);
  const [description, setDescription] = useState("");
  const fileInputsRef = useRef({});

  // Narrative Scaffold State
  const [activeNarrativeId, setActiveNarrativeId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [scaffoldData, setScaffoldData] = useState({
    found: "",
    missing: [],
    next_prompt: "",
    is_complete: false,
    connective_count: 0
  });
  const [scaffoldLoading, setScaffoldLoading] = useState(false);
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [audioBlob, setAudioBlob] = useState(null);

  // Course Filtering
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);

  useEffect(() => {
    const fetchCourses = async () => {
      if (!student?.id) return;
      try {
        const res = await api.get(`/students/${student.id}/assigned-courses`);
        const sortedCourses = res.data.sort((a, b) => {
          const titleA = (a.title || `Course ${a.course_number}`).toLowerCase();
          const titleB = (b.title || `Course ${b.course_number}`).toLowerCase();
          return titleA.localeCompare(titleB);
        });
        setCourses(sortedCourses);
        if (sortedCourses.length > 0) setSelectedCourse(sortedCourses[0].id);
      } catch (err) {
        console.error("Failed to load courses:", err);
      }
    };
    fetchCourses();
  }, [student?.id]);

  useEffect(() => {
    const loadLessonsAssignmentsAndSubmissions = async () => {
      const params = selectedCourse ? { course_id: selectedCourse } : {};
      const res = await api.get(`/students/${student.id}/lessons`, { params });

      const grouped = {};
      const initialOpenMilestones = {};
      const initialOpenLessons = {};

      for (let lesson of res.data) {
        const assRes = await api.get(
          `/students/${student.id}/lessons/${lesson.id}/assignments`
        );
        // Submissions are now included in the assignments response from the backend
        lesson.assignments = assRes.data;

        if (!grouped[lesson.milestone_number]) grouped[lesson.milestone_number] = [];
        grouped[lesson.milestone_number].push(lesson);

        // Expand by default
        initialOpenMilestones[lesson.milestone_number] = true;
        initialOpenLessons[lesson.id] = true;
      }
      setMilestones(grouped);
      setOpenMilestones(initialOpenMilestones);
      setOpenLessons(initialOpenLessons);
    };
    if (student?.id && selectedCourse) loadLessonsAssignmentsAndSubmissions();
  }, [student?.id, selectedCourse]);

  const getLessonStatus = (lesson) => {
    if (lesson.progress === 100) return "completed";
    if (lesson.status === "in-progress") return "in-progress";
    return "locked";
  };

  const [errorMessage, setErrorMessage] = useState(null);

  const submitAssignment = async (assignmentId, selectedFiles, narrativeMetadata = {}) => {
    setErrorMessage(null); // Clear previous errors
    try {
      const formData = new FormData();
      formData.append("description", narrativeMetadata.transcript || description);
      
      if (selectedFiles && selectedFiles.length > 0) {
        selectedFiles.forEach((file) => formData.append("files", file));
      }

      formData.append("submission_method", narrativeMetadata.method || "typed");
      if (narrativeMetadata.story_grammar_score) {
        formData.append("story_grammar_score", narrativeMetadata.story_grammar_score);
      }
      if (narrativeMetadata.causal_connective_count !== undefined) {
        formData.append("causal_connective_count", narrativeMetadata.causal_connective_count);
      }
      
      if (narrativeMetadata.audio) {
        formData.append("audio", narrativeMetadata.audio, `submission_${assignmentId}.webm`);
      }

      // Correct endpoint: /students/{student_id}/assignments/{assignment_id}/submit
      const res = await api.postForm(
        `/students/${student.id}/assignments/${assignmentId}/submit`,
        formData
      );

      // Update state to reflect submission without reload
      setMilestones((prev) => {
        const updated = { ...prev };
        for (const milestoneLessons of Object.values(updated)) {
          for (const lesson of milestoneLessons) {
            const assignment = lesson.assignments.find((a) => a.id === assignmentId);
            if (assignment) assignment.submission = res.data;
          }
        }
        return updated;
      });

      setUploadingFor(null);
      setFiles([]);
      setDescription("");
      alert("Submitted successfully");
    } catch (err) {
      console.error("Submission error:", err);
      const msg = err.response?.data?.detail || "Submission failed";
      setErrorMessage(typeof msg === 'string' ? msg : JSON.stringify(msg));
      setUploadingFor(null); // Stop spinner
    }
  };
  const toggleMilestone = (milestoneNumber) => {
    setOpenMilestones((prev) => ({
      ...prev,
      [milestoneNumber]: !prev[milestoneNumber],
    }));
  };

  const toggleLesson = (lessonId) => {
    setOpenLessons((prev) => ({
      ...prev,
      [lessonId]: !prev[lessonId],
    }));
  };

  const handleUploadClick = (assignmentId) => {
    if (fileInputsRef.current[assignmentId]) {
      fileInputsRef.current[assignmentId].click();
    }
  };

  const handleFileChange = (assignmentId, e) => {
    const selectedFiles = [...e.target.files];
    if (selectedFiles.length === 0) return; // Do not proceed if no files selected

    setUploadingFor(assignmentId);
    setFiles(selectedFiles);
    submitAssignment(assignmentId, selectedFiles);
  };

  // --- NARRATIVE SCAFFOLD LOGIC ---
  const startRecording = (assignmentId) => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setErrorMessage("Oh no! My ears are a bit sleepy right now (Browser doesn't support voice). Can you try typing for me? 😴✨");
      return;
    }

    setActiveNarrativeId(assignmentId);
    setTranscript("");
    setIsRecording(true);

    const recognition = new SpeechRecognition();
    recognition.lang = "ar-SA";
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onresult = (event) => {
      let finalTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      if (finalTranscript) {
        setTranscript(prev => (prev + " " + finalTranscript).trim());
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech error", event.error);
      setIsRecording(false);
      if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
      setErrorMessage("Oh no! My ears are a bit sleepy right now. Can you try again or type for me? 😴✨");
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();

    // Start Audio Recording
    try {
      navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          setAudioBlob(blob);
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
      });
    } catch (err) {
      console.error("MediaRecorder error:", err);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const analyzeNarrative = async (assignmentId) => {
    if (!transcript.trim()) return;
    setScaffoldLoading(true);
    try {
      const res = await api.post("/ai/scaffold/narrative", { text: transcript });
      setScaffoldData(res.data);
      if (res.data.is_complete) {
        // Automatically submit if complete? Or let user confirm?
        // Let's just update the state and show completion.
      }
    } catch (err) {
      console.error("Scaffold error:", err);
    } finally {
      setScaffoldLoading(false);
    }
  };

  const finishNarrativeSubmission = async (assignmentId) => {
    if (!window.confirm("Ready to send your story to Baseet and your teacher? ✨")) return;
    
    setUploadingFor(assignmentId);
    setScaffoldLoading(true);

    let finalScaffoldData = scaffoldData;

    // Perform one LAST analysis to make sure we capture everything added in the final recording/edit
    try {
      if (transcript.trim()) {
        const res = await api.post("/ai/scaffold/narrative", { text: transcript });
        finalScaffoldData = res.data;
      }
    } catch (err) {
      console.error("Final analysis error:", err);
      // Fallback to existing scaffoldData if final one fails
    }

    await submitAssignment(assignmentId, [], {
      method: "voice",
      transcript: transcript,
      story_grammar_score: finalScaffoldData.found,
      causal_connective_count: finalScaffoldData.connective_count,
      audio: audioBlob
    });

    // Reset scaffold state
    setActiveNarrativeId(null);
    setTranscript("");
    setAudioBlob(null);
    setScaffoldData({ found: "", missing: [], next_prompt: "", is_complete: false, connective_count: 0 });
    setScaffoldLoading(false);
  };

  return (
    <div className="student-assignments-page kid-friendly-vibe">
      <div className="hero-blob-container assignments-style" style={{ borderColor: '#E0E7FF', boxShadow: '0 12px 0 #E0E7FF' }}>
        <div className="hero-blob-bg" style={{ background: 'radial-gradient(circle, #F1F4FF 0%, #E0E7FF 100%)' }}></div>
        <div className="hero-blob-content">
          <div className="hero-blob-image-wrapper shift-right">
            <img
              src={require("../../../assets/hi_baseet.png")}
              alt="Hi Baseet"
              className="hero-blob-img"
            />
          </div>
          <div className="hero-blob-text">
            <h1 style={{ color: '#6C63FF' }}>🏆 ! تحدي الأبطال </h1>
            <p>ورينا شطارتك وحل المهمات عشان تجمع النجوم</p>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="error-bubble-container">
          <div className="error-bubble">
            <span className="error-icon">⚠️</span>
            <p>{errorMessage}</p>
            <button className="close-error" onClick={() => setErrorMessage(null)}>×</button>
          </div>
        </div>
      )}

      {courses.length === 0 ? (
        <div className="empty-milestones">
          <p>لسه مفيش كورسات.. بسيط مستنيك!</p>
        </div>
      ) : (
        <>
          {/* Course Filter */}
          <div className="course-filter-section" style={{ marginBottom: "2rem" }}>
            <div className="flex items-center gap-4">
              <select
                className="kid-select"
                value={selectedCourse || ""}
                onChange={(e) => setSelectedCourse(Number(e.target.value) || null)}
              >
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.title || `Course ${course.course_number}`}
                  </option>
                ))}
              </select>
              <span className="filter-label" style={{ fontWeight: 800, fontSize: "1.1rem" }}>: اختر الكورس</span>
            </div>
          </div>

          {Object.keys(milestones).length === 0 ? (
            <div className="empty-milestones mt-4">
              <p>لسه مفيش مهمات موجودة.. بسيط مستنيك!</p>
            </div>
          ) : (
            <div className="milestones-container">
              {Object.entries(milestones)
                .sort(([a], [b]) => Number(a) - Number(b))
                .map(([milestoneNumberStr, lessons]) => {
                  const milestoneNumber = Number(milestoneNumberStr);
                  return (
                    <div key={milestoneNumber} className="milestone-island">
                      <div className="milestone-header-kid">
                        <div className="milestone-badge">مرحلة {milestoneNumber}</div>
                        <h2 className="milestone-title">المرحلة {milestoneNumber}</h2>
                      </div>

                      <div className="lesson-assignments-container">
                        {lessons.map((lesson) => {
                          const status = getLessonStatus(lesson);
                          const isOpen = openLessons[lesson.id];

                          return (
                            <div key={lesson.id} className={`lesson-assignment-block ${status}`}>
                              <div
                                className="lesson-header-pill"
                                onClick={() => toggleLesson(lesson.id)}
                              >
                                <div className="lesson-pill-info">
                                  <div className="lesson-pill-icon">
                                    {isOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                                  </div>
                                  <span>درس {lesson.lesson_number}: {lesson.title}</span>
                                </div>
                                {status === "locked" && <Lock size={18} className="text-secondary-text" />}
                              </div>

                              {isOpen && (
                                <div className="assignments-bubbles-container">
                                  {lesson.assignments?.length > 0 ? (
                                    lesson.assignments.map((assignment) => (
                                      <div key={assignment.id} className="assignment-bubble-wrapper">
                                        <div className="assignment-bubble">
                                          <div className="assignment-bubble-main">
                                            <div className="assignment-bubble-icon">
                                              {status === "locked" ? (
                                                <Lock size={24} />
                                              ) : (
                                                assignmentIcons[assignment.assignment_type] || <File size={24} />
                                              )}
                                            </div>
                                            <div className="assignment-bubble-text">
                                              <h4>{assignment.title}</h4>
                                              {assignment.deadline && !assignment.submission && (
                                                <div className="deadline-pill">
                                                  ⏱️ {formatRemaining(assignment.deadline)}
                                                </div>
                                              )}
                                            </div>
                                          </div>

                                          <div className="assignment-bubble-actions">
                                            {status !== "locked" && (
                                              <>
                                                {/* View Files */}
                                                {(assignment.files || []).map((f) => (
                                                  <a
                                                    key={f.id}
                                                    href={`${API_BASE_URL}${f.file_url}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="btn-circle-action"
                                                    title="View"
                                                  >
                                                    <Eye size={18} />
                                                  </a>
                                                ))}

                                                {/* Mic Button for Narrative */}
                                                {assignment.assignment_type === "narrative" && !assignment.submission && (
                                                  <button
                                                    className="btn-circle-action mic-button-special"
                                                    onClick={() => startRecording(assignment.id)}
                                                    title="Talk to Baseet"
                                                    style={{ backgroundColor: "#FF6B6B", color: "white" }}
                                                  >
                                                    <Mic size={18} />
                                                  </button>
                                                )}

                                                {/* Upload/Resubmit File */}
                                                <button
                                                  className={`btn-circle-action ${assignment.submission ? 'resubmit' : 'upload'}`}
                                                  onClick={() => handleUploadClick(assignment.id)}
                                                  title={assignment.submission ? "Resubmit File" : "Upload File"}
                                                >
                                                  {assignment.submission ? <RefreshCcw size={18} /> : <Upload size={18} />}
                                                </button>

                                                {/* Re-record Option for Narrative */}
                                                {assignment.assignment_type === "narrative" && assignment.submission && (
                                                  <button
                                                    className="btn-circle-action mic-button-special"
                                                    onClick={() => startRecording(assignment.id)}
                                                    title="Re-record Story"
                                                    style={{ backgroundColor: "#FF6B6B", color: "white" }}
                                                  >
                                                    <Mic size={18} />
                                                  </button>
                                                )}
                                              </>
                                            )}
                                          </div>

                                          <input
                                            type="file"
                                            multiple
                                            style={{ display: "none" }}
                                            ref={(el) => (fileInputsRef.current[assignment.id] = el)}
                                            onChange={(e) => handleFileChange(assignment.id, e)}
                                          />
                                        </div>

                                        {/* --- NARRATIVE SCAFFOLD OVERLAY --- */}
                                        {activeNarrativeId === assignment.id && (
                                          <div className="narrative-scaffold-overlay">
                                            <div className="scaffold-card">
                                              <div className="scaffold-header">
                                                <h3><MessageCircle size={20} /> مساعد بسيط الذكي</h3>
                                                <button onClick={() => setActiveNarrativeId(null)} className="close-btn"><X size={20} /></button>
                                              </div>
                                              
                                              <div className="scaffold-content">
                                                {isRecording ? (
                                                  <div className="recording-status">
                                                    <div className="pulse-mic"><Mic size={40} /></div>
                                                    <p>بسيط بيسمعك دلوقتي... اتكلم يا بطل!</p>
                                                    <button className="btn btn-stop" onClick={stopRecording}>خلصت كلام 👋</button>
                                                  </div>
                                                ) : (
                                                  <>
                                                    <div className="transcript-box scrollable-transcript">
                                                      <p className="label">حكايتك:</p>
                                                      <div className="text-content">
                                                        {transcript || "مستني اسمع حكايتك..."}
                                                      </div>
                                                    </div>

                                                    {scaffoldData.next_prompt && (
                                                      <div className="ai-prompt-bubble">
                                                        <div className="avatar">🤖</div>
                                                        <div className="message">{scaffoldData.next_prompt}</div>
                                                      </div>
                                                    )}

                                                    <div className="scaffold-actions">
                                                      <button 
                                                        className="btn btn-mic-again" 
                                                        onClick={() => startRecording(assignment.id)}
                                                      >
                                                        <Mic size={18} /> اتكلم تاني
                                                      </button>
                                                      
                                                      {transcript && (
                                                        <button 
                                                          className="btn btn-analyze" 
                                                          onClick={() => analyzeNarrative(assignment.id)}
                                                          disabled={scaffoldLoading}
                                                        >
                                                          {scaffoldLoading ? "بفكر..." : "بص كدة يا بسيط ✨"}
                                                        </button>
                                                      )}

                                                      {transcript && (
                                                        <button 
                                                          className="btn btn-submit-narrative" 
                                                          onClick={() => finishNarrativeSubmission(assignment.id)}
                                                        >
                                                          <Send size={18} /> {scaffoldData.is_complete ? "ابعت الواجب" : "خلصت حكايتي"}
                                                        </button>
                                                      )}
                                                    </div>
                                                  </>
                                                )}
                                              </div>
                                            </div>
                                          </div>
                                        )}

                                        {/* Status & Feedback */}
                                        {assignment.submission && (
                                          <div className="submission-card-kid">
                                            <div className="submission-header">
                                              <span className={`status-badge-kid ${assignment.submission.status}`}>
                                                {assignment.submission.status === 'evaluated' ? 'تم التقييم ✨' :
                                                  assignment.submission.status === 'resubmitted' ? 'تم الإرسال مرة أخرى 🚀' :
                                                    assignment.submission.status === 'submitted' ? 'تم الإرسال 👍' : 'لم يتم الإرسال'}
                                              </span>
                                              {assignment.deadline && (
                                                <span className="deadline-text">آخر موعد: {new Date(assignment.deadline).toLocaleDateString()}</span>
                                              )}
                                            </div>

                                            {assignment.submission.feedback && (
                                              <div className="baseet-feedback-speech">
                                                <div className="baseet-mini-avatar">
                                                  <img src={require("../../../assets/hii_baseet.png")} alt="Baseet" />
                                                </div>
                                                <div className="speech-bubble">
                                                  <div className="speech-content">
                                                    <p>{assignment.submission.feedback.comment}</p>
                                                    {assignment.submission.feedback.rating && (
                                                      <div className="stars-kid">
                                                        {"⭐".repeat(assignment.submission.feedback.rating)}
                                                      </div>
                                                    )}
                                                  </div>
                                                </div>
                                              </div>
                                            )}
                                          </div>
                                        )}
                                      </div>
                                    ))
                                  ) : (
                                    <div className="empty-bubble">مفيش مهمات موجودة حالياً 😅</div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
