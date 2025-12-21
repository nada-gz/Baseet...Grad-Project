import { useEffect, useState } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth";
import {
  FileText,
  Image,
  Video,
  Presentation,
  File,
  Lock,
  Eye,
  Download,
  Music,
  ChevronDown,
  ChevronRight,
  Frown,
} from "lucide-react";

/**
 * Supported material types:
 * word | pdf | ppt | img | video | audio
 */
const materialIcons = {
  word: <FileText size={18} />,
  pdf: <FileText size={18} />,
  ppt: <Presentation size={18} />,
  img: <Image size={18} />,
  video: <Video size={18} />,
  audio: <Music size={18} />,
};

export default function StudentMaterials() {
  const { user: student } = useAuth();

  const [milestones, setMilestones] = useState({});
  const [openMilestones, setOpenMilestones] = useState({});
  const [openLessons, setOpenLessons] = useState({});

  useEffect(() => {
    const loadLessonsAndMaterials = async () => {
      const res = await api.get(`/students/${student.id}/lessons`);
      const grouped = {};

      for (let lesson of res.data) {
        // fetch materials for each lesson
        const matRes = await api.get(
          `/students/${student.id}/lessons/${lesson.id}/materials`
        );
        lesson.materials = matRes.data;

        if (!grouped[lesson.milestone_number]) grouped[lesson.milestone_number] = [];
        grouped[lesson.milestone_number].push(lesson);
      }

      setMilestones(grouped);
    };

    if (student?.id) loadLessonsAndMaterials();
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

                  {/* Materials */}
                  {openLessons[lesson.id] ? (
                    lesson.materials?.length > 0 ? (
                      <div className="materials-list">
                        {lesson.materials.map((material) => (
                          <div key={material.id} className="material-item">
                            <div className="material-info">
                              <div className="material-icon">
                                {materialIcons[material.material_type] || (
                                  <File size={18} />
                                )}
                              </div>
                              <div className="material-text">
                                <p className="material-title">{material.title}</p>
                                {material.description && (
                                  <p className="material-description">
                                    {material.description}
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
                                  href={`http://127.0.0.1:8000${material.file_url}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="material-btn material-btn-outline"
                                >
                                  <Eye size={16} /> View
                                </a>

                                {/* <a
                                  href={`http://127.0.0.1:8000/students/${student.id}/lessons/${lesson.id}/materials/${material.id}/download`}
                                  className="material-btn material-btn-primary"
                                >
                                  <Download size={16} /> Download
                                </a> */}

                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="materials-empty-icon">
                        <span>No materials uploaded yet</span>
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
