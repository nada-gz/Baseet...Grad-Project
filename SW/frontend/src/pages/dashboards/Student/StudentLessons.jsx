import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Lock, RotateCcw, Play } from "lucide-react";

export default function StudentLessons() {
  const { user: student } = useAuth();
  const navigate = useNavigate();

  const [milestones, setMilestones] = useState([]);
  const [confirmLesson, setConfirmLesson] = useState(null);

  useEffect(() => {
    const loadLessons = async () => {
      const res = await api.get(`/students/${student.id}/lessons`);
      setMilestones(groupByMilestone(res.data));
    };
    if (student) loadLessons();
  }, [student]);

  const groupByMilestone = (lessons) => {
    const grouped = {};
    lessons.forEach((l) => {
      if (!grouped[l.milestone_id]) grouped[l.milestone_id] = [];
      grouped[l.milestone_id].push(l);
    });
    return grouped;
  };

  const resetLesson = async (lessonId) => {
    try {
      const payload = {
        progress: 0,
        status: "in-progress"
      };
  
      const response = await api.patch(
        `/students/${student.id}/lessons/${lessonId}`,
        payload
      );
  
      console.log("Lesson reset:", response.data);
  
      setConfirmLesson(null);
      navigate(`/dashboard/student/lesson/${lessonId}`);
    } catch (err) {
      console.error("Failed to reset lesson", err);
    }
  };  
  
  return (
    <div className="student-lessons-page">
      {Object.entries(milestones).map(([milestoneId, lessons]) => (
        <div key={milestoneId} className="milestone-section">
          <h2 className="milestone-title">Milestone {milestoneId}</h2>

          <div className="lesson-list">
            {lessons.map((lesson) => (
              <div
                key={lesson.id}
                className={`lesson-card ${lesson.status}`}
              >
                <div className="lesson-info">
                  <h3 className="lesson-title">
                    {lesson.milestone_id}.{lesson.id} {lesson.title}
                  </h3>
                  <p className="lesson-desc">{lesson.description}</p>

                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${lesson.progress}%` }}
                    />
                  </div>

                  <span className={`lesson-status ${lesson.status}`}>
                    {lesson.status.replace("-", " ")}
                  </span>
                </div>

                {/* ACTIONS */}
                <div className="lesson-actions">
                  {lesson.status === "completed" && (
                    <button
                      className="btn btn-outline"
                      onClick={() => setConfirmLesson(lesson)}
                    >
                      <RotateCcw size={18} /> Retake
                    </button>
                  )}

                  {lesson.status === "in-progress" && (
                    <>
                      <button
                        className="btn btn-primary"
                        onClick={() =>
                          navigate(`/dashboard/student/lesson/${lesson.id}`)
                        }
                      >
                        <Play size={18} /> Continue
                      </button>
                      <button
                        className="btn btn-outline"
                        onClick={() => setConfirmLesson(lesson)}
                      >
                        Restart
                      </button>

                    </>
                  )}

                  {lesson.status === "locked" && (
                    <div className="locked-icon">
                      <Lock size={24} />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* CONFIRM MODAL */}
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
    </div>
  );
}
