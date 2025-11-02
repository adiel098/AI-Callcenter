import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Analytics
export const getAnalyticsOverview = async () => {
  const response = await api.get('/analytics/overview')
  return response.data
}

export const getCallOutcomes = async () => {
  const response = await api.get('/analytics/call-outcomes')
  return response.data
}

export const getLanguageDistribution = async () => {
  const response = await api.get('/analytics/language-distribution')
  return response.data
}

export const getLeadStatusDistribution = async () => {
  const response = await api.get('/analytics/lead-status-distribution')
  return response.data
}

export const getRecentActivity = async (limit = 10) => {
  const response = await api.get(`/analytics/recent-activity?limit=${limit}`)
  return response.data
}

export const getActiveCampaigns = async () => {
  const response = await api.get('/analytics/active-campaigns')
  return response.data
}

// Leads
export const getLeads = async (page = 1, pageSize = 50) => {
  const response = await api.get(`/leads/?page=${page}&page_size=${pageSize}`)
  return response.data
}

export const createLead = async (lead: { name: string; phone: string; email?: string }) => {
  const response = await api.post('/leads/', lead)
  return response.data
}

export const uploadLeadsCSV = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/leads/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const deleteLead = async (leadId: number) => {
  const response = await api.delete(`/leads/${leadId}`)
  return response.data
}

// Calls
export const getCalls = async (page = 1, pageSize = 50) => {
  const response = await api.get(`/calls/?page=${page}&page_size=${pageSize}`)
  return response.data
}

export const getCallDetails = async (callId: number) => {
  const response = await api.get(`/calls/${callId}`)
  return response.data
}

// Meetings
export const getMeetings = async (page = 1, pageSize = 50) => {
  const response = await api.get(`/meetings/?page=${page}&page_size=${pageSize}`)
  return response.data
}

// Campaigns
export const startCampaign = async (campaign: { name: string; lead_ids: number[] }) => {
  const response = await api.post('/campaigns/start', campaign)
  return response.data
}

export const getCampaignStatus = async () => {
  const response = await api.get('/campaigns/status')
  return response.data
}

// Settings
export const getSystemPrompt = async () => {
  const response = await api.get('/settings/system_prompt')
  return response.data
}

export const updateSystemPrompt = async (value: string) => {
  const response = await api.put('/settings/system_prompt', { value })
  return response.data
}

export const getDefaultSystemPrompt = async () => {
  const response = await api.get('/settings/system_prompt/default')
  return response.data
}

export const clearSettingsCache = async () => {
  const response = await api.post('/settings/cache/clear')
  return response.data
}

// Voice Settings
export const getAvailableVoices = async () => {
  const response = await api.get('/settings/voices')
  return response.data
}

export const getDefaultVoice = async () => {
  const response = await api.get('/settings/voice')
  return response.data
}

export const updateDefaultVoice = async (voiceId: string, voiceName: string) => {
  const response = await api.put('/settings/voice', { voice_id: voiceId, voice_name: voiceName })
  return response.data
}

// Voice Analytics
export const getVoicePerformance = async () => {
  const response = await api.get('/analytics/voice-performance')
  return response.data
}

export default api
