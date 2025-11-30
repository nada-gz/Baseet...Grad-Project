import { Outlet, Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function MainLayout() {
  const { role, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Role-based sidebar items
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
    <div className="min-h-screen flex bg-gray-50">
      {/* Left Sidebar */}
      <div className="w-64 bg-gray-800 text-white flex flex-col">
        {/* Logo/Brand */}
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-xl font-bold">EduPlatform</h1>
          <p className="text-sm text-gray-400 mt-1 capitalize">{role} Portal</p>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-4 space-y-2">
          {sidebarItems.map((item) => {
            const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-700 text-white'
                    : 'hover:bg-gray-700 text-gray-300'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User Info at Bottom */}
        <div className="p-4 border-t border-gray-700">
          <div className="text-sm text-gray-400 mb-2">
            {user?.username || user?.email || "User"}
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors text-sm"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Navbar */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-gray-800">
                {sidebarItems.find((item) => location.pathname === item.path || location.pathname.startsWith(item.path + '/'))?.label || "Dashboard"}
              </h2>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                <span className="font-medium capitalize">{role}</span>
              </div>
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.username?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
