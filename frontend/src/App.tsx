import { Navigate, Route, Routes } from "react-router-dom";

import { ProjectDetailPage } from "@/pages/ProjectDetailPage";
import { ProjectListPage } from "@/pages/ProjectListPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/projects" replace />} />
      <Route path="/projects" element={<ProjectListPage />} />
      <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  );
}
