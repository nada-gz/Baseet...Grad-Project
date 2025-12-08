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
 * @param {number} [data.age] - Student age
 * @param {string} [data.autism_type] - Autism type
 * @param {string} [data.sensitivities] - Sensitivities
 * @param {string} [data.learning_style] - Learning style
 * @param {number} [data.baseline_engagement] - Baseline engagement
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

