import React, { useEffect, useState } from "react";
import { 
  Users, 
  UserPlus, 
  UserMinus, 
  Search, 
  ArrowLeft,
  CheckCircle2
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../../../services/api";

export default function TeachersManagement() {
  const navigate = useNavigate();
  const [teachers, setTeachers] = useState([]);
  const [allStudents, setAllStudents] = useState([]);
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTeacher, setSearchTeacher] = useState("");
  const [searchStudent, setSearchStudent] = useState("");
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [teachersRes, studentsRes] = await Promise.all([
        api.get("/supervisor/teachers"),
        api.get("/supervisor/students/all")
      ]);
      setTeachers(teachersRes.data);
      setAllStudents(studentsRes.data);
      
      // Keep selected teacher reference updated with new data
      if (selectedTeacher) {
        const updated = teachersRes.data.find(t => t.id === selectedTeacher.id);
        if (updated) setSelectedTeacher(updated);
      }
    } catch (err) {
      console.error("Error fetching management data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async (studentId) => {
    if (!selectedTeacher || processing) return;
    setProcessing(true);
    try {
      await api.post("/supervisor/assignments", {
        teacher_id: selectedTeacher.id,
        student_ids: [studentId]
      });
      await fetchData(); // Refresh
    } catch (err) {
      console.error("Error assigning student:", err);
    } finally {
      setProcessing(false);
    }
  };

  const handleUnassign = async (studentId) => {
    if (!selectedTeacher || processing) return;
    setProcessing(true);
    try {
      await api.delete("/supervisor/assignments", {
        data: {
          teacher_id: selectedTeacher.id,
          student_ids: [studentId]
        }
      });
      await fetchData(); // Refresh
    } catch (err) {
      console.error("Error unassigning student:", err);
    } finally {
      setProcessing(false);
    }
  };

  const filteredTeachers = teachers.filter(t => 
    t.username.toLowerCase().includes(searchTeacher.toLowerCase())
  );

  if (loading) {
    return (
      <div className="supervisor-dashboard-container">
        <div className="status-checking">Gathering Teacher Data...</div>
      </div>
    );
  }

  return (
    <div className="supervisor-dashboard-container">
      {/* Header */}
      <header className="supervisor-header" style={{ alignItems: 'flex-end', marginBottom: '40px' }}>
        <div>
          <button 
            onClick={() => navigate("/dashboard/supervisor")}
            className="back-btn"
          >
            <ArrowLeft size={16} /> Dashboard
          </button>
          <h1 className="supervisor-title">Teachers <span>Management</span></h1>
          <p className="stat-label" style={{ textTransform: 'none', marginTop: '5px' }}>Configure access levels and student-teacher relationships.</p>
        </div>
      </header>

      <div className="assignment-split-view">
        {/* Teacher List */}
        <div className="teacher-sidebar">
          <div className="search-wrapper" style={{ marginBottom: '20px' }}>
            <Search className="search-icon" size={18} />
            <input 
              type="text" 
              placeholder="Search teachers..." 
              value={searchTeacher}
              onChange={(e) => setSearchTeacher(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="teacher-list-panel">
            {filteredTeachers.length > 0 ? filteredTeachers.map((teacher) => (
              <button
                key={teacher.id}
                onClick={() => setSelectedTeacher(teacher)}
                className={`teacher-selection-btn ${selectedTeacher?.id === teacher.id ? "selected" : ""}`}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                  <div className="student-initials-box" style={{ width: '45px', height: '45px', fontSize: '1rem', borderRadius: '14px' }}>
                    {teacher.username.charAt(0).toUpperCase()}
                  </div>
                  <div style={{ textAlign: 'left' }}>
                    <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800 }}>{teacher.username}</h3>
                    <p className="stat-label" style={{ fontSize: '10px', marginTop: '2px' }}>{teacher.assigned_students_count} Students</p>
                  </div>
                </div>
                {selectedTeacher?.id === teacher.id && (
                  <CheckCircle2 className="stat-label" style={{ color: 'var(--highlight)' }} size={20} />
                )}
              </button>
            )) : (
              <div style={{ textAlign: 'center', padding: '40px 0', opacity: 0.3 }}>
                <Users size={40} style={{ margin: '0 auto 10px' }} />
                <p className="stat-label">No results</p>
              </div>
            )}
          </div>
        </div>

        {/* Assignment Tool */}
        <div className="assignment-main">
          {selectedTeacher ? (
            <div className="supervisor-card" style={{ animation: 'fadeIn 0.3s ease-out' }}>
              <div className="supervisor-card-header">
                <div>
                  <h2 className="supervisor-card-title">
                    Manage Access: <span style={{ color: 'var(--highlight)', marginLeft: '8px' }}>{selectedTeacher.username}</span>
                  </h2>
                  <p className="stat-label" style={{ textTransform: 'none', marginTop: '5px' }}>Toggle students to define this teacher's visibility.</p>
                </div>
              </div>

              <div className="search-wrapper" style={{ margin: '30px 0' }}>
                <Search className="search-icon" size={18} />
                <input 
                  type="text" 
                  placeholder="Filter student list..." 
                  value={searchStudent}
                  onChange={(e) => setSearchStudent(e.target.value)}
                  className="search-input"
                  style={{ background: 'var(--secondary-bg)', borderColor: 'transparent' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '15px', maxHeight: '550px', overflowY: 'auto', paddingRight: '10px' }}>
                {allStudents
                  .filter(s => s.username.toLowerCase().includes(searchStudent.toLowerCase()))
                  .map((student) => {
                    const isAssigned = selectedTeacher.assigned_student_ids?.includes(student.id);
                    
                    return (
                      <div 
                        key={student.id}
                        className={`supervisor-student-card ${isAssigned ? 'flagged' : ''}`}
                        style={{ padding: '15px 20px', borderRadius: '20px', boxShadow: 'none', border: '3px solid var(--neutral)', borderColor: isAssigned ? 'var(--highlight)' : 'var(--neutral)', background: isAssigned ? 'rgba(108, 99, 255, 0.05)' : 'white' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div className="student-initials-box" style={{ width: '36px', height: '36px', fontSize: '0.8rem', borderRadius: '10px', background: isAssigned ? 'var(--highlight)' : 'var(--neutral)', color: isAssigned ? 'white' : 'var(--primary-text)' }}>
                              {student.username.charAt(0).toUpperCase()}
                            </div>
                            <span style={{ fontWeight: 800, fontSize: '0.9rem', color: 'var(--primary-text)' }}>{student.username}</span>
                          </div>
                          
                          <button
                            onClick={() => isAssigned ? handleUnassign(student.id) : handleAssign(student.id)}
                            disabled={processing}
                            className={`assignment-action-btn ${isAssigned ? 'remove' : 'add'}`}
                            style={{ 
                              background: isAssigned ? 'var(--error-bg)' : 'var(--highlight)',
                              color: 'white',
                              borderRadius: '12px',
                              padding: '8px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              border: 'none',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                          >
                            {isAssigned ? <UserMinus size={16} /> : <UserPlus size={16} />}
                          </button>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          ) : (
            <div className="supervisor-card" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', borderStyle: 'dashed' }}>
              <div className="stat-icon-box" style={{ background: 'var(--neutral)', color: 'white', width: '100px', height: '100px', marginBottom: '30px', opacity: 0.5 }}>
                <Users size={50} />
              </div>
              <h2 className="supervisor-title" style={{ color: 'var(--neutral)', fontSize: '1.5rem', textAlign: 'center' }}>
                Select a <span>Teacher</span> to manage their class.
              </h2>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
