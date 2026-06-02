import { useState, useEffect, useRef } from "react";
import { Outlet, Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  BookOpen,
  Folder,
  ClipboardList,
  HelpCircle,
  PlayCircle,
  Users,
  School,
  Moon,
  Sun,
  LayoutDashboard,
  Bell,
  Settings,
  Activity
} from "lucide-react";
import Logo from "../components/ui/logo";
import HiBaseet from "../assets/hii_baseet.png";
import VisualTimeStrip from "../components/ui/VisualTimeStrip";

export default function MainLayout() {
  const { role, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem("teacher-theme") === "dark";
  });
  const [topbarHeight, setTopbarHeight] = useState(80);
  const topbarRef = useRef(null);

  useEffect(() => {
    const updateTopbarHeight = () => {
      if (topbarRef.current) {
        setTopbarHeight(topbarRef.current.offsetHeight);
      }
    };
    // Initial check
    setTimeout(updateTopbarHeight, 100);
    window.addEventListener("resize", updateTopbarHeight);
    return () => window.removeEventListener("resize", updateTopbarHeight);
  }, [location.pathname]);

  useEffect(() => {
    if (role === "teacher") {
      if (isDarkMode) {
        document.body.classList.add("dark-theme");
        localStorage.setItem("teacher-theme", "dark");
      } else {
        document.body.classList.remove("dark-theme");
        localStorage.setItem("teacher-theme", "light");
      }
    } else {
      // Ensure other roles stay in light mode
      document.body.classList.remove("dark-theme");
    }
  }, [isDarkMode, role]);

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  const getSidebarItems = () => {
    switch (role) {
      case "teacher":
        return [
          {
            label: "Content",
            topbarLabel: "Content Preparation",
            path: "/dashboard/teacher/lessons-prep",
            icon: <BookOpen size={20} />
          },
          {
            label: "Classrooms",
            topbarLabel: "Classrooms Management",
            path: "/dashboard/teacher/classrooms",
            icon: <School size={20} />
          },
          {
            label: "Students",
            topbarLabel: "Students Monitoring",
            path: "/dashboard/teacher/students",
            icon: <Users size={20} />
          }
        ];

      case "parent":
        return [
          {
            label: "Dashboard",
            path: "/dashboard/parent",
            icon: <LayoutDashboard size={20} />,
          },
          {
            label: "Notifications",
            path: "/dashboard/parent/notifications",
            icon: <Bell size={20} />,
          },
          {
            label: "Child Insights",
            path: "/dashboard/parent/students",
            icon: <Users size={20} />,
          },
          {
            label: "Preferences",
            path: "/dashboard/parent/settings",
            icon: <Settings size={20} />,
          },
        ];

      case "student":
        return [
          {
            label: "Courses",
            path: "/dashboard/student/courses",
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
          {
            label: "Dashboard",
            path: "/dashboard/supervisor",
            icon: <LayoutDashboard size={20} />
          },
          {
            label: "Monitoring",
            path: "/dashboard/supervisor/monitoring",
            icon: <Activity size={20} />
          },
          {
            label: "Teachers",
            path: "/dashboard/supervisor/teachers",
            icon: <ClipboardList size={20} />
          },
          {
            label: "All Students",
            path: "/students",
            icon: <Users size={20} />
          }
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

    if (role === "student" || role === "parent") {
      return (
        <>
          {role === "student" && (
            <Link to="/dashboard/student" className="topbar-continue">
              <PlayCircle size={20} />
              <span>Continue</span>
            </Link>
          )}

          <div className="topbar-actions">
            {role === "student" ? (
              <>
                <Link to="/dashboard/student/analytics" className="topbar-link">
                  Analytics
                </Link>
                <Link to={`/students/${user.id}/profile`} className="topbar-link">
                  My Profile
                </Link>
              </>
            ) : (
              <Link to="/dashboard/parent/notifications" className="topbar-link">
                Alerts Center
              </Link>
            )}
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
          {role === "teacher" && (
            <div className="theme-toggle-container">
              <span className="theme-label">
                {isDarkMode ? "Dark Mode" : "Light Mode"}
              </span>
              <button
                className={`theme-toggle-btn ${isDarkMode ? 'active' : ''}`}
                onClick={toggleTheme}
                title="Toggle Theme"
              >
                <div className="toggle-thumb">
                  {isDarkMode ? <Moon size={14} /> : <Sun size={14} />}
                </div>
              </button>
            </div>
          )}
          <div className="user-name">{user?.email}</div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main">
        <header className="topbar" ref={topbarRef}>
          <h2 className="topbar-title">
            {(() => {
              const activeItem = sidebarItems.find(
                (item) =>
                  location.pathname === item.path ||
                  location.pathname.startsWith(item.path + "/")
              );
              const isHome = location.pathname === "/dashboard/parent" || 
                             location.pathname === "/dashboard/student" || 
                             location.pathname === "/dashboard/teacher" ||
                             location.pathname === "/dashboard/supervisor";
              
              // For parents and supervisors, show greeting on all pages but style it differently
              if (role === "parent" || role === "supervisor") {
                if (isHome) {
                  return (
                    <span className="topbar-greeting">
                      Hello, {user?.username || "there"}
                      {role === "parent" && <img src={HiBaseet} alt="Hi Baseet" className="topbar-hi-icon" />}
                    </span>
                  );
                } else {
                  return <span style={{ fontWeight: 600, color: "var(--secondary-text)" }}>{role === "supervisor" ? "Supervisor Control" : "Parent Access"}</span>;
                }
              }

              return (activeItem && !isHome) ? (activeItem.topbarLabel || activeItem.label) : (
                <span className="topbar-greeting">
                  Hello, {user?.username || "there"}
                  {(role === "student" || role === "parent") && (
                    <img
                      src={HiBaseet}
                      alt="Hi Baseet"
                      className="topbar-hi-icon"
                    />
                  )}
                </span>
              );
            })()}
          </h2>

          <div className="topbar-user">
            {renderTopbarExtras()}
            <Link to="/account" className="avatar avatar-clickable">
              {user?.username?.[0]?.toUpperCase()}
            </Link>
          </div>
        </header>

        <div className="content" style={{ paddingTop: `${topbarHeight + 10}px` }}>
          {role === "student" && <VisualTimeStrip initialMinutes={20} />}
          <Outlet />
        </div>
      </main>
    </div>
  );
}
