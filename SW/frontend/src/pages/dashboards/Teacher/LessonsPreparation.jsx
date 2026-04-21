import { useEffect, useState } from "react"; 
import api from "../../../services/api";
import { Trash2, FileText, Plus, File } from "lucide-react";

export default function LessonPreparation() {
  const [courses, setCourses] = useState([]);
  const [courseDescriptions, setCourseDescriptions] = useState({}); // { course_number: "desc" }
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("dashboard"); // "dashboard" | "detail"
  const [selectedCourse, setSelectedCourse] = useState(null);

  // ---------------- FETCH CONTENT ----------------
  const fetchLessons = async (silent = false) => {
    if (!silent) setLoading(true);
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
          url: m.file_url,
          file: null
        })) : [],
        assignments: lesson.assignments ? lesson.assignments.map(a => ({
          id: a.id,
          title: a.title,
          description: a.description || "",
          assignment_type: a.assignment_type || "unknown",
          deadline: a.deadline ? a.deadline.split('.')[0] : "", // format for datetime-local
          files: a.files ? a.files.map(f => ({
            id: f.id,
            name: f.file_name,
            url: f.file_url,
            file: null
          })) : []
        })) : []
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
      setCourses(courses.filter((c) => c.course_number !== num));
      try {
        await api.delete(`/teacher/courses/${num}`);
        // Remove description local
        const newDescs = { ...courseDescriptions };
        delete newDescs[num];
        setCourseDescriptions(newDescs);
      } catch (err) {
        console.error("Delete Course Error:", err);
        fetchLessons(true);
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
      updateMilestoneState();
      try {
        await api.delete(`/teacher/courses/${courseNumber}/milestones/${milestoneNumber}`);
      } catch (err) {
        console.error("Delete Milestone Error:", err);
        fetchLessons(true);
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
                      assignments: [],
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

  const addAssignment = (courseNumber, milestoneNumber, lessonNumber, event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

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
                        assignments: [
                          ...lsn.assignments,
                          ...files.map((f) => ({
                            title: f.name, // Use filename as title
                            description: "",
                            assignment_type: "unknown",
                            deadline: "",
                            files: [{
                              file: f,
                              url: URL.createObjectURL(f),
                              name: f.name
                            }],
                          }))
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

  const deleteAssignment = async (courseNumber, milestoneNumber, lessonNumber, assignmentIndex, assignmentId) => {
    if (window.confirm("Delete this assignment?")) {
      try {
        if (assignmentId) {
          await api.delete(`/teacher/assignments/${assignmentId}`);
        }
        updateAssignmentState();
      } catch (err) {
        console.error("Delete Assignment Error:", err);
        updateAssignmentState();
      }
    }

    function updateAssignmentState() {
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
                          assignments: lsn.assignments.filter((_, idx) => idx !== assignmentIndex),
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

  const handleAssignmentTitleChange = (courseNumber, milestoneNumber, lessonNumber, assignmentIndex, value) => {
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
                        assignments: lsn.assignments.map((asg, idx) =>
                          idx === assignmentIndex ? { ...asg, title: value } : asg
                        ),
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

  const handleAssignmentDescriptionChange = (courseNumber, milestoneNumber, lessonNumber, assignmentIndex, value) => {
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
                        assignments: lsn.assignments.map((asg, idx) =>
                          idx === assignmentIndex ? { ...asg, description: value } : asg
                        ),
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

  const handleAssignmentDeadlineChange = (courseNumber, milestoneNumber, lessonNumber, assignmentIndex, value) => {
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
                        assignments: lsn.assignments.map((asg, idx) =>
                          idx === assignmentIndex ? { ...asg, deadline: value } : asg
                        ),
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

  const handleAssignmentTypeChange = (courseNumber, milestoneNumber, lessonNumber, assignmentIndex, value) => {
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
                        assignments: lsn.assignments.map((asg, idx) =>
                          idx === assignmentIndex ? { ...asg, assignment_type: value } : asg
                        ),
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

  const deleteLesson = async (courseNumber, milestoneNumber, lessonNumber, lessonId) => {
    if (window.confirm("Delete this lesson?")) {
      updateLessonState();
      try {
        if (lessonId) {
          await api.delete(`/teacher/lessons/${lessonId}`);
        }
      } catch (err) {
        console.error("Delete Lesson Error:", err);
        // Silently re-fetch to restore state if delete failed
        fetchLessons(true);
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
                    lessons: m.lessons.filter((lsn) => {
                      if (lessonId && lsn.id) return lsn.id !== lessonId;
                      return lsn.lesson_number !== lessonNumber;
                    }),
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

  const handleLessonDescriptionChange = (courseNumber, milestoneNumber, lessonNumber, value) => {
    setCourses((prev) =>
      prev.map((c) =>
        c.course_number === courseNumber
          ? {
            ...c,
            milestones: c.milestones.map((m) =>
              m.milestone_number === milestoneNumber
                ? {
                  ...m,
                  lessons: m.lessons.map((l) =>
                    l.lesson_number === lessonNumber ? { ...l, description: value } : l
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
      updateFileState();
      try {
        await api.delete(`/teacher/lessons/${lessonId}/materials/${fileId}`);
      } catch (err) {
        console.error("Delete File Error:", err);
        fetchLessons(true);
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
  const deleteAssignmentFile = async (courseNumber, milestoneNumber, lessonNumber, assignmentIndex, fileIndex, fileId, assignmentId) => {
    if (fileId && assignmentId) {
      if (!window.confirm("Delete this assignment file?")) return;
      updateFileState();
      try {
        await api.delete(`/teacher/assignments/${assignmentId}/files/${fileId}`);
      } catch (err) {
        console.error("Delete Assignment File Error:", err);
        fetchLessons(true);
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
                          assignments: lsn.assignments.map((asg, aIdx) =>
                            aIdx === assignmentIndex
                              ? { ...asg, files: asg.files.filter((_, fIdx) => fIdx !== fileIndex) }
                              : asg
                          ),
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

  const handleAssignmentFileUpload = (courseNumber, milestoneNumber, lessonNumber, assignmentIndex, event) => {
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
                        assignments: lsn.assignments.map((asg, aIdx) =>
                          aIdx === assignmentIndex
                            ? {
                              ...asg,
                              files: [
                                ...asg.files,
                                ...files.map((f) => ({
                                  file: f,
                                  url: URL.createObjectURL(f),
                                  name: f.name,
                                })),
                              ],
                            }
                            : asg
                        ),
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
                headers: { "Content-Type": undefined }
              });
            }

            // 3. Save Assignments
            if (lesson.assignments) {
              for (const asg of lesson.assignments) {
                if (!asg.title.trim()) continue;

                const asgFormData = new FormData();
                asgFormData.append("title", asg.title);
                asgFormData.append("description", asg.description || "");
                asgFormData.append("assignment_type", asg.assignment_type || "unknown");
                if (asg.deadline) {
                  asgFormData.append("deadline", asg.deadline);
                }

                const asgRes = await api.post(`/teacher/lessons/${createdLesson.id}/assignments`, asgFormData, {
                  headers: { "Content-Type": undefined }
                });
                const createdAsg = asgRes.data;

                // upload assignment files
                for (const af of asg.files) {
                  if (!af.file) continue;
                  const afData = new FormData();
                  afData.append("file", af.file);
                  await api.post(`/teacher/assignments/${createdAsg.id}/files`, afData, {
                    headers: { "Content-Type": undefined }
                  });
                }
              }
            }
          }
        }
      }

      await fetchLessons(true);
      alert("Content saved successfully!");
    } catch (err) {
      console.error("Save Content Error:", err);
      if (err.response && err.response.data) {
        console.error("Server Error Details:", err.response.data);
      }
      alert("Error saving content. Check console for details.");
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
                  className="delete-btn-well-styled"
                  title="Delete Course"
                  onClick={(e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    deleteCourse(course.course_number, e);
                  }}
                >
                  <Trash2 size={24} />
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
        <div className="back-box">
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
      </div>
      <h1 className="text-2xl level-card-title">Course {course.course_number}: {courseDescriptions[course.course_number]}</h1>

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
                className="delete-btn-well-styled"
                title="Delete Milestone"
                onClick={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  deleteMilestone(course.course_number, m.milestone_number);
                }}
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
                    className="lesson-title-input"
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
                    className="delete-btn-well-styled"
                    title="Delete Lesson"
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                      deleteLesson(course.course_number, m.milestone_number, l.lesson_number, l.id);
                    }}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                {/* --- LESSON MATERIALS --- */}
                <div className="lesson-files">
                  <div className="items-center justify-between mb-2">
                    <p className="section-subtitle">Lesson Materials</p>
                    <label className="btn btn-primary btn-xs cursor-pointer gap-1">
                      <Plus size={14} /> Upload Material
                      <input
                        type="file"
                        multiple
                        className="hidden"
                        onChange={(e) =>
                          handleFileUpload(course.course_number, m.milestone_number, l.lesson_number, e)
                        }
                      />
                    </label>
                  </div>
                  <div className="materials-list">
                    {l.files.map((f, idx) => (
                      <div key={idx} className="file-item flex items-center p-2 border rounded mb-1 w-full">
                        <div className="flex items-center gap-2 flex-grow min-w-0">
                          <FileText size={18} className="text-secondary shrink-0" />
                          <a
                            href={f.file ? f.url : `http://127.0.0.1:8000${f.url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="clickable-file-link text-sm truncate"
                          >
                            {f.name}
                          </a>
                        </div>
                        <button
                          className="delete-btn-well-styled shrink-0"
                          title="Delete Material"
                          onClick={(e) => {
                            e.stopPropagation();
                            e.preventDefault();
                            deleteFile(
                              course.course_number,
                              m.milestone_number,
                              l.lesson_number,
                              idx,
                              f.id,
                              l.id
                            );
                          }}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* --- ASSIGNMENTS --- */}
                < div className="lesson-assignments-section" >
                  <div className="items-center justify-between mb-2">
                    <p className="section-subtitle">Assignments</p>
                    <label className="btn btn-primary btn-xs cursor-pointer gap-1">
                      <Plus size={14} /> Add Assignment
                      <input
                        type="file"
                        multiple
                        className="hidden"
                        onChange={(e) => addAssignment(course.course_number, m.milestone_number, l.lesson_number, e)}
                      />
                    </label>
                  </div>

                  <div className="assignments-list mt-2">
                    {l.assignments && l.assignments.map((asg, aIdx) => (
                      <div key={aIdx} className="assignment-card-premium">
                        {/* Row 1: File Info & Delete Icon */}
                        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-50">
                          <div className="flex items-center gap-3">
                            <div className="bg-indigo-50 p-2 rounded-xl">
                              <File size={20} className="text-indigo-600" />
                            </div>
                            <div className="flex flex-col">
                              <a
                                href={asg.files[0]?.file ? asg.files[0]?.url : `http://127.0.0.1:8000${asg.files[0]?.url}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="clickable-file-link text-sm font-black text-slate-700"
                              >
                                {asg.title}
                              </a>
                              <span className="text-[10px] text-slate-400 font-bold uppercase">Assignment File</span>
                            </div>
                          </div>
                          <button
                            className="trash-icon-btn"
                            title="Delete Assignment"
                            onClick={(e) => {
                              e.stopPropagation();
                              e.preventDefault();
                              deleteAssignment(course.course_number, m.milestone_number, l.lesson_number, aIdx, asg.id);
                            }}
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>

                        {/* Row 2: Type Toggle & Deadline */}
                        <div className="flex flex-wrap items-end gap-6">
                          <div>
                            <p className="text-[10px] font-black uppercase text-slate-400 mb-2 ml-1">Submission Type</p>
                            <div className="type-toggle-container">
                              <button
                                className={`type-toggle-btn ${asg.assignment_type !== 'narrative' ? 'active-standard' : ''}`}
                                onClick={() => handleAssignmentTypeChange(course.course_number, m.milestone_number, l.lesson_number, aIdx, "unknown")}
                              >
                                STANDARD
                              </button>
                              <button
                                className={`type-toggle-btn ${asg.assignment_type === 'narrative' ? 'active-narrative' : ''}`}
                                onClick={() => handleAssignmentTypeChange(course.course_number, m.milestone_number, l.lesson_number, aIdx, "narrative")}
                              >
                                NARRATIVE
                              </button>
                            </div>
                          </div>

                          <div>
                            <p className="text-[10px] font-black uppercase text-slate-400 mb-2 ml-1">Deadline Date</p>
                            <input
                              type="datetime-local"
                              className="deadline-input-compact"
                              value={asg.deadline || ""}
                              onChange={(e) => handleAssignmentDeadlineChange(course.course_number, m.milestone_number, l.lesson_number, aIdx, e.target.value)}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
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
