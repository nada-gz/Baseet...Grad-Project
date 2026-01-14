import { Outlet, Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  BookOpen,
  Folder,
  ClipboardList,
  HelpCircle,
  PlayCircle,
  Users,
  School
} from "lucide-react";
import Logo from "../components/ui/logo";
import HiBaseet from "../assets/hii_baseet.png";

export default function MainLayout() {
  const { role, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const getSidebarItems = () => {
    switch (role) {
      case "teacher":
        return [
          {
            label: "Students",
            path: "/dashboard/teacher/students",
            icon: <Users size={20} />
          },
          {
            label: "Classrooms",
            path: "/dashboard/teacher/classrooms",
            icon: <School size={20} />
          },
          {
            label: "Content",
            path: "/dashboard/teacher/lessons-prep",
            icon: <BookOpen size={20} />
          }
        ];

      case "parent":
        return [
          { label: "Child Progress", path: "/dashboard/parent/progress", icon: "📊" },
          { label: "Reports", path: "/dashboard/parent/reports", icon: "📄" }
        ];

      case "student":
        return [
          {
            label: "Lessons",
            path: "/dashboard/student/lessons",
            icon: <BookOpen size={20} />
          },
          {
            label: "Materials",
            path: "/dashboard/student/materials",
            icon: <Folder size={20} />
          },
          {
            label: "Assignments",
            path: "/dashboard/student/assignments",
            icon: <ClipboardList size={20} />
          },
          {
            label: "Quizzes",
            path: "/dashboard/student/quizzes",
            icon: <HelpCircle size={20} />
          },
          {
            label: "Ask Baseet",
            path: "/dashboard/student/ask-baseet",
            icon: (
              <img
                src={require("../assets/eyes_baseet.png")}
                alt="Ask Baseet"
                style={{ width: 80, height: 80 }}
              />
            )
          }
        ];

      case "supervisor":
        return [
          { label: "Analytics", path: "/dashboard/supervisor/analytics", icon: "📈" },
          { label: "Student List", path: "/dashboard/supervisor/students", icon: "👨‍🎓" }
        ];

      default:
        return [];
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const sidebarItems = getSidebarItems();

  const renderTopbarExtras = () => {
    if (!user) return null;

    if (role === "student") {
      return (
        <>
          <Link to="/dashboard/student" className="topbar-continue">
            <PlayCircle size={20} />
            <span>Continue</span>
          </Link>

          <div className="topbar-actions">
            <Link to="/dashboard/student/analytics" className="topbar-link">
              Analytics
            </Link>
            <Link to={`/students/${user.id}/profile`} className="topbar-link">
              My Profile
            </Link>
          </div>
        </>
      );
    }

    if (role === "teacher") {
      return (
        <div className="topbar-actions">
          <Link to="/dashboard/teacher" className="topbar-link">
            Home
          </Link>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div>
          <div className="sidebar-logo">
            <Logo />
          </div>

          <div
            className="sidebar-role-container"
            style={{ textAlign: "center", marginBottom: "20px" }}
          >
            <p className="sidebar-role">{role} Portal</p>
          </div>

          <nav className="sidebar-menu">
            {sidebarItems.map((item) => {
              const isActive =
                location.pathname === item.path ||
                location.pathname.startsWith(item.path + "/");

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`sidebar-link ${isActive ? "active" : ""}`}
                >
                  <span className="sidebar-icon">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="sidebar-footer">
          <div className="user-name">{user?.email}</div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main">
        <header className="topbar">
          <h2 className="topbar-title">
            {sidebarItems.find(
              (item) =>
                location.pathname === item.path ||
                location.pathname.startsWith(item.path + "/")
            )?.label || (
                <span className="topbar-greeting">
                  Hi, {user?.username || "there"}
                  {role === "student" && (
                    <img
                      src={HiBaseet}
                      alt="Hi Baseet"
                      className="topbar-hi-icon"
                    />
                  )}
                </span>
              )}
          </h2>

          <div className="topbar-user">
            {renderTopbarExtras()}
            <Link to="/account" className="avatar avatar-clickable">
              {user?.username?.[0]?.toUpperCase()}
            </Link>
          </div>
        </header>

        <div className="content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
