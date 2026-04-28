import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { 
  ChevronLeft, 
  Save, 
  Settings2, 
  Volume2, 
  Sun, 
  Type, 
  Gamepad2,
  CheckCircle2,
  Clock
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import api from "../../../services/api";

export default function ChildPreferences() {
  const { studentId } = useParams();
  const [difficulty, setDifficulty] = useState(5);
  const [sensorySettings, setSensorySettings] = useState({
    reducedBrightness: false,
    simplifiedAudio: false,
    highContrast: false,
    extraResponseTime: true,
  });
  const [saving, setSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [childName, setChildName] = useState("Child");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get("/parent/my-children");
        const child = response.data.find(c => c.id === parseInt(studentId));
        if (child) {
          setChildName(child.name);
          setDifficulty(child.difficulty_level || 5);
          if (child.sensory_settings) {
            setSensorySettings(child.sensory_settings);
          }
        }
      } catch (err) {
        console.error("Error fetching child data:", err);
      }
    };
    fetchData();
  }, [studentId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.patch(`/parent/child/${studentId}/preferences`, {
        difficulty_level: difficulty,
        sensory_settings: sensorySettings
      });
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

  return (
    <div className="min-h-screen bg-[#FAFBFF] p-4 md:p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div className="flex items-center gap-4">
          <Link to="/dashboard/parent" className="p-2 hover:bg-slate-100 rounded-full transition-colors">
            <ChevronLeft size={24} className="text-slate-600" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-slate-800">Personalize Settings</h1>
            <p className="text-slate-500">Adjust the experience for {childName}</p>
          </div>
        </div>
        
        <button 
          onClick={handleSave}
          disabled={saving}
          className={`flex items-center gap-2 px-8 py-4 bg-emerald-600 text-white rounded-2xl font-bold shadow-lg shadow-emerald-100 hover:bg-emerald-700 transition-all active:scale-95 ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {saving ? (
            <div className="w-5 h-5 border-2 border-white border-b-transparent rounded-full animate-spin"></div>
          ) : (
            <Save size={20} />
          )}
          {saving ? "Saving..." : "Save Preferences"}
        </button>
      </div>

      <AnimatePresence>
        {showSuccess && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mb-6 p-4 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center gap-3 text-emerald-800"
          >
            <CheckCircle2 size={20} className="text-emerald-500" />
            <span className="font-bold">Preferences saved successfully!</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Difficulty Scale */}
        <section className="bg-white rounded-[2.5rem] p-10 shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-3 bg-indigo-100 text-indigo-600 rounded-2xl">
              <Gamepad2 size={24} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-slate-800">Difficulty Level</h3>
              <p className="text-slate-500">Tailor the academic challenges to {childName}'s current level.</p>
            </div>
          </div>

          <div className="py-12 px-4">
            <input 
              type="range" 
              min="1" 
              max="10" 
              value={difficulty}
              onChange={(e) => setDifficulty(parseInt(e.target.value))}
              className="w-full h-4 bg-slate-100 rounded-full appearance-none cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between mt-6 px-2">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(val => (
                <span key={val} className={`text-sm font-bold ${difficulty === val ? 'text-indigo-600' : 'text-slate-300'}`}>
                  {val}
                </span>
              ))}
            </div>
            
            <div className="mt-12 p-6 bg-slate-50 rounded-3xl text-center">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">Current Setting</span>
              <p className="text-4xl font-black text-indigo-600">Level {difficulty}</p>
              <p className="text-slate-500 mt-2 text-sm">
                {difficulty <= 3 ? "Beginner: Focus on basics and core concepts." : 
                 difficulty <= 7 ? "Intermediate: Balanced mix of review and new content." : 
                 "Advanced: Faster pace with more complex challenges."}
              </p>
            </div>
          </div>
        </section>

        {/* Sensory Settings */}
        <section className="bg-white rounded-[2.5rem] p-10 shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-3 bg-rose-100 text-rose-600 rounded-2xl">
              <Settings2 size={24} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-slate-800">Sensory Preferences</h3>
              <p className="text-slate-500">Customize visual and auditory elements for comfort.</p>
            </div>
          </div>

          <div className="space-y-6">
            <ToggleOption 
              icon={<Sun size={20} />}
              title="Reduced Brightness"
              desc="Softer colors and lower contrast for light sensitivity."
              active={sensorySettings.reducedBrightness}
              onToggle={() => toggleSensory('reducedBrightness')}
              color="amber"
            />
            <ToggleOption 
              icon={<Volume2 size={20} />}
              title="Simplified Audio"
              desc="Minimize background sounds and use clearer narration."
              active={sensorySettings.simplifiedAudio}
              onToggle={() => toggleSensory('simplifiedAudio')}
              color="blue"
            />
            <ToggleOption 
              icon={<Type size={20} />}
              title="High Contrast"
              desc="Make text and UI elements easier to distinguish."
              active={sensorySettings.highContrast}
              onToggle={() => toggleSensory('highContrast')}
              color="slate"
            />
            <ToggleOption 
              icon={<Clock size={20} />}
              title="Extra Response Time"
              desc="Allow more time for tasks and interactions."
              active={sensorySettings.extraResponseTime}
              onToggle={() => toggleSensory('extraResponseTime')}
              color="indigo"
            />
          </div>
        </section>
      </div>
    </div>
  );
}

function ToggleOption({ icon, title, desc, active, onToggle, color }) {
  const colors = {
    amber: "bg-amber-100 text-amber-600",
    blue: "bg-blue-100 text-blue-600",
    slate: "bg-slate-100 text-slate-600",
    indigo: "bg-indigo-100 text-indigo-600"
  };

  return (
    <div className="flex items-center gap-4 p-6 bg-slate-50 rounded-3xl border border-transparent hover:border-slate-200 transition-all">
      <div className={`p-4 rounded-2xl ${colors[color] || colors.indigo}`}>
        {icon}
      </div>
      <div className="flex-1">
        <h4 className="font-bold text-slate-800">{title}</h4>
        <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
      </div>
      <button 
        onClick={onToggle}
        className={`w-14 h-8 rounded-full relative transition-colors ${active ? 'bg-indigo-600' : 'bg-slate-300'}`}
      >
        <motion.div 
          animate={{ x: active ? 24 : 4 }}
          className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-sm"
        />
      </button>
    </div>
  );
}
