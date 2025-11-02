import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Leads from './pages/Leads'
import Calls from './pages/Calls'
import Meetings from './pages/Meetings'
import Analytics from './pages/Analytics'
import { Toaster } from '@/components/ui/toaster'
import { Toaster as Sonner } from 'sonner'

function App() {
  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/calls" element={<Calls />} />
          <Route path="/meetings" element={<Meetings />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
      <Toaster />
      <Sonner />
    </>
  )
}

export default App
