import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bell, 
  User, 
  Settings, 
  TrendingUp, 
  Activity, 
  MessageSquare, 
  AlertTriangle,
  ChevronRight,
  Heart
} from "lucide-react";
import useAuth from "../../hooks/useAuth";
import api from "../../services/api";

export default function ParentDashboard() {
  const { user } = useAuth();
  const [children, setChildren] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [childrenRes, notifyRes] = await Promise.all([
          api.get("/parent/my-children"),
          api.get("/parent/notifications")
        ]);
        setChildren(childrenRes.data);
        setNotifications(notifyRes.data);
      } catch (err) {
        console.error("Error fetching parent data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const urgentAlerts = notifications.filter(n => n.is_urgent && !n.is_read);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-4 md:p-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl md:text-4xl font-bold text-slate-800"
          >
            Welcome back, <span className="text-indigo-600">{user?.username}</span>!
          </motion.h1>
          <p className="text-slate-500 mt-1">Here's what's happening with your children today.</p>
        </div>
        
        <div className="flex items-center gap-3 bg-white p-2 rounded-2xl shadow-sm border border-slate-100">
          <div className="relative p-2 text-slate-600 hover:bg-slate-50 rounded-xl transition-colors cursor-pointer">
            <Bell size={20} />
            {notifications.some(n => !n.is_read) && (
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            )}
          </div>
          <div className="h-8 w-[1px] bg-slate-100 mx-1"></div>
          <div className="flex items-center gap-2 pl-2 pr-1">
            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content: Children Cards */}
        <div className="lg:col-span-2 space-y-6">
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <Heart className="text-rose-500" size={24} />
                My Children
              </h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {children.length > 0 ? (
                children.map((child, index) => (
                  <motion.div
                    key={child.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="group bg-white rounded-3xl p-6 shadow-sm hover:shadow-xl transition-all border border-slate-100 overflow-hidden relative"
                  >
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                      <User size={80} />
                    </div>
                    
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                        {child.name.charAt(0)}
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-slate-800">{child.name}</h3>
                        <p className="text-slate-500 text-sm">Age: {child.age || "N/A"}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 mb-6">
                      <div className="bg-slate-50 p-3 rounded-2xl">
                        <p className="text-xs text-slate-400 uppercase font-bold tracking-wider">Difficulty</p>
                        <p className="text-lg font-bold text-indigo-600">Lvl {child.difficulty_level}</p>
                      </div>
                      <div className="bg-slate-50 p-3 rounded-2xl">
                        <p className="text-xs text-slate-400 uppercase font-bold tracking-wider">Status</p>
                        <p className="text-lg font-bold text-emerald-600">Active</p>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <Link 
                        to={`/dashboard/parent/child/${child.id}/insights`}
                        className="w-full py-3 bg-indigo-600 text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-indigo-700 transition-colors"
                      >
                        <TrendingUp size={18} />
                        View Insights
                      </Link>
                      <Link 
                        to={`/dashboard/parent/child/${child.id}/settings`}
                        className="w-full py-3 bg-slate-50 text-slate-600 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-slate-100 transition-colors border border-slate-200"
                      >
                        <Settings size={18} />
                        Personalize Settings
                      </Link>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="col-span-full bg-indigo-50 border-2 border-dashed border-indigo-200 rounded-3xl p-12 text-center">
                  <User className="mx-auto text-indigo-300 mb-4" size={48} />
                  <h3 className="text-xl font-bold text-indigo-800">No children linked yet</h3>
                  <p className="text-indigo-600 mt-2">Contact your school or use a link code to connect.</p>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Sidebar: Notifications & Alerts */}
        <div className="space-y-6">
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
            <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Bell className="text-indigo-500" size={24} />
              Notifications
            </h2>
            
            <AnimatePresence>
              {urgentAlerts.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="mb-4 bg-rose-50 border border-rose-100 rounded-2xl p-4 flex items-start gap-3"
                >
                  <div className="bg-rose-500 p-2 rounded-xl text-white animate-pulse">
                    <AlertTriangle size={18} />
                  </div>
                  <div>
                    <h4 className="font-bold text-rose-800">Urgent Alert</h4>
                    <p className="text-sm text-rose-600">{urgentAlerts[0].message}</p>
                    <button className="mt-2 text-sm font-bold text-rose-700 flex items-center gap-1 hover:underline">
                      Take Action <ChevronRight size={14} />
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="space-y-4">
              {notifications.length > 0 ? (
                notifications.slice(0, 5).map((note) => (
                  <div key={note.id} className="flex gap-4 p-2 hover:bg-slate-50 rounded-2xl transition-colors cursor-pointer">
                    <div className={`p-3 rounded-2xl ${
                      note.type === 'comment' ? 'bg-blue-100 text-blue-600' : 
                      note.type === 'feedback' ? 'bg-emerald-100 text-emerald-600' : 
                      'bg-slate-100 text-slate-600'
                    }`}>
                      {note.type === 'comment' ? <MessageSquare size={18} /> : 
                       note.type === 'feedback' ? <Activity size={18} /> : 
                       <Bell size={18} />}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-slate-800 text-sm">{note.title}</h4>
                      <p className="text-xs text-slate-500 line-clamp-1">{note.message}</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">
                        {new Date(note.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-slate-400 text-center py-8">No new notifications</p>
              )}
            </div>

            <button className="w-full mt-6 py-3 text-slate-500 font-bold text-sm hover:text-indigo-600 transition-colors">
              View All Notifications
            </button>
          </section>

          {/* Quick Stats/Insights Card */}
          <section className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl p-6 text-white shadow-lg">
            <h3 className="font-bold text-lg mb-2">Weekly Summary</h3>
            <p className="text-indigo-100 text-sm mb-6">Overall progress across all your children is increasing!</p>
            
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <span className="text-sm font-medium">Academic Focus</span>
                <span className="text-xl font-bold">85%</span>
              </div>
              <div className="w-full bg-indigo-900/30 rounded-full h-2">
                <div className="bg-white h-2 rounded-full w-[85%]"></div>
              </div>

              <div className="flex justify-between items-end">
                <span className="text-sm font-medium">Emotional Balance</span>
                <span className="text-xl font-bold">92%</span>
              </div>
              <div className="w-full bg-indigo-900/30 rounded-full h-2">
                <div className="bg-emerald-400 h-2 rounded-full w-[92%] shadow-[0_0_8px_rgba(52,211,153,0.6)]"></div>
              </div>
            </div>
            
            <button className="w-full mt-8 py-3 bg-white/10 hover:bg-white/20 rounded-2xl font-bold text-sm transition-all backdrop-blur-md">
              Download Full Report
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}
