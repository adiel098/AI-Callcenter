export default function Leads() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Leads Management</h2>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-4">
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            📤 Upload CSV
          </button>
        </div>

        <div className="text-sm text-gray-500">
          Leads list will appear here. Connect to API to fetch leads.
        </div>
      </div>
    </div>
  )
}
