import './App.css';
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import TestBackend from './playground/TestBackend';

// Layout
import MainLayout from "./layouts/MainLayout";

// Pages
import Home from "./pages/home";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { path: "", element: <Home /> },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
