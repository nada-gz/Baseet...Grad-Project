import { Outlet } from "react-router-dom";

export default function MainLayout() {
  return (
    <div className="min-h-screen flex">
        
        {/* Sidebar */}
        <div className="w-64 bg-gray-200 p-4">
                <div className="font-bold mb-4">Sidebar</div>
        </div>

        {/* Main content area */}
        <div className="flex-1 flex flex-col">

            {/* Navbar */}
            <div className="w-full bg-white shadow p-4">
                <div className="font-bold">Navbar</div>
            </div>

            {/* Routed pages */}
            <div className="p-6">
                <Outlet />
            </div>
        </div>
    </div>
  );
}
