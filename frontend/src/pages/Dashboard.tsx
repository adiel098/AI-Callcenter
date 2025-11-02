import { useQuery } from '@tanstack/react-query'
import { getAnalyticsOverview } from '../services/api'

export default function Dashboard() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: getAnalyticsOverview,
  })

  if (isLoading) {
    return <div>Loading...</div>
  }

  const stats = [
    { label: 'Total Leads', value: analytics?.total_leads || 0, icon: '👥', color: 'bg-blue-500' },
    { label: 'Calls Made', value: analytics?.total_calls || 0, icon: '📞', color: 'bg-green-500' },
    { label: 'Meetings Scheduled', value: analytics?.total_meetings || 0, icon: '📅', color: 'bg-purple-500' },
    { label: 'Calls Today', value: analytics?.calls_today || 0, icon: '🔥', color: 'bg-orange-500' },
    { label: 'Meetings Today', value: analytics?.meetings_scheduled_today || 0, icon: '✨', color: 'bg-pink-500' },
    { label: 'Conversion Rate', value: `${analytics?.conversion_rate || 0}%`, icon: '📊', color: 'bg-indigo-500' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard Overview</h2>
        <p className="mt-1 text-sm text-gray-500">
          Real-time metrics for your AI call campaigns
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${stat.color} rounded-md p-3`}>
                  <span className="text-2xl">{stat.icon}</span>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.label}
                    </dt>
                    <dd className="text-3xl font-semibold text-gray-900">
                      {stat.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <button className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            📤 Upload Leads
          </button>
          <button className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
            🚀 Start Campaign
          </button>
          <button className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700">
            📊 View Analytics
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="text-sm text-gray-500">
          Connect to the backend API to see real-time activity...
        </div>
      </div>
    </div>
  )
}
