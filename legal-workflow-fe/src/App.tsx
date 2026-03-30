import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { MyTasksPage } from './pages/MyTasksPage'
import { CreateTaskPage } from './pages/CreateTaskPage'
import { TaskDetailPage } from './pages/TaskDetailPage'
import { ConfigTSTPage } from './pages/ConfigTSTPage'
import { ConfigTRTPage } from './pages/ConfigTRTPage'
import { ConfigTDTPage } from './pages/ConfigTDTPage'
import { ConfigFiltersPage } from './pages/ConfigFiltersPage'
import { SLAReportPage } from './pages/SLAReportPage'
import { WorkloadReportPage } from './pages/WorkloadReportPage'
import { LoginPage } from './pages/LoginPage'
import { useAuthStore } from './stores/auth.store'

function App() {
  const token = useAuthStore((s) => s.token)

  return (
    <BrowserRouter>
      <Routes>
        {!token ? (
          <>
            <Route path="/login" element={<LoginPage />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </>
        ) : (
          <>
            <Route path="/legal" element={<AppLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="tasks" element={<MyTasksPage />} />
              <Route path="tasks/new" element={<CreateTaskPage />} />
              <Route path="tasks/:id" element={<TaskDetailPage />} />
              <Route path="config/tst" element={<ConfigTSTPage />} />
              <Route path="config/trt" element={<ConfigTRTPage />} />
              <Route path="config/tdt" element={<ConfigTDTPage />} />
              <Route path="config/filters" element={<ConfigFiltersPage />} />
              <Route path="reports/sla" element={<SLAReportPage />} />
              <Route path="reports/workload" element={<WorkloadReportPage />} />
              <Route path="settings" element={<div>Settings</div>} />
            </Route>
            <Route path="/login" element={<Navigate to="/legal" replace />} />
            <Route path="*" element={<Navigate to="/legal" replace />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  )
}

export default App
