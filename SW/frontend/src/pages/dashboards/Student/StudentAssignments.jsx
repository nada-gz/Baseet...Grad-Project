import { useEffect, useState } from "react";
import api from "../../../services/api";
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
} from "lucide-react";

/**
 * Supported assignment types:
 * pdf | docx | img | zip
 */
const assignmentIcons = {
  pdf: <FileText size={18} />,
  docx: <FileText size={18} />,
  img: <Image size={18} />,
  zip: <File size={18} />,
};

export default function StudentAssignments() {
  const { user: student } = useAuth();

  const [milestones, setMilestones] = useState({});
  const [openMilestones, setOpenMilestones] = useState({});
  const [openLessons, setOpenLessons] = useState({});

  useEffect(() => {
    const loadLessonsAndAssignments = async () => {
      const res = await api.get(`/students/${student.id}/lessons`);
      const grouped = {};

      for (let lesson of res.data) {
        const assRes = await api.get(
          `/students/${student.id}/lessons/${lesson.id}/assignments`
        );

        lesson.assignments = assRes.data;

        if (!grouped[lesson.milestone_number]) {
          grouped[lesson.milestone_number] = [];
        }
        grouped[lesson.milestone_number].push(lesson);
      }

      setMilestones(grouped);
    };

    if (student?.id) loadLessonsAndAssignments();
  }, [student]);

  const getLessonStatus = (lesson) => {
    if (lesson.progress === 100) return "completed";
    if (lesson.status === "in-progress") return "in-progress";
    return "locked";
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

  return (
    <div className="materials-page">
      {Object.entries(milestones).map(([milestoneNumber, lessons]) => (
        <div key={milestoneNumber} className="milestone-card">
          {/* Milestone Header */}
          <div
            className="milestone-header"
            onClick={() => toggleMilestone(milestoneNumber)}
          >
            {openMilestones[milestoneNumber] ? (
              <ChevronDown size={18} color="var(--highlight)" />
            ) : (
              <ChevronRight size={18} color="var(--highlight)" />
            )}
            <h2>Milestone {milestoneNumber}</h2>
          </div>

          {/* Lessons */}
          {openMilestones[milestoneNumber] &&
            lessons.map((lesson) => {
              const status = getLessonStatus(lesson);

              return (
                <div key={lesson.id} className="lesson-block">
                  <div
                    className="lesson-header"
                    onClick={() => toggleLesson(lesson.id)}
                  >
                    {openLessons[lesson.id] ? (
                      <ChevronDown size={16} />
                    ) : (
                      <ChevronRight size={16} />
                    )}
                    <span>
                      Lesson {lesson.lesson_number}: {lesson.title}
                    </span>
                  </div>

                  {/* Assignments */}
                  {openLessons[lesson.id] ? (
                    lesson.assignments?.length > 0 ? (
                      <div className="materials-list">
                        {lesson.assignments.map((assignment) => (
                          <div
                            key={assignment.id}
                            className="material-item"
                          >
                            <div className="material-info">
                              <div className="material-icon">
                                {assignmentIcons[
                                  assignment.assignment_type
                                ] || <File size={18} />}
                              </div>

                              <div className="material-text">
                                <p className="material-title">
                                  {assignment.title}
                                </p>
                                {assignment.description && (
                                  <p className="material-description">
                                    {assignment.description}
                                  </p>
                                )}
                              </div>
                            </div>

                            {status === "locked" ? (
                              <span className="material-locked">
                                <Lock size={24} />
                              </span>
                            ) : (
                              <div className="material-actions">
                                <a
                                  href={`http://127.0.0.1:8000${assignment.file_url}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="material-btn material-btn-outline"
                                >
                                  <Eye size={16} /> View
                                </a>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="materials-empty-icon">
                        <span>No assignments uploaded yet</span>
                        <Frown size={24} className="sad-icon" />
                      </div>
                    )
                  ) : null}
                </div>
              );
            })}
        </div>
      ))}
    </div>
  );
}
