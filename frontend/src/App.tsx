import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppConfigProvider } from "./lib/AppConfigContext";
import { AssessmentProvider } from "./lib/AssessmentContext";
import { TopNav } from "./components/TopNav";
import DashboardPage from "./pages/DashboardPage";
import MsmeSelectionPage from "./pages/MsmeSelectionPage";
import PublicAssessmentPage from "./pages/PublicAssessmentPage";
import ConsentSimulationPage from "./pages/ConsentSimulationPage";
import AgentProcessingPage from "./pages/AgentProcessingPage";
import HealthCardPage from "./pages/HealthCardPage";
import RecommendationPage from "./pages/RecommendationPage";
import ChatAssistantPage from "./pages/ChatAssistantPage";
import ReportPage from "./pages/ReportPage";

function App() {
  return (
    <AppConfigProvider>
      <AssessmentProvider>
        <BrowserRouter>
          <TopNav />
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/msme" element={<MsmeSelectionPage />} />
            <Route path="/msme/:id/public" element={<PublicAssessmentPage />} />
            <Route path="/msme/:id/consent" element={<ConsentSimulationPage />} />
            <Route path="/msme/:id/processing" element={<AgentProcessingPage />} />
            <Route path="/msme/:id/health-card" element={<HealthCardPage />} />
            <Route path="/msme/:id/recommendation" element={<RecommendationPage />} />
            <Route path="/msme/:id/chat" element={<ChatAssistantPage />} />
            <Route path="/msme/:id/report" element={<ReportPage />} />
          </Routes>
        </BrowserRouter>
      </AssessmentProvider>
    </AppConfigProvider>
  );
}

export default App;
