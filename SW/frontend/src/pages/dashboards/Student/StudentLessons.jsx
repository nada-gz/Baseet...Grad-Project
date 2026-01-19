import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Lock, RotateCcw, Play } from "lucide-react";

export default function StudentLessons() {
  const { user: student } = useAuth();
  const { courseId } = useParams();
  const navigate = useNavigate();

  const [milestones, setMilestones] = useState({});
  const [confirmLesson, setConfirmLesson] = useState(null);

  const groupByMilestone = (lessons) => {
    const grouped = {};
    lessons.forEach((lesson) => {
      const key = lesson.milestone_number;
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(lesson);
    });
    Object.values(grouped).forEach(list =>
      list.sort((a, b) => a.lesson_number - b.lesson_number)
    );
    return grouped;
  };

  const loadLessons = async () => {
    if (!student?.id || !courseId) return;
    try {
      const res = await api.get(`/students/${student.id}/lessons`, {
        params: { course_id: courseId }
      });
      const grouped = groupByMilestone(res.data);
      setMilestones(grouped);
    } catch (err) {
      console.error("Failed to load lessons:", err);
    }
  };

  useEffect(() => {
    loadLessons();
  }, [student?.id, courseId]);

  const resetLesson = async (lessonId) => {
    try {
      await api.patch(`/students/${student.id}/lessons/${lessonId}`, {
        progress: 0
      });
      setConfirmLesson(null);
      // reload lessons
      loadLessons();
    } catch (err) {
      console.error("Failed to reset lesson:", err);
    }
  };

  return (
    <div className="student-lessons-page">
      {Object.keys(milestones).length === 0 ? (
        <div className="text-center p-10 bg-white rounded-lg border border-dashed border-slate-300">
          <p className="text-slate-500">No milestones assigned yet for this course.</p>
        </div>
      ) : (
        Object.entries(milestones)
          .sort(([a], [b]) => Number(a) - Number(b))
          .map(([milestoneNumberStr, lessons]) => {
            const milestoneNumber = Number(milestoneNumberStr);
            return (
              <div key={milestoneNumber} className="milestone-section">
                <h2 className="milestone-title">Milestone {milestoneNumber}</h2>

                <div className="lesson-list">
                  {lessons.map((lesson) => {
                    const status = lesson.status;

                    return (
                      <div key={lesson.id} className={`lesson-card ${status}`}>
                        <div className="lesson-info">
                          <h3 className="lesson-title">
                            {lesson.number} {lesson.title}
                          </h3>
                          <p className="lesson-desc">{lesson.description}</p>

                          <div className="progress-bar">
                            <div
                              className="progress-fill"
                              style={{ width: `${lesson.progress}%` }}
                            />
                          </div>

                          <span className={`lesson-status ${status}`}>
                            {status.replace("-", " ")}
                          </span>
                        </div>

                        <div className="lesson-actions">
                          {status === "completed" && (
                            <button
                              className="btn btn-outline"
                              onClick={() => setConfirmLesson(lesson)}
                            >
                              <RotateCcw size={18} /> Retake
                            </button>
                          )}

                          {status === "in-progress" && (
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

                          {status === "locked" && <Lock size={24} />}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })
      )}

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
