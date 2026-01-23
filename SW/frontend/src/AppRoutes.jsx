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

import TeacherDashboard from "./pages/dashboards/Teacher/TeacherDashboard";
import LessonPreparation from "./pages/dashboards/Teacher/LessonsPreparation";
import StudentMonitoring from "./pages/dashboards/Teacher/StudentMonitoring";
import StudentEducationalProgress from "./pages/dashboards/Teacher/StudentEducationalProgress";
import StudentLiveMonitoring from "./pages/dashboards/Teacher/StudentLiveMonitoring";
import ClassManagement from "./pages/dashboards/Teacher/ClassManagement";

import StudentDashboard from "./pages/dashboards/Student/StudentDashboard";
import LessonPlayer from "./pages/dashboards/Student/LessonPlayer";
import LessonChat from "./pages/dashboards/Student/LessonChat";
import LessonVoice from "./pages/dashboards/Student/LessonVoice";
import StudentLessons from "./pages/dashboards/Student/StudentLessons";
import StudentCourses from "./pages/dashboards/Student/StudentCourses";
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

          // New route: Lesson Preparation
          { path: "/dashboard/teacher/lessons-prep", element: <LessonPreparation /> },
          { path: "/dashboard/teacher/students", element: <StudentMonitoring /> },
          { path: "/dashboard/teacher/students/:studentId/progress", element: <StudentEducationalProgress /> },
          { path: "/dashboard/teacher/students/:studentId/live", element: <StudentLiveMonitoring /> },
          { path: "/dashboard/teacher/classrooms", element: <ClassManagement /> },
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
          { path: "/dashboard/student/courses", element: <StudentCourses /> },
          { path: "/dashboard/student/courses/:courseId", element: <StudentLessons /> },
          { path: "/dashboard/student/lesson/:lessonId", element: <LessonChat /> },
          { path: "/dashboard/student/lesson/:lessonId/voice", element: <LessonVoice /> },
          { path: "/dashboard/student/lesson/:lessonId/video", element: <LessonPlayer /> },
          { path: "/dashboard/student/materials", element: <StudentMaterials /> },
          { path: "/dashboard/student/assignments", element: <StudentAssignments /> },
          { path: "/dashboard/student/quizzes", element: <StudentQuizzes /> },
          { path: "/dashboard/student/analytics", element: <StudentAnalytics /> },
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
        children: [{ path: "/dashboard/parent", element: <ParentDashboard /> }],
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
          { path: "/students/:studentId/profile", element: <StudentProfile /> },
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
        children: [{ path: "/account", element: <MyAccount /> }],
      },
    ],
  },

  // Default redirect
  { path: "/", element: <Navigate to="/login" replace /> },

  // Catch-all redirect
  { path: "*", element: <Navigate to="/login" replace /> },
]);

export default router;
