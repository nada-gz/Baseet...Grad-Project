import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import useAuth from "../../hooks/useAuth";
import api from "../../services/api";

const StudentProfile = () => {
  const { user, loading: authLoading } = useAuth(); 
  const { id: studentId } = useParams();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const isEditable = !authLoading && user && (user.role === "Teacher" || user.role === "Parent");

  useEffect(() => {
    if (!user) return; 

    let isMounted = true;

    const fetchProfile = async () => {
      setLoading(true);
      try {
        const response = await api.get(`/students/${studentId}`);
        if (!isMounted) return;

        const data = response.data;

        setProfile({
          age: data.age ?? "",
          autismType: data.autism_type ?? "",
          sensitivities: data.sensitivities ?? "",
          learningStyle: data.learning_style ?? "",
          baselineEngagement: data.baseline_engagement ?? "",
        });

      } catch (err) {
        console.error("Error fetching profile:", err);
        alert("Failed to load student profile");
        if (isMounted) {
          setProfile({
            age: "",
            autismType: "",
            sensitivities: "",
            learningStyle: "",
            baselineEngagement: "",
          });
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchProfile();

    return () => {
      isMounted = false;
    };
  }, [studentId, user]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put(`/students/${studentId}`, {
        age: profile.age,
        autism_type: profile.autismType,
        sensitivities: profile.sensitivities,
        learning_style: profile.learningStyle,
        baseline_engagement: profile.baselineEngagement,
      });
      alert("Profile saved successfully!");
    } catch (err) {
      console.error("Error saving profile:", err);
      alert("Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading || profile === null) {
    return (
      <div className="max-w-3xl mx-auto p-6 bg-white rounded shadow animate-pulse">
        <div className="h-6 bg-gray-300 rounded mb-4 w-1/3"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-10 bg-gray-200 rounded mb-3"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded shadow">
      <h1 className="text-2xl font-semibold mb-6">Student Profile</h1>

      <form className="space-y-4" onSubmit={handleSave}>
        <Input
          label="Age"
          value={profile.age}
          readOnly={!isEditable}
          onChange={(e) => setProfile({ ...profile, age: e.target.value })}
        />
        <Input
          label="Autism Type"
          value={profile.autismType}
          readOnly={!isEditable}
          onChange={(e) =>
            setProfile({ ...profile, autismType: e.target.value })
          }
        />
        <Input
          label="Sensitivities"
          value={profile.sensitivities}
          readOnly={!isEditable}
          onChange={(e) =>
            setProfile({ ...profile, sensitivities: e.target.value })
          }
        />
        <Input
          label="Learning Style"
          value={profile.learningStyle}
          readOnly={!isEditable}
          onChange={(e) =>
            setProfile({ ...profile, learningStyle: e.target.value })
          }
        />
        <Input
          label="Baseline Engagement"
          value={profile.baselineEngagement}
          readOnly={!isEditable}
          onChange={(e) =>
            setProfile({ ...profile, baselineEngagement: e.target.value })
          }
        />

        {isEditable && (
          <Button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </Button>
        )}
      </form>
    </div>
  );
};

export default StudentProfile;
