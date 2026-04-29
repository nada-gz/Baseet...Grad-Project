import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  Bell, 
  MessageSquare, 
  AlertTriangle, 
  CheckCircle2, 
  ChevronRight,
  Clock
} from "lucide-react";
import api from "../../../services/api";

export default function ParentNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await api.get("/parent/notifications");
        setNotifications(response.data);
      } catch (err) {
        console.error("Error fetching notifications:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchNotifications();
  }, []);

  const filteredNotifications = notifications.filter(n => {
    if (filter === "all") return true;
    if (filter === "urgent") return n.is_urgent;
    if (filter === "feedback") return n.type === "feedback";
    if (filter === "comments") return n.type === "comment";
    return true;
  });

  if (loading) {
    return <div className="status checking p-10">Loading notifications...</div>;
  }

  return (
    <div className="parent-dashboard-wrapper">
      <div style={{ marginBottom: "40px" }}>
        <h1 className="topbar-title" style={{ fontSize: "2.5rem", marginBottom: "10px" }}>Notification Center</h1>
        <p style={{ color: "var(--secondary-text)" }}>Stay updated on your child's progress and alerts.</p>
      </div>

      <div className="parent-tabs">
        <button className={`parent-tab ${filter === "all" ? "active" : ""}`} onClick={() => setFilter("all")}>All</button>
        <button className={`parent-tab ${filter === "urgent" ? "active" : ""}`} onClick={() => setFilter("urgent")}>Urgent</button>
        <button className={`parent-tab ${filter === "feedback" ? "active" : ""}`} onClick={() => setFilter("feedback")}>Feedback</button>
        <button className={`parent-tab ${filter === "comments" ? "active" : ""}`} onClick={() => setFilter("comments")}>Comments</button>
      </div>

      <div className="notification-feed">
        {filteredNotifications.length > 0 ? (
          filteredNotifications.map((note, idx) => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className={`notification-item ${note.is_urgent ? 'urgent' : ''}`}
            >
              <div className="notification-icon-box" style={{ 
                background: note.is_urgent ? "var(--error-bg)" : "var(--primary-bg)",
                color: note.is_urgent ? "white" : "var(--highlight)"
              }}>
                {note.is_urgent ? <AlertTriangle size={24} /> : 
                 note.type === 'comment' ? <MessageSquare size={24} /> : 
                 <CheckCircle2 size={24} />}
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <h3 style={{ margin: 0 }}>{note.title}</h3>
                  <span style={{ fontSize: "0.8rem", color: "var(--secondary-text)", display: "flex", alignItems: "center", gap: "5px" }}>
                    <Clock size={12} />
                    {new Date(note.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p>{note.message}</p>

                {note.is_urgent && (
                  <div style={{ marginTop: "15px", display: "flex", gap: "10px" }}>
                    <Link 
                      to={`/dashboard/parent/students`} 
                      className="btn btn-calm"
                      style={{ padding: "8px 15px", fontSize: "0.8rem" }}
                    >
                      View Child Insights <ChevronRight size={14} />
                    </Link>
                  </div>
                )}
              </div>
            </motion.div>
          ))
        ) : (
          <div className="parent-card" style={{ textAlign: "center", padding: "80px" }}>
            <Bell size={48} style={{ opacity: 0.1, marginBottom: "20px" }} />
            <p>No notifications in this category.</p>
          </div>
        )}
      </div>
    </div>
  );
}
