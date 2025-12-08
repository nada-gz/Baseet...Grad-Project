import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { getStudentById, updateStudent } from "../../api/student";
import { Input, Button, Card, ErrorMessage } from "../../components/ui";

export default function StudentProfile() {
  const { studentId } = useParams();
  const { role } = useAuth();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Form state
  const [formData, setFormData] = useState({
    age: "",
    autism_type: "",
    sensitivities: "",
    learning_style: "",
    baseline_engagement: "",
  });

  // Check if user can edit (parent or teacher only)
  const canEdit = role === "parent" || role === "teacher";

  // Load student data on mount
  useEffect(() => {
    if (studentId) {
      loadStudent();
    }
  }, [studentId]);

  const loadStudent = async () => {
    setLoading(true);
    setError("");
    try {
      console.log("[StudentProfile] Loading student with ID:", studentId);
      const studentData = await getStudentById(parseInt(studentId));
      setStudent(studentData);
      
      // Populate form with student data
      setFormData({
        age: studentData.age || "",
        autism_type: studentData.autism_type || "",
        sensitivities: studentData.sensitivities || "",
        learning_style: studentData.learning_style || "",
        baseline_engagement: studentData.baseline_engagement || "",
      });
      
      console.log("[StudentProfile] Student loaded successfully:", studentData);
    } catch (err) {
      console.error("[StudentProfile] Error loading student:", err);
      const errorMessage = err.response?.data?.detail || "Failed to load student profile";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      console.log("[StudentProfile] Updating student with data:", formData);
      
      // Prepare update data (only send fields that have values)
      const updateData = {};
      if (formData.age) updateData.age = parseInt(formData.age);
      if (formData.autism_type) updateData.autism_type = formData.autism_type;
      if (formData.sensitivities) updateData.sensitivities = formData.sensitivities;
      if (formData.learning_style) updateData.learning_style = formData.learning_style;
      if (formData.baseline_engagement) {
        updateData.baseline_engagement = parseFloat(formData.baseline_engagement);
      }

      const updatedStudent = await updateStudent(parseInt(studentId), updateData);
      setStudent(updatedStudent);
      setSuccess("Student profile updated successfully!");
      console.log("[StudentProfile] Student updated successfully:", updatedStudent);
    } catch (err) {
      console.error("[StudentProfile] Error updating student:", err);
      const errorMessage = err.response?.data?.detail || "Failed to update student profile";
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-gray-700">Loading student profile...</p>
        </div>
      </div>
    );
  }

  if (!student) {
    return (
      <div className="p-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <ErrorMessage message={error || "Student not found"} variant="error" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Student Profile</h1>
      
      <Card>
        {error && <ErrorMessage message={error} variant="error" />}
        {success && (
          <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
            {success}
          </div>
        )}

        <form onSubmit={handleUpdate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Student ID
              </label>
              <input
                type="text"
                value={student.id}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                User ID
              </label>
              <input
                type="text"
                value={student.user_id}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-600"
              />
            </div>

            <Input
              label="Age"
              id="age"
              name="age"
              type="number"
              value={formData.age}
              onChange={handleInputChange}
              disabled={!canEdit}
              placeholder="Enter age"
            />

            <Input
              label="Autism Type"
              id="autism_type"
              name="autism_type"
              type="text"
              value={formData.autism_type}
              onChange={handleInputChange}
              disabled={!canEdit}
              placeholder="Enter autism type"
            />

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sensitivities
              </label>
              <textarea
                id="sensitivities"
                name="sensitivities"
                value={formData.sensitivities}
                onChange={handleInputChange}
                disabled={!canEdit}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-600"
                placeholder="Enter sensitivities"
              />
            </div>

            <Input
              label="Learning Style"
              id="learning_style"
              name="learning_style"
              type="text"
              value={formData.learning_style}
              onChange={handleInputChange}
              disabled={!canEdit}
              placeholder="Enter learning style"
            />

            <Input
              label="Baseline Engagement"
              id="baseline_engagement"
              name="baseline_engagement"
              type="number"
              step="0.01"
              value={formData.baseline_engagement}
              onChange={handleInputChange}
              disabled={!canEdit}
              placeholder="Enter baseline engagement"
            />
          </div>

          {canEdit && (
            <div className="flex justify-end space-x-4 pt-4">
              <Button
                type="button"
                variant="secondary"
                onClick={loadStudent}
                disabled={saving}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={saving}
                loading={saving}
              >
                {saving ? "Saving..." : "Update Student"}
              </Button>
            </div>
          )}

          {!canEdit && (
            <div className="mt-4 p-3 bg-yellow-100 text-yellow-700 rounded text-sm">
              You don't have permission to edit this profile. Only parents and teachers can edit student profiles.
            </div>
          )}
        </form>
      </Card>
    </div>
  );
}
