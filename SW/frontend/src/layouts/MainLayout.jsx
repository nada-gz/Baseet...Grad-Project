import { Outlet, Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Logo from "../components/ui/logo";

export default function MainLayout() {
  const { role, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const getSidebarItems = () => {
    switch (role) {
      case "teacher":
        return [
          { label: "Students", path: "/dashboard/teacher", icon: "👥" },
          { label: "Content", path: "/dashboard/teacher/content", icon: "📚" },
          { label: "Classrooms", path: "/dashboard/teacher/classrooms", icon: "🏫" },
        ];
      case "parent":
        return [
          { label: "Child Progress", path: "/dashboard/parent/progress", icon: "📊" },
          { label: "Reports", path: "/dashboard/parent/reports", icon: "📄" },
        ];
      case "student":
        return [
          { label: "Lessons", path: "/dashboard/student/lessons", icon: "📖" },
          { label: "Assignments", path: "/dashboard/student/assignments", icon: "📝" },
        ];
      case "supervisor":
        return [
          { label: "Analytics", path: "/dashboard/supervisor/analytics", icon: "📈" },
          { label: "Student List", path: "/dashboard/supervisor/students", icon: "👨‍🎓" },
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

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div>
          {/* Logo section */}
          <div className="sidebar-logo">
            <Logo />
          </div>

          {/* Role text */}
          <div className="sidebar-role-container" style={{ textAlign: "center", marginBottom: "20px" }}>
            <p className="sidebar-role">{role} Portal</p>
          </div>

          {/* Menu */}
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
            )?.label || "Dashboard"}
          </h2>

          <div className="topbar-user">
            <span className="topbar-role">{role}</span>
            <div className="avatar">
              {user?.email?.[0]?.toUpperCase()}
            </div>
          </div>
        </header>

        <div className="content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
