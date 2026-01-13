import { useEffect, useState } from "react";
import api from "../../../services/api";
import { Trash2, FileText } from "lucide-react";

export default function LessonPreparation() {
  const [levels, setLevels] = useState([]);
  const [loading, setLoading] = useState(true);

  // ---------------- FETCH CONTENT ----------------
  // ---------------- FETCH CONTENT ----------------
  const fetchLessons = async () => {
    setLoading(true);
    try {
      const res = await api.get("/teacher/lessons");
      const grouped = groupByLevels(res.data || []);
      setLevels(grouped);
    } catch (err) {
      console.error("Fetch content lessons error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLessons();
  }, []);

  const groupByLevels = (lessons) => {
    const levelsMap = {};

    lessons.forEach((lesson) => {
      const levelNum = lesson.level_number;

      if (!levelsMap[levelNum]) {
        levelsMap[levelNum] = { level_number: levelNum, milestones: [] };
      }

      let milestone = levelsMap[levelNum].milestones.find(
        (m) => m.milestone_number === lesson.milestone_number
      );

      if (!milestone) {
        milestone = { milestone_number: lesson.milestone_number, lessons: [] };
        levelsMap[levelNum].milestones.push(milestone);
      }

      milestone.lessons.push({
        id: lesson.id,
        lesson_number: lesson.lesson_number,
        title: lesson.title,
        description: lesson.description || "",
        files: lesson.materials ? lesson.materials.map(m => ({
          id: m.id,
          name: m.title,
          url: m.file_url, // assuming backend provides this
          file: null // It's a remote file, not a local File object
        })) : [],
      });
    });

    return Object.values(levelsMap);
  };

  // ---------------- LEVELS ----------------
  const addLevel = () => {
    const next =
      levels.length > 0
        ? Math.max(...levels.map((l) => l.level_number)) + 1
        : 1;

    setLevels([...levels, { level_number: next, milestones: [] }]);
  };

  const deleteLevel = async (num) => {
    if (window.confirm("Are you sure you want to delete this level and all its contents? This cannot be undone.")) {
      try {
        await api.delete(`/teacher/levels/${num}`);
        setLevels(levels.filter((l) => l.level_number !== num));
      } catch (err) {
        console.error("Delete Level Error:", err);
        // Fallback for unsaved levels (local only)
        setLevels(levels.filter((l) => l.level_number !== num));
      }
    }
  };

  // ---------------- MILESTONES ----------------
  const addMilestone = (levelNumber) => {
    setLevels((prev) =>
      prev.map((l) =>
        l.level_number === levelNumber
          ? {
            ...l,
            milestones: [
              ...l.milestones,
              {
                milestone_number:
                  l.milestones.length > 0
                    ? Math.max(...l.milestones.map((m) => m.milestone_number)) + 1
                    : 1,
                lessons: [],
              },
            ],
          }
          : l
      )
    );
  };

  const deleteMilestone = async (levelNumber, milestoneNumber) => {
    if (window.confirm("Delete this milestone and its lessons?")) {
      try {
        await api.delete(`/teacher/levels/${levelNumber}/milestones/${milestoneNumber}`);
        updateMilestoneState();
      } catch (err) {
        console.error("Delete Milestone Error:", err);
        updateMilestoneState();
      }
    }

    function updateMilestoneState() {
      setLevels((prev) =>
        prev.map((l) =>
          l.level_number === levelNumber
            ? {
              ...l,
              milestones: l.milestones.filter((m) => m.milestone_number !== milestoneNumber),
            }
            : l
        )
      );
    }
  };

  // ---------------- LESSONS ----------------
  const addLesson = (levelNumber, milestoneNumber) => {
    setLevels((prev) =>
      prev.map((l) =>
        l.level_number === levelNumber
          ? {
            ...l,
            milestones: l.milestones.map((m) =>
              m.milestone_number === milestoneNumber
                ? {
                  ...m,
                  lessons: [
                    ...m.lessons,
                    {
                      lesson_number:
                        m.lessons.length > 0
                          ? Math.max(...m.lessons.map((x) => x.lesson_number)) + 1
                          : 1,
                      title: "",
                      description: "",
                      files: [],
                    },
                  ],
                }
                : m
            ),
          }
          : l
      )
    );
  };

  const deleteLesson = async (levelNumber, milestoneNumber, lessonNumber, lessonId) => {
    if (window.confirm("Delete this lesson?")) {
      try {
        if (lessonId) {
          await api.delete(`/teacher/lessons/${lessonId}`);
        }
        updateLessonState();
      } catch (err) {
        console.error("Delete Lesson Error:", err);
        updateLessonState();
      }
    }

    function updateLessonState() {
      setLevels((prev) =>
        prev.map((l) =>
          l.level_number === levelNumber
            ? {
              ...l,
              milestones: l.milestones.map((m) =>
                m.milestone_number === milestoneNumber
                  ? {
                    ...m,
                    lessons: m.lessons.filter((lsn) => lsn.lesson_number !== lessonNumber),
                  }
                  : m
              ),
            }
            : l
        )
      );
    }
  };

  const handleLessonTitleChange = (levelNumber, milestoneNumber, lessonNumber, value) => {
    setLevels((prev) =>
      prev.map((l) =>
        l.level_number === levelNumber
          ? {
            ...l,
            milestones: l.milestones.map((m) =>
              m.milestone_number === milestoneNumber
                ? {
                  ...m,
                  lessons: m.lessons.map((lsn) =>
                    lsn.lesson_number === lessonNumber
                      ? { ...lsn, title: value }
                      : lsn
                  ),
                }
                : m
            ),
          }
          : l
      )
    );
  };

  const deleteFile = async (levelNumber, milestoneNumber, lessonNumber, fileIndex, fileId, lessonId) => {
    if (fileId && lessonId) {
      if (!window.confirm("Delete this file permanently?")) return;
      try {
        await api.delete(`/teacher/lessons/${lessonId}/materials/${fileId}`);
        updateFileState();
      } catch (err) {
        console.error("Delete File Error:", err);
      }
    } else {
      updateFileState();
    }

    function updateFileState() {
      setLevels((prev) =>
        prev.map((l) =>
          l.level_number === levelNumber
            ? {
              ...l,
              milestones: l.milestones.map((m) =>
                m.milestone_number === milestoneNumber
                  ? {
                    ...m,
                    lessons: m.lessons.map((lsn) =>
                      lsn.lesson_number === lessonNumber
                        ? {
                          ...lsn,
                          files: lsn.files.filter((_, idx) => idx !== fileIndex),
                        }
                        : lsn
                    ),
                  }
                  : m
              ),
            }
            : l
        )
      );
    }
  };

  const handleFileUpload = (levelNumber, milestoneNumber, lessonNumber, event) => {
    const files = Array.from(event.target.files);

    setLevels((prev) =>
      prev.map((l) =>
        l.level_number === levelNumber
          ? {
            ...l,
            milestones: l.milestones.map((m) =>
              m.milestone_number === milestoneNumber
                ? {
                  ...m,
                  lessons: m.lessons.map((lsn) =>
                    lsn.lesson_number === lessonNumber
                      ? {
                        ...lsn,
                        files: [
                          ...lsn.files,
                          ...files.map((f) => ({
                            file: f,
                            url: URL.createObjectURL(f),
                            name: f.name,
                          })),
                        ],
                      }
                      : lsn
                  ),
                }
                : m
            ),
          }
          : l
      )
    );
  };

  // ---------------- SAVE ----------------
  const saveLevels = async () => {
    try {
      for (const level of levels) {
        for (const milestone of level.milestones) {
          for (const lesson of milestone.lessons) {
            if (!lesson.title.trim()) continue;

            const formData = new FormData();
            formData.append("level_number", level.level_number);
            formData.append("milestone_number", milestone.milestone_number);
            formData.append("lesson_number", lesson.lesson_number);
            formData.append("title", lesson.title);
            formData.append("description", lesson.description || "");

            console.log("Saving lesson:", {
              level_number: level.level_number,
              milestone_number: milestone.milestone_number,
              lesson_number: lesson.lesson_number,
              title: lesson.title,
              description: lesson.description || ""
            });

            const res = await api.post("/teacher/lessons", formData, {
              headers: {
                "Content-Type": undefined,
              },
            });
            const createdLesson = res.data;

            // upload files
            for (const f of lesson.files) {
              if (!f.file) continue;

              const fileData = new FormData();
              fileData.append("file", f.file);

              await api.post(`/teacher/lessons/${createdLesson.id}/materials`, fileData, {
                headers: {
                  "Content-Type": undefined,
                },
              });
            }
          }
        }
      }

      alert("Content saved successfully!");
      fetchLessons();
    } catch (err) {
      console.error("Save Content Error:", err);
      alert("Error saving content. Check console.");
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div className="lesson-prep-container">
      <button className="btn btn-primary mb-6" onClick={addLevel}>
        Add Level
      </button>

      {levels.map((level) => (
        <div key={level.level_number} className="level-card">
          <div className="level-header">
            <h2>Level {level.level_number}</h2>
            <button
              className="delete-btn"
              onClick={() => deleteLevel(level.level_number)}
            >
              <Trash2 size={22} />
            </button>
          </div>

          <button
            className="btn btn-outline mb-4"
            onClick={() => addMilestone(level.level_number)}
          >
            Add Milestone
          </button>

          {level.milestones.map((m) => (
            <div key={m.milestone_number} className="milestone-card">
              <div className="milestone-header">
                <h3>Milestone {m.milestone_number}</h3>
                <button
                  className="delete-btn"
                  onClick={() => deleteMilestone(level.level_number, m.milestone_number)}
                >
                  <Trash2 size={18} />
                </button>
              </div>

              <button
                className="btn btn-outline mb-4 add-lesson"
                onClick={() => addLesson(level.level_number, m.milestone_number)}
              >
                Add Lesson
              </button>

              {m.lessons.map((l) => (
                <div key={l.lesson_number} className="lesson-card">
                  <div className="lesson-header">
                    <span>
                      {level.level_number}.{m.milestone_number}.{l.lesson_number}
                    </span>

                    <input
                      type="text"
                      value={l.title}
                      placeholder="Lesson Title"
                      onChange={(e) =>
                        handleLessonTitleChange(
                          level.level_number,
                          m.milestone_number,
                          l.lesson_number,
                          e.target.value
                        )
                      }
                    />
                    <button
                      className="delete-btn"
                      onClick={() =>
                        deleteLesson(level.level_number, m.milestone_number, l.lesson_number, l.id)
                      }
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>

                  <div className="lesson-files">
                    {l.files.map((f, idx) => (
                      <div key={idx} className="file-item">
                        <span><FileText size={16} /> {f.name}</span>
                        <button
                          className="delete-btn-sm"
                          style={{ marginLeft: "10px", background: "none", border: "none", cursor: "pointer", color: "red" }}
                          onClick={() =>
                            deleteFile(
                              level.level_number,
                              m.milestone_number,
                              l.lesson_number,
                              idx,
                              f.id,
                              l.id
                            )
                          }
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}

                    <input
                      type="file"
                      multiple
                      onChange={(e) =>
                        handleFileUpload(level.level_number, m.milestone_number, l.lesson_number, e)
                      }
                    />
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      ))}

      <button className="btn btn-save mt-6" onClick={saveLevels}>
        Save All
      </button>
    </div>
  );
}
