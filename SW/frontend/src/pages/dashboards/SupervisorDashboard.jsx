import useAuth from "../../hooks/useAuth";

export default function SupervisorDashboard() {
  const { user, loading, error } = useAuth();

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-600">Error loading user.</p>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Supervisor Dashboard</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-4">
        <h2 className="text-xl font-semibold mb-2">
          Welcome, {user?.username}
        </h2>
        <p className="text-gray-700">
          This is your Supervisor Dashboard.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-700">Supervisor Dashboard Content</p>
      </div>
    </div>
  );
}
