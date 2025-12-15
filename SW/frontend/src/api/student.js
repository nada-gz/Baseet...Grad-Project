import api from './axios';

/**
 * Get student by ID
 * @param {number} studentId - Student ID
 * @returns {Promise<Object>} Student data
 */
export const getStudentById = async (studentId) => {
  console.log('[Student API] Fetching student with ID:', studentId);
  try {
    const response = await api.get(`/students/${studentId}`);
    console.log('[Student API] Student fetched successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error fetching student:', error);
    throw error;
  }
};

/**
 * Update student
 * @param {number} studentId - Student ID
 * @param {Object} data - Student update data
 * @returns {Promise<Object>} Updated student data
 */
export const updateStudent = async (studentId, data) => {
  console.log('[Student API] Updating student with ID:', studentId);
  console.log('[Student API] Update data:', data);
  try {
    const response = await api.put(`/students/${studentId}`, data);
    console.log('[Student API] Student updated successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error updating student:', error);
    throw error;
  }
};

/**
 * Get student dashboard data (all modules aggregated)
 * @param {number} studentId - Student ID
 * @returns {Promise<Object>} Dashboard data with lessons, materials, assignments, quizzes, ask_baseet
 */
export const getStudentDashboard = async (studentId) => {
  console.log('[Student API] Fetching dashboard for student ID:', studentId);
  try {
    const response = await api.get(`/students/${studentId}/dashboard`);
    console.log('[Student API] Dashboard fetched successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error fetching dashboard:', error);
    throw error;
  }
};

/**
 * Get all lessons for a student, grouped by milestones
 * @param {number} studentId - Student ID
 * @returns {Promise<Array>} Array of milestones, each containing its lessons
 */
export const getStudentLessons = async (studentId) => {
  try {
    const response = await api.get(`/students/${studentId}/lessons`);
    return response.data; // Returns array of milestones with lessons
  } catch (error) {
    console.error('[Student API] Error fetching lessons:', error);
    throw error;
  }
};

/**
 * Get all materials for a student
 * @param {number} studentId - Student ID
 * @returns {Promise<Array>} Array of materials
 */
export const getStudentMaterials = async (studentId) => {
  try {
    const response = await api.get(`/students/${studentId}/materials`);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error fetching materials:', error);
    throw error;
  }
};

/**
 * Get all assignments for a student
 * @param {number} studentId - Student ID
 * @returns {Promise<Array>} Array of assignments
 */
export const getStudentAssignments = async (studentId) => {
  try {
    const response = await api.get(`/students/${studentId}/assignments`);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error fetching assignments:', error);
    throw error;
  }
};

/**
 * Get all quizzes for a student
 * @param {number} studentId - Student ID
 * @returns {Promise<Array>} Array of quizzes
 */
export const getStudentQuizzes = async (studentId) => {
  try {
    const response = await api.get(`/students/${studentId}/quizzes`);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error fetching quizzes:', error);
    throw error;
  }
};

/**
 * Get all Ask Baseet conversations for a student
 * @param {number} studentId - Student ID
 * @returns {Promise<Array>} Array of Ask Baseet conversations
 */
export const getStudentAskBaseet = async (studentId) => {
  try {
    const response = await api.get(`/students/${studentId}/ask-baseet`);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error fetching Ask Baseet:', error);
    throw error;
  }
};

/**
 * Submit an assignment
 * @param {number} studentId - Student ID
 * @param {number} assignmentId - Assignment ID
 * @param {Object} data - Submission data (submission_url, etc.)
 * @returns {Promise<Object>} Updated assignment
 */
export const submitAssignment = async (studentId, assignmentId, data) => {
  try {
    const response = await api.put(`/students/${studentId}/assignments/${assignmentId}`, {
      ...data,
      status: 'submitted',
      submitted_at: new Date().toISOString(),
    });
    return response.data;
  } catch (error) {
    console.error('[Student API] Error submitting assignment:', error);
    throw error;
  }
};

/**
 * Submit quiz answers
 * @param {number} studentId - Student ID
 * @param {number} quizId - Quiz ID
 * @param {Object} data - Quiz data (answers, status, score, etc.)
 * @returns {Promise<Object>} Updated quiz
 */
export const submitQuiz = async (studentId, quizId, data) => {
  try {
    const response = await api.put(`/students/${studentId}/quizzes/${quizId}`, {
      ...data,
      completed_at: new Date().toISOString(),
    });
    return response.data;
  } catch (error) {
    console.error('[Student API] Error submitting quiz:', error);
    throw error;
  }
};

/**
 * Create a new Ask Baseet question
 * @param {number} studentId - Student ID
 * @param {Object} data - Question data (question, context)
 * @returns {Promise<Object>} Created Ask Baseet entry
 */
export const createAskBaseet = async (studentId, data) => {
  try {
    const response = await api.post(`/students/${studentId}/ask-baseet`, data);
    return response.data;
  } catch (error) {
    console.error('[Student API] Error creating Ask Baseet:', error);
    throw error;
  }
};
