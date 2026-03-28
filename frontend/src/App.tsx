import { Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import Handler from "./stack/handler";
import SignInPage from "./pages/SignInPage";
import SignUpPage from "./pages/SignUpPage";

function App() {
  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <Routes>
        {/* Stack Auth handler routes (sign-in, sign-up, password reset, etc.) */}
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/sign-up" element={<SignUpPage />} />

        {/* Public routes */}
        <Route path="/" element={<DashboardPage />} />

        {/* These will be added as we build each page: */}
        {/* <Route path="/login" element={<LoginPage />} /> */}
        {/* <Route path="/agents/:id" element={<AgentDetailPage />} /> */}
        {/* <Route path="/assets/:symbol" element={<AssetDeepDivePage />} /> */}
        {/* <Route path="/briefings" element={<BriefingsPage />} /> */}
        {/* <Route path="/settings" element={<SettingsPage />} /> */}
      </Routes>
    </div>
  );
}

export default App;
