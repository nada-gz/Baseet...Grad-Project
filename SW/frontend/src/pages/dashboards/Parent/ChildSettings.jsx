import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ChevronLeft, 
  Save, 
  Gamepad2, 
  Settings2, 
  Volume2, 
  Sun, 
  Type, 
  Clock,
  CheckCircle2
} from "lucide-react";
import api from "../../../services/api";

export default function ChildSettings() {
  const { studentId: paramId } = useParams();
  const [children, setChildren] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState(paramId || "");
  const [difficulty, setDifficulty] = useState(5);
  const [sensorySettings, setSensorySettings] = useState({
    reducedBrightness: false,
    simplifiedAudio: false,
    highContrast: false,
    extraResponseTime: true,
  });
  const [saving, setSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get("/parent/my-children");
        setChildren(response.data);
        
        const targetId = paramId || (response.data.length > 0 ? response.data[0].id.toString() : "");
        setSelectedChildId(targetId);
      } catch (err) {
        console.error("Error fetching settings data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [paramId]);

  // Sync form values when selected child changes
  useEffect(() => {
    if (children.length > 0 && selectedChildId) {
      const child = children.find(c => c.id.toString() === selectedChildId);
      if (child) {
        setDifficulty(child.difficulty_level || 5);
        if (child.sensory_settings) {
          setSensorySettings(child.sensory_settings);
        } else {
          // Default if none set
          setSensorySettings({
            reducedBrightness: false,
            simplifiedAudio: false,
            highContrast: false,
            extraResponseTime: true,
          });
        }
      }
    }
  }, [selectedChildId, children]);

  const handleSave = async () => {
    if (!selectedChildId) return;
    setSaving(true);
    try {
      await api.patch(`/parent/child/${selectedChildId}/preferences`, {
        difficulty_level: difficulty,
        sensory_settings: sensorySettings
      });
      
      // Update local children list so the state is preserved if we switch back and forth
      setChildren(prev => prev.map(c => 
        c.id.toString() === selectedChildId 
          ? { ...c, difficulty_level: difficulty, sensory_settings: sensorySettings }
          : c
      ));

      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      console.error("Error saving preferences:", err);
    } finally {
      setSaving(false);
    }
  };

  const toggleSensory = (key) => {
    setSensorySettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  if (loading) {
    return <div className="status checking p-10">Loading preferences...</div>;
  }

  const selectedChild = children.find(c => c.id.toString() === selectedChildId);

  return (
    <div className="parent-dashboard-wrapper">
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "40px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <Link to="/dashboard/parent" className="btn btn-outline" style={{ borderRadius: "15px", padding: "10px" }}>
            <ChevronLeft size={24} />
          </Link>
          <div>
            <h1 className="topbar-title" style={{ fontSize: "2.5rem" }}>Learning Preferences</h1>
            <p style={{ color: "var(--secondary-text)" }}>Tailor the environment for your child.</p>
          </div>
        </div>

        <button 
          onClick={handleSave}
          disabled={saving || !selectedChildId}
          className="btn btn-primary"
          style={{ padding: "15px 40px", borderRadius: "2rem" }}
        >
          {saving ? "Saving..." : <><Save size={20} style={{ marginRight: "10px" }} /> Save Changes</>}
        </button>
      </div>

      <AnimatePresence>
        {showSuccess && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            style={{ 
              marginBottom: "25px", 
              padding: "15px 25px", 
              background: "var(--highlight)", 
              color: "white", 
              borderRadius: "15px",
              display: "flex",
              alignItems: "center",
              fontWeight: "700",
              boxShadow: "0 10px 20px rgba(108, 99, 255, 0.2)"
            }}
          >
            <CheckCircle2 size={20} style={{ marginRight: "12px" }} />
            Settings updated successfully for {selectedChild?.name}!
          </motion.div>
        )}
      </AnimatePresence>

      <div className="parent-grid" style={{ gridTemplateColumns: "2fr 1fr" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "30px" }}>
          {/* Child Selector */}
          <div className="parent-card">
            <h3 style={{ fontSize: "1.2rem", fontWeight: "800", marginBottom: "20px" }}>Select Child Profile</h3>
            <div style={{ display: "flex", gap: "10px" }}>
              {children.map(child => (
                <button
                  key={child.id}
                  onClick={() => setSelectedChildId(child.id.toString())}
                  className={`parent-tab ${selectedChildId === child.id.toString() ? 'active' : ''}`}
                  style={{ border: "2px solid var(--neutral)" }}
                >
                  {child.name}
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty Slider */}
          <div className="preference-slider-container">
            <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "40px" }}>
              <div style={{ background: "var(--primary-bg)", padding: "15px", borderRadius: "15px", color: "var(--highlight)" }}>
                <Gamepad2 size={32} />
              </div>
              <div>
                <h3 style={{ fontSize: "1.8rem", fontWeight: "900" }}>Difficulty Level</h3>
                <p style={{ color: "var(--secondary-text)" }}>Adjust the academic challenge level.</p>
              </div>
            </div>

            <div style={{ padding: "20px" }}>
              <input 
                type="range" 
                min="1" 
                max="10" 
                value={difficulty}
                onChange={(e) => setDifficulty(parseInt(e.target.value))}
                style={{ height: "12px", background: "var(--neutral)" }}
              />
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: "15px" }}>
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(val => (
                  <span key={val} style={{ fontSize: "0.8rem", fontWeight: "900", color: difficulty === val ? "var(--highlight)" : "var(--neutral)" }}>{val}</span>
                ))}
              </div>

              <div style={{ marginTop: "40px", background: "var(--primary-bg)", padding: "30px", borderRadius: "20px", textAlign: "center" }}>
                <p style={{ fontSize: "0.75rem", fontWeight: "900", color: "var(--secondary-text)", textTransform: "uppercase", marginBottom: "10px" }}>Current Intensity</p>
                <p style={{ fontSize: "3rem", fontWeight: "950", color: "var(--highlight)" }}>Level {difficulty}</p>
                <p style={{ color: "var(--secondary-text)", marginTop: "10px", maxWidth: "400px", margin: "10px auto" }}>
                  {difficulty <= 3 ? "Basics: Slow-paced with frequent repetitions and simplified concepts." : 
                   difficulty <= 7 ? "Balanced: Standard progression with adaptive feedback loops." : 
                   "Advanced: Fast-paced with complex problem solving and minimal review."}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Sensory Settings */}
        <div className="parent-card" style={{ alignSelf: "start" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "30px" }}>
            <Settings2 size={24} color="var(--secondary-color)" />
            <h3 style={{ fontWeight: "900" }}>Sensory Profile</h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
            <SensoryToggleCard 
              icon={<Sun size={20} />} 
              title="Soft Visuals" 
              desc="Low intensity colors."
              active={sensorySettings.reducedBrightness}
              onToggle={() => toggleSensory('reducedBrightness')}
            />
            <SensoryToggleCard 
              icon={<Volume2 size={20} />} 
              title="Audio Focus" 
              desc="Mute ambient noise."
              active={sensorySettings.simplifiedAudio}
              onToggle={() => toggleSensory('simplifiedAudio')}
            />
            <SensoryToggleCard 
              icon={<Type size={20} />} 
              title="High Legibility" 
              desc="Larger, bolder fonts."
              active={sensorySettings.highContrast}
              onToggle={() => toggleSensory('highContrast')}
            />
            <SensoryToggleCard 
              icon={<Clock size={20} />} 
              title="Patient Mode" 
              desc="Extra response time."
              active={sensorySettings.extraResponseTime}
              onToggle={() => toggleSensory('extraResponseTime')}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function SensoryToggleCard({ icon, title, desc, active, onToggle }) {
  return (
    <div className="sensory-toggle-card">
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{ color: active ? "var(--highlight)" : "var(--secondary-text)" }}>{icon}</div>
        <div className="sensory-info">
          <h4 style={{ fontSize: "0.9rem" }}>{title}</h4>
          <p style={{ fontSize: "0.75rem" }}>{desc}</p>
        </div>
      </div>
      <button 
        onClick={onToggle}
        style={{ 
          width: "44px", 
          height: "22px", 
          borderRadius: "20px", 
          background: active ? "var(--highlight)" : "var(--neutral)",
          border: "none",
          position: "relative",
          cursor: "pointer"
        }}
      >
        <div style={{ 
          position: "absolute", 
          top: "2px", 
          left: active ? "24px" : "2px", 
          width: "18px", 
          height: "18px", 
          background: "white", 
          borderRadius: "50%",
          transition: "left 0.2s"
        }} />
      </button>
    </div>
  );
}
