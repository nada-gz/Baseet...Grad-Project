import { useEffect, useState } from "react";
import api from "../../../services/api";
import { Trash2, FileText } from "lucide-react";

export default function LessonPreparation() {
  const [courses, setCourses] = useState([]);
  const [courseDescriptions, setCourseDescriptions] = useState({}); // { course_number: "desc" }
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("dashboard"); // "dashboard" | "detail"
  const [selectedCourse, setSelectedCourse] = useState(null);

  // ---------------- FETCH CONTENT ----------------
  const fetchLessons = async () => {
    setLoading(true);
    try {
      const [lessonsRes, coursesRes] = await Promise.all([
        api.get("/teacher/lessons"),
        api.get("/teacher/courses")
      ]);

      // 1. Group lessons by course
      const groupedLessons = groupByCourses(lessonsRes.data || []);

      // 2. Identify all unique course numbers from metadata + lessons
      const allCourseNumbers = new Set([
        ...(coursesRes.data || []).map(c => c.course_number),
        ...groupedLessons.map(c => c.course_number)
      ]);

      // 3. Construct the merged courses array
      const mergedCourses = Array.from(allCourseNumbers)
        .sort((a, b) => a - b)
        .map(num => {
          // Find existing group or create empty one
          const existingGroup = groupedLessons.find(g => g.course_number === num);
          if (existingGroup) return existingGroup;

          return { course_number: num, milestones: [] };
        });

      setCourses(mergedCourses);

      // 4. Map descriptions
      const descMap = {};
      (coursesRes.data || []).forEach(c => {
        descMap[c.course_number] = c.description || "";
      });
      setCourseDescriptions(descMap);

    } catch (err) {
      console.error("Fetch content lessons error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLessons();
  }, []);

  const groupByCourses = (lessons) => {
    const coursesMap = {};

    lessons.forEach((lesson) => {
      const courseNum = lesson.course_number;

      if (!coursesMap[courseNum]) {
        coursesMap[courseNum] = { course_number: courseNum, milestones: [] };
      }

      let milestone = coursesMap[courseNum].milestones.find(
        (m) => m.milestone_number === lesson.milestone_number
      );

      if (!milestone) {
        milestone = { milestone_number: lesson.milestone_number, lessons: [] };
        coursesMap[courseNum].milestones.push(milestone);
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

    return Object.values(coursesMap);
  };

  // ---------------- COURSES ----------------
  const addCourse = () => {
    const next =
      courses.length > 0
        ? Math.max(...courses.map((c) => c.course_number)) + 1
        : 1;

    setCourses([...courses, { course_number: next, milestones: [] }]);
    setCourseDescriptions(prev => ({ ...prev, [next]: "" }));
  };

  const deleteCourse = async (num, e) => {
    e.stopPropagation(); // prevent card click
    if (window.confirm("Are you sure you want to delete this course and all its contents? This cannot be undone.")) {
      try {
        await api.delete(`/teacher/courses/${num}`);
        setCourses(courses.filter((c) => c.course_number !== num));
        // Remove description local
        const newDescs = { ...courseDescriptions };
        delete newDescs[num];
        setCourseDescriptions(newDescs);
      } catch (err) {
        console.error("Delete Course Error:", err);
        // Fallback for unsaved courses (local only)
        setCourses(courses.filter((c) => c.course_number !== num));
      }
    }
  };

  // ---------------- MILESTONES ----------------
  const addMilestone = (courseNumber) => {
    setCourses((prev) =>
      prev.map((c) =>
        c.course_number === courseNumber
          ? {
            ...c,
            milestones: [
              ...c.milestones,
              {
                milestone_number:
                  c.milestones.length > 0
                    ? Math.max(...c.milestones.map((m) => m.milestone_number)) + 1
                    : 1,
                lessons: [],
              },
            ],
          }
          : c
      )
    );
  };

  const deleteMilestone = async (courseNumber, milestoneNumber) => {
    if (window.confirm("Delete this milestone and its lessons?")) {
      try {
        await api.delete(`/teacher/courses/${courseNumber}/milestones/${milestoneNumber}`);
        updateMilestoneState();
      } catch (err) {
        console.error("Delete Milestone Error:", err);
        updateMilestoneState();
      }
    }

    function updateMilestoneState() {
      setCourses((prev) =>
        prev.map((c) =>
          c.course_number === courseNumber
            ? {
              ...c,
              milestones: c.milestones.filter((m) => m.milestone_number !== milestoneNumber),
            }
            : c
        )
      );
    }
  };

  // ---------------- LESSONS ----------------
  const addLesson = (courseNumber, milestoneNumber) => {
    setCourses((prev) =>
      prev.map((c) =>
        c.course_number === courseNumber
          ? {
            ...c,
            milestones: c.milestones.map((m) =>
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
          : c
      )
    );
  };

  const deleteLesson = async (courseNumber, milestoneNumber, lessonNumber, lessonId) => {
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
      setCourses((prev) =>
        prev.map((c) =>
          c.course_number === courseNumber
            ? {
              ...c,
              milestones: c.milestones.map((m) =>
                m.milestone_number === milestoneNumber
                  ? {
                    ...m,
                    lessons: m.lessons.filter((lsn) => lsn.lesson_number !== lessonNumber),
                  }
                  : m
              ),
            }
            : c
        )
      );
    }
  };

  const handleLessonTitleChange = (courseNumber, milestoneNumber, lessonNumber, value) => {
    setCourses((prev) =>
      prev.map((c) =>
        c.course_number === courseNumber
          ? {
            ...c,
            milestones: c.milestones.map((m) =>
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
          : c
      )
    );
  };

  const deleteFile = async (courseNumber, milestoneNumber, lessonNumber, fileIndex, fileId, lessonId) => {
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
      setCourses((prev) =>
        prev.map((c) =>
          c.course_number === courseNumber
            ? {
              ...c,
              milestones: c.milestones.map((m) =>
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
            : c
        )
      );
    }
  };

  const handleFileUpload = (courseNumber, milestoneNumber, lessonNumber, event) => {
    const files = Array.from(event.target.files);

    setCourses((prev) =>
      prev.map((c) =>
        c.course_number === courseNumber
          ? {
            ...c,
            milestones: c.milestones.map((m) =>
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
          : c
      )
    );
  };

  // ---------------- SAVE ----------------
  const saveCourses = async () => {
    try {
      // 1. Save Course Metadata
      for (const course of courses) {
        await api.post("/teacher/courses", {
          course_number: course.course_number,
          description: courseDescriptions[course.course_number] || ""
        });
      }

      // 2. Save Lessons
      for (const course of courses) {
        for (const milestone of course.milestones) {
          for (const lesson of milestone.lessons) {
            if (!lesson.title.trim()) continue;

            const formData = new FormData();
            formData.append("course_number", course.course_number);
            formData.append("milestone_number", milestone.milestone_number);
            formData.append("lesson_number", lesson.lesson_number);
            formData.append("title", lesson.title);
            formData.append("description", lesson.description || "");

            console.log("Saving lesson:", {
              course_number: course.course_number,
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

  // --- DASHBOARD VIEW ---
  if (view === "dashboard") {
    return (
      <div className="lesson-prep-container level-prep-container">
        <button className="btn btn-primary mb-6" onClick={addCourse}>
          Add Course
        </button>

        <div className="levels-grid">
          {courses.map((course) => (
            <div
              key={course.course_number}
              className="level-card-dashboard"
              onClick={() => {
                setSelectedCourse(course);
                setView("detail");
              }}
            >
              <div className="level-card-header">
                <h2 className="level-card-title">Course {course.course_number}</h2>
                <button
                  className="level-delete-btn"
                  title="Delete Course"
                  onClick={(e) => deleteCourse(course.course_number, e)}
                >
                  <Trash2 size={20} />
                </button>
              </div>

              <div className="mb-2" style={{ flexGrow: 1 }}>
                <label className="level-card-desc-label">Description</label>
                <textarea
                  className="level-card-textarea"
                  rows={4}
                  placeholder="Enter a brief description for this course..."
                  value={courseDescriptions[course.course_number] || ""}
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) =>
                    setCourseDescriptions({
                      ...courseDescriptions,
                      [course.course_number]: e.target.value
                    })
                  }
                />
              </div>

              <div className="level-card-footer">
                <span>{course.milestones.length} Milestones</span>
              </div>
            </div>
          ))}
        </div>

        <button className="btn btn-save mt-6" onClick={saveCourses}>
          Save All
        </button>
      </div>
    );
  }

  // --- DETAIL VIEW ---
  // Ensure we are working with the latest state of the selected course
  const course = courses.find(c => c.course_number === selectedCourse.course_number);

  if (!course) return <p>Course not found</p>;

  return (
    <div className="lesson-prep-container">
      <div className="flex items-center mb-6">
        <div class="back-box">
          <button
            className="mr-4 back"
            onClick={() => {
              setView("dashboard");
              setSelectedCourse(null);
            }}
          >
            &larr; Back to Courses
          </button>
        </div>
        <h1 className="text-2xl level-card-title">Course {course.course_number}: {courseDescriptions[course.course_number]}</h1>
      </div>

      <div className="level-detail-view">
        <button
          className="btn btn-outline mb-4 add-milestone"
          onClick={() => addMilestone(course.course_number)}
        >
          Add Milestone
        </button>

        {course.milestones.map((m) => (
          <div key={m.milestone_number} className="milestone-card">
            <div className="milestone-header">
              <h3>Milestone {m.milestone_number}</h3>
              <button
                className="delete-btn"
                onClick={() => deleteMilestone(course.course_number, m.milestone_number)}
              >
                <Trash2 size={18} />
              </button>
            </div>

            <button
              className="btn btn-outline mb-4 add-lesson"
              onClick={() => addLesson(course.course_number, m.milestone_number)}
            >
              Add Lesson
            </button>

            {m.lessons.map((l) => (
              <div key={l.lesson_number} className="lesson-card">
                <div className="lesson-header">
                  <span>
                    {course.course_number}.{m.milestone_number}.{l.lesson_number}
                  </span>

                  <input
                    type="text"
                    value={l.title}
                    placeholder="Lesson Title"
                    onChange={(e) =>
                      handleLessonTitleChange(
                        course.course_number,
                        m.milestone_number,
                        l.lesson_number,
                        e.target.value
                      )
                    }
                  />
                  <button
                    className="delete-btn"
                    onClick={() =>
                      deleteLesson(course.course_number, m.milestone_number, l.lesson_number, l.id)
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
                            course.course_number,
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
                      handleFileUpload(course.course_number, m.milestone_number, l.lesson_number, e)
                    }
                  />
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      <button className="btn detail-save mt-6" onClick={saveCourses}>
        Save
      </button>
    </div>
  );
}
