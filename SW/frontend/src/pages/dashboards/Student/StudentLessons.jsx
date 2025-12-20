import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import { Lock, RotateCcw, Play } from "lucide-react";

export default function StudentLessons() {
  const { user: student } = useAuth();
  const navigate = useNavigate();

  const getInitialUnlocked = () => {
    // load from localStorage if exists, else unlock milestone 1
    const saved = localStorage.getItem("unlockedMilestones");
    if (saved) return new Set(JSON.parse(saved));
    return new Set([1]);
  };

  const [milestones, setMilestones] = useState({});
  const [confirmLesson, setConfirmLesson] = useState(null);
  const [unlockedMilestones, setUnlockedMilestones] = useState(getInitialUnlocked);

  // persist unlocked milestones whenever it changes
  useEffect(() => {
    localStorage.setItem(
      "unlockedMilestones",
      JSON.stringify(Array.from(unlockedMilestones))
    );
  }, [unlockedMilestones]);

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
    try {
      const res = await api.get(`/students/${student.id}/lessons`);
      const grouped = groupByMilestone(res.data);
      setMilestones(grouped);

      // unlock new milestones if previous milestone fully completed
      setUnlockedMilestones(prevUnlocked => {
        const updatedUnlocked = new Set(prevUnlocked);
        const sortedMilestones = Object.keys(grouped)
          .map(Number)
          .sort((a, b) => a - b);

        for (let i = 1; i < sortedMilestones.length; i++) {
          const prevNum = sortedMilestones[i - 1];
          const currNum = sortedMilestones[i];

          // only add new, never remove
          if (!updatedUnlocked.has(currNum)) {
            const prevLessons = grouped[prevNum];
            if (prevLessons.every(l => l.progress === 100)) {
              updatedUnlocked.add(currNum);
            }
          }
        }
        return updatedUnlocked;
      });

    } catch (err) {
      console.error("Failed to load lessons:", err);
    }
  };

  useEffect(() => {
    if (student) loadLessons();
  }, [student]);

  const resetLesson = async (lessonId) => {
    try {
      await api.patch(`/students/${student.id}/lessons/${lessonId}`, {
        progress: 0
      });
      setConfirmLesson(null);
      navigate(`/dashboard/student/lesson/${lessonId}`);
      
      // reload lessons but DO NOT touch unlockedMilestones
      const res = await api.get(`/students/${student.id}/lessons`);
      setMilestones(groupByMilestone(res.data));

    } catch (err) {
      console.error("Failed to reset lesson:", err);
    }
  };

  const getLessonStatus = (lesson, milestoneNumber) => {
    if (lesson.progress === 100) return "completed";
    if (!unlockedMilestones.has(milestoneNumber)) return "locked";
    return "in-progress";
  };

  return (
    <div className="student-lessons-page">
      {Object.entries(milestones)
        .sort(([a], [b]) => Number(a) - Number(b))
        .map(([milestoneNumberStr, lessons]) => {
          const milestoneNumber = Number(milestoneNumberStr);
          return (
            <div key={milestoneNumber} className="milestone-section">
              <h2 className="milestone-title">Milestone {milestoneNumber}</h2>

              <div className="lesson-list">
                {lessons.map((lesson) => {
                  const status = getLessonStatus(lesson, milestoneNumber);

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
        })}

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
