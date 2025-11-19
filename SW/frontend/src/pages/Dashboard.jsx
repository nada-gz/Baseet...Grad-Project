import { useParams } from "react-router-dom";

export default function Dashboard() {
  const { role } = useParams();

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-700">
          Welcome to the dashboard! Your role is: <span className="font-semibold">{role}</span>
        </p>
        <p className="text-sm text-gray-500 mt-2">
          TODO: Implement dashboard content based on role ({role})
        </p>
      </div>
    </div>
  );
}

