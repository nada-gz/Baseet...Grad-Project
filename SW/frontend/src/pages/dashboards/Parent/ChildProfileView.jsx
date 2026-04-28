import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, Cell 
} from "recharts";
import { 
  ChevronLeft, 
  Download, 
  BookOpen, 
  Smile, 
  Clock, 
  Target, 
  Zap, 
  Users,
  Compass,
  Lightbulb,
  FileText,
  TrendingUp,
  ChevronRight
} from "lucide-react";
import { motion } from "framer-motion";
import api from "../../../services/api";

export default function ChildProfileView() {
  const { studentId } = useParams();
  const [activeTab, setActiveTab] = useState("academic");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await api.get(`/parent/child/${studentId}/insights`);
        setData(response.data);
      } catch (err) {
        console.error("Error fetching insights:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, [studentId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!data) return <div className="p-8 text-center text-slate-500">No data found for this student.</div>;

  const sentimentData = data.sentiment_trend.values.map((val, idx) => ({
    day: data.sentiment_trend.labels[idx],
    value: val
  }));

  return (
    <div className="min-h-screen bg-[#FDFEFF] p-4 md:p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div className="flex items-center gap-4">
          <Link to="/dashboard/parent" className="p-2 hover:bg-slate-100 rounded-full transition-colors">
            <ChevronLeft size={24} className="text-slate-600" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-slate-800">{data.child_name}'s Profile</h1>
            <p className="text-slate-500">Academic & Emotional Insights</p>
          </div>
        </div>
        
        <button className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-2xl font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all active:scale-95">
          <Download size={20} />
          Download Summary
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 p-1 bg-slate-100 rounded-2xl w-fit mb-8">
        <button 
          onClick={() => setActiveTab("academic")}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold transition-all ${
            activeTab === "academic" ? "bg-white text-indigo-600 shadow-sm" : "text-slate-500 hover:text-slate-700"
          }`}
        >
          <BookOpen size={18} />
          Academic Insights
        </button>
        <button 
          onClick={() => setActiveTab("emotional")}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold transition-all ${
            activeTab === "emotional" ? "bg-white text-rose-600 shadow-sm" : "text-slate-500 hover:text-slate-700"
          }`}
        >
          <Smile size={18} />
          Emotional Insights
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Stats & Charts */}
        <div className="lg:col-span-2 space-y-8">
          {activeTab === "academic" ? (
            <>
              {/* Academic Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <AcademicStatCard 
                  icon={<Clock className="text-blue-500" />} 
                  label="Study Hours" 
                  value={data.time_well_spent.study_hours_today}
                  sub="Today's goal: 3h"
                />
                <AcademicStatCard 
                  icon={<Target className="text-purple-500" />} 
                  label="Focus Score" 
                  value={data.time_well_spent.focus_score}
                  sub="Consistent with yesterday"
                />
                <AcademicStatCard 
                  icon={<Zap className="text-amber-500" />} 
                  label="Calm Percentage" 
                  value={data.time_well_spent.calm_percentage}
                  sub="Excellent regulation"
                />
              </div>

              {/* Learning Journey Map */}
              <section className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100">
                <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                  <Compass className="text-indigo-500" size={24} />
                  Learning Journey
                </h3>
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-100"></div>
                  <div className="space-y-8">
                    {data.learning_journey_map.map((item, idx) => (
                      <motion.div 
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        className="flex items-start gap-8 relative z-10"
                      >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center border-4 border-white shadow-sm ${
                          item.success === true ? 'bg-emerald-500' : 'bg-slate-300'
                        }`}>
                          {item.success === true && <div className="w-2 h-2 bg-white rounded-full"></div>}
                        </div>
                        <div className="bg-slate-50 rounded-2xl p-4 flex-1">
                          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{item.stage}</span>
                          <h4 className="font-bold text-slate-800">{item.activity}</h4>
                          <p className="text-sm text-slate-500">
                            {item.success === true ? "Successfully completed" : "Ongoing activity"}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </section>
            </>
          ) : (
            <>
              {/* Emotional Snapshots */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <AcademicStatCard 
                  icon={<Smile className="text-rose-500" />} 
                  label="Overall Mood" 
                  value={data.daily_snapshot.overall_mood}
                  sub="Vibrant and happy"
                />
                <AcademicStatCard 
                  icon={<Zap className="text-orange-500" />} 
                  label="Energy Level" 
                  value={data.daily_snapshot.energy_level}
                  sub="High but regulated"
                />
                <AcademicStatCard 
                  icon={<Users className="text-indigo-500" />} 
                  label="Social Engagement" 
                  value={data.daily_snapshot.social_engagement}
                  sub="Great interactions"
                />
              </div>

              {/* Sentiment Trend Chart */}
              <section className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100">
                <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                  <TrendingUp className="text-rose-500" size={24} />
                  Sentiment Trend (Weekly)
                </h3>
                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={sentimentData}>
                      <defs>
                        <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.1}/>
                          <stop offset="95%" stopColor="#F43F5E" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis 
                        dataKey="day" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{fill: '#94a3b8', fontSize: 12}}
                        dy={10}
                      />
                      <YAxis hide />
                      <Tooltip 
                        contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#F43F5E" 
                        strokeWidth={3}
                        fillOpacity={1} 
                        fill="url(#colorVal)" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </section>
            </>
          )}
        </div>

        {/* Right Column: Parent Toolkit */}
        <div className="space-y-8">
          <section className="bg-indigo-600 rounded-[2rem] p-8 text-white shadow-xl shadow-indigo-100 relative overflow-hidden">
            <div className="absolute -top-12 -right-12 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
            
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Lightbulb className="text-amber-300" size={24} />
              Parent Toolkit
            </h3>
            
            <div className="space-y-6">
              <div>
                <h4 className="text-indigo-200 text-xs font-bold uppercase tracking-widest mb-2">Discuss Today</h4>
                <p className="text-lg leading-relaxed font-medium">"{data.parent_toolkit.discuss_today}"</p>
              </div>
              
              <div className="bg-white/10 rounded-2xl p-4 backdrop-blur-md border border-white/10">
                <h4 className="text-indigo-200 text-xs font-bold uppercase tracking-widest mb-2">Suggested Activity</h4>
                <p className="text-sm leading-relaxed">{data.parent_toolkit.suggested_activity}</p>
              </div>

              <div>
                <h4 className="text-indigo-200 text-xs font-bold uppercase tracking-widest mb-3">New Words Learned</h4>
                <div className="flex flex-wrap gap-2">
                  {data.parent_toolkit.new_words.map((word, i) => (
                    <span key={i} className="px-4 py-1.5 bg-white/20 rounded-full text-sm font-bold border border-white/10">
                      {word}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <section className="bg-slate-50 border border-slate-100 rounded-[2rem] p-8">
            <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
              <FileText className="text-slate-400" size={24} />
              Resources
            </h3>
            <p className="text-slate-500 text-sm mb-6">Hand-picked resources to help you support {data.child_name}'s learning journey.</p>
            <div className="space-y-3">
              <ResourceItem title="Supporting Sensory Needs" />
              <ResourceItem title="Positive Reinforcement Tips" />
              <ResourceItem title="Understanding Math Progress" />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function AcademicStatCard({ icon, label, value, sub }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm"
    >
      <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center mb-4">
        {icon}
      </div>
      <p className="text-slate-400 text-sm font-medium">{label}</p>
      <h4 className="text-2xl font-black text-slate-800 my-1">{value}</h4>
      <p className="text-xs text-slate-400">{sub}</p>
    </motion.div>
  );
}

function ResourceItem({ title }) {
  return (
    <div className="flex items-center justify-between p-4 bg-white rounded-2xl hover:bg-slate-100 transition-colors cursor-pointer group">
      <span className="text-sm font-bold text-slate-700">{title}</span>
      <ChevronRight size={16} className="text-slate-300 group-hover:text-indigo-600 transition-colors" />
    </div>
  );
}
