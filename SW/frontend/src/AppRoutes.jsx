import { createBrowserRouter, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";

// Layout
import MainLayout from "./layouts/MainLayout";

// Pages - Public
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import NotAllowed from "./pages/auth/NotAllowed";

// Pages - Protected - Dashboards

import MyAccount from "./pages/account/MyAccount";
import StudentProfile from "./pages/dashboards/Common/StudentProfile";

import TeacherDashboard from "./pages/dashboards/TeacherDashboard";

import StudentDashboard from "./pages/dashboards/Student/StudentDashboard";
import LessonPlayer from "./pages/dashboards/Student/LessonPlayer";
import LessonChat from "./pages/dashboards/Student/LessonChat";
import StudentLessons from "./pages/dashboards/Student/StudentLessons";
import StudentMaterials from "./pages/dashboards/Student/StudentMaterials";
import StudentAssignments from "./pages/dashboards/Student/StudentAssignments";
import StudentQuizzes from "./pages/dashboards/Student/StudentQuizzes";
import StudentAnalytics from "./pages/dashboards/Student/StudentAnalytics";

import ParentDashboard from "./pages/dashboards/ParentDashboard";

import SupervisorDashboard from "./pages/dashboards/SupervisorDashboard";




import AllStudents from "./pages/dashboards/Common/AllStudents";

const router = createBrowserRouter([
  // Public routes
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  { path: "/not-allowed", element: <NotAllowed /> },

  // Protected routes - Teacher
  {
    element: <ProtectedRoute allowedRoles={["teacher"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { path: "/dashboard/teacher", element: <TeacherDashboard /> },
        ],
      },
    ],
  },


  // Protected routes - Student
{
  element: <ProtectedRoute allowedRoles={["student"]} />,
  children: [
    {
      element: <MainLayout />,
      children: [
        { path: "/dashboard/student", element: <StudentDashboard /> },

        // Lessons list
        { path: "/dashboard/student/lessons", element: <StudentLessons /> },

        // Single lesson chat
        { path: "/dashboard/student/lesson/:lessonId", element: <LessonChat /> },

        // Materials
        { path: "/dashboard/student/materials", element: <StudentMaterials /> },

        // Assignments
        { path: "/dashboard/student/assignments", element: <StudentAssignments /> },

        // Quizzes
        { path: "/dashboard/student/quizzes", element: <StudentQuizzes /> },

        // Analytics
        { path: "/dashboard/student/analytics", element: <StudentAnalytics /> },

        // Profile
      ],
    },
  ],
},


  // Protected routes - Parent
  {
    element: <ProtectedRoute allowedRoles={["parent"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { path: "/dashboard/parent", element: <ParentDashboard /> },
        ],
      },
    ],
  },

  // Protected routes - Supervisor
  {
    element: <ProtectedRoute allowedRoles={["supervisor"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [{ path: "/dashboard/supervisor", element: <SupervisorDashboard /> }],
      },
    ],
  },

  // Protected routes - all students
  {
    element: <ProtectedRoute allowedRoles={["teacher", "parent", "supervisor"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [{ path: "/students", element: <AllStudents /> }],
      },
    ],
  },

  // Protected routes - Profile (student / parent / teacher)
  {
    element: <ProtectedRoute allowedRoles={["student", "parent", "teacher"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [
          {
            path: "/students/:studentId/profile",
            element: <StudentProfile />,
          },
        ],
      },
    ],
  },
  

  // Protected routes - Account (student / parent / teacher / supervisor)
  {
    element: <ProtectedRoute allowedRoles={["student", "parent", "teacher", "supervisor"]} />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { path: "/account", element: <MyAccount /> },
        ],
      },
    ],
  },
  


  // Default redirect
  { path: "/", element: <Navigate to="/login" replace /> },

  // Catch-all redirect
  { path: "*", element: <Navigate to="/login" replace /> },
]);

export default router;
