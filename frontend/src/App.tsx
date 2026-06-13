import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { DashboardPage } from "./pages/DashboardPage";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RepositoryReviewPage } from "./pages/RepositoryReviewPage";
import { ReviewDetailsPage } from "./pages/ReviewDetailsPage";
import { ReviewHistoryPage } from "./pages/ReviewHistoryPage";
import { SignupPage } from "./pages/SignupPage";
import { SubmitCodePage } from "./pages/SubmitCodePage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/submit" element={<SubmitCodePage />} />
          <Route path="/reviews" element={<ReviewHistoryPage />} />
          <Route path="/reviews/:reviewId" element={<ReviewDetailsPage />} />
          <Route path="/repository-review" element={<RepositoryReviewPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
