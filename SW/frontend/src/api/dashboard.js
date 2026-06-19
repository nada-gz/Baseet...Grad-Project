/**
 * Dashboard Analytics API
 * Calls the AI Report Agent endpoints for each role.
 */
import api from './axios';

/**
 * Fetch student dashboard analytics from the AI report agent.
 * Returns the StudentReport JSON.
 */
export const fetchStudentDashboard = async () => {
  const response = await api.get('/auth/dashboard/student');
  return response.data;
};

/**
 * Fetch teacher dashboard analytics from the AI report agent.
 * @param {number|null} studentId  Optional: specific student to analyze.
 */
export const fetchTeacherDashboard = async (studentId = null) => {
  const params = studentId ? { student_id: studentId } : {};
  const response = await api.get('/auth/dashboard/teacher', { params });
  return response.data;
};

/**
 * Fetch parent dashboard analytics for their child.
 * @param {number|null} studentId  Optional: specific child to analyze.
 */
export const fetchParentDashboard = async (studentId = null) => {
  const params = studentId ? { student_id: studentId } : {};
  const response = await api.get('/auth/dashboard/parent', { params });
  return response.data;
};

/**
 * Fetch supervisor organization-wide analytics.
 * @param {number|null} studentId  Optional: specific student to analyze.
 */
export const fetchSupervisorDashboard = async (studentId = null) => {
  const params = studentId ? { student_id: studentId } : {};
  const response = await api.get('/auth/dashboard/supervisor', { params });
  return response.data;
};
