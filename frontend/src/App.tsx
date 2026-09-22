import { Routes, Route } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { ToastProvider } from "./hooks/useToast";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Landing from "./pages/public/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import Scans from "./pages/Scans";
import ScanDetails from "./pages/ScanDetails";
import Findings from "./pages/Findings";
import FindingDetail from "./pages/FindingDetail";
import AttackSurface from "./pages/AttackSurface";
import Reports from "./pages/Reports";
import KnowledgeBase from "./pages/KnowledgeBase";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        {/* --- Public product website — no authentication required --- */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* --- Authenticated security workspace --- */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:projectId" element={<ProjectDetail />} />
            <Route path="/scans" element={<Scans />} />
            <Route path="/scans/:scanId" element={<ScanDetails />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/findings/:findingId" element={<FindingDetail />} />
            <Route path="/attack-surface" element={<AttackSurface />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/knowledge-base" element={<KnowledgeBase />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
      </Routes>
    </ToastProvider>
  );
}
