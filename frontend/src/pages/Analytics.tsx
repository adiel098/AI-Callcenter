import { useQuery } from '@tanstack/react-query';
import { getAnalyticsOverview, getCallOutcomes, getLanguageDistribution } from '../services/api';
import { PageHeader } from '@/components/PageHeader';
import { StatCard } from '@/components/StatCard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ChartSkeleton, StatCardsSkeleton } from '@/components/LoadingStates';
import {
  Users,
  Phone,
  Calendar,
  TrendingUp,
  DollarSign,
  Target,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';

export default function Analytics() {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: getAnalyticsOverview,
  });

  const { isLoading: outcomesLoading } = useQuery({
    queryKey: ['call-outcomes'],
    queryFn: getCallOutcomes,
  });

  const { isLoading: languageLoading } = useQuery({
    queryKey: ['language-distribution'],
    queryFn: getLanguageDistribution,
  });

  // Mock data for demo
  const mockCallOutcomes = [
    { name: 'Meeting Scheduled', value: 45, color: '#8b5cf6' },
    { name: 'Interested', value: 78, color: '#10b981' },
    { name: 'Not Interested', value: 34, color: '#6b7280' },
    { name: 'Callback', value: 23, color: '#3b82f6' },
    { name: 'No Answer', value: 56, color: '#f59e0b' },
  ];

  const mockLanguageData = [
    { language: 'English', calls: 145 },
    { language: 'Spanish', calls: 89 },
    { language: 'French', calls: 56 },
    { language: 'German', calls: 34 },
    { language: 'Other', calls: 22 },
  ];

  const mockCallsOverTime = [
    { date: 'Jan 1', calls: 65, meetings: 12 },
    { date: 'Jan 2', calls: 78, meetings: 15 },
    { date: 'Jan 3', calls: 90, meetings: 18 },
    { date: 'Jan 4', calls: 81, meetings: 14 },
    { date: 'Jan 5', calls: 95, meetings: 20 },
    { date: 'Jan 6', calls: 102, meetings: 22 },
    { date: 'Jan 7', calls: 88, meetings: 16 },
  ];

  const mockConversionFunnel = [
    { stage: 'Leads', value: 500 },
    { stage: 'Calls Made', value: 346 },
    { stage: 'Interested', value: 180 },
    { stage: 'Meetings', value: 90 },
    { stage: 'Closed', value: 45 },
  ];

  const COLORS = ['#8b5cf6', '#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Analytics & Reports"
        description="Comprehensive insights into your outbound call campaigns"
      />

      {/* KPI Cards */}
      {analyticsLoading ? (
        <StatCardsSkeleton count={6} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <StatCard
            title="Total Leads"
            value={analytics?.total_leads || 500}
            icon={Users}
            iconClassName="bg-blue-500/10 text-blue-500"
            trend={{ value: 12, label: 'from last month' }}
            description="All time"
          />
          <StatCard
            title="Total Calls"
            value={analytics?.total_calls || 346}
            icon={Phone}
            iconClassName="bg-green-500/10 text-green-500"
            trend={{ value: 8, label: 'from last month' }}
            description="All time"
          />
          <StatCard
            title="Meetings Booked"
            value={analytics?.total_meetings || 90}
            icon={Calendar}
            iconClassName="bg-purple-500/10 text-purple-500"
            trend={{ value: 15, label: 'from last month' }}
            description="All time"
          />
          <StatCard
            title="Conversion Rate"
            value={`${analytics?.conversion_rate || 26}%`}
            icon={Target}
            iconClassName="bg-indigo-500/10 text-indigo-500"
            trend={{ value: 3, label: 'from last month' }}
            description="Calls to meetings"
          />
          <StatCard
            title="Revenue Impact"
            value="$45,000"
            icon={DollarSign}
            iconClassName="bg-emerald-500/10 text-emerald-500"
            trend={{ value: 18, label: 'from last month' }}
            description="Estimated value"
          />
          <StatCard
            title="ROI"
            value="385%"
            icon={TrendingUp}
            iconClassName="bg-pink-500/10 text-pink-500"
            trend={{ value: 22, label: 'from last month' }}
            description="Return on investment"
          />
        </div>
      )}

      <Tabs defaultValue="outcomes" className="space-y-4">
        <TabsList>
          <TabsTrigger value="outcomes">Call Outcomes</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="languages">Languages</TabsTrigger>
          <TabsTrigger value="funnel">Conversion Funnel</TabsTrigger>
        </TabsList>

        <TabsContent value="outcomes" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Pie Chart */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Call Outcomes Distribution</CardTitle>
                  <CardDescription>Breakdown of all call outcomes</CardDescription>
                </CardHeader>
                <CardContent>
                  {outcomesLoading ? (
                    <ChartSkeleton />
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={mockCallOutcomes}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) =>
                            `${name}: ${(percent * 100).toFixed(0)}%`
                          }
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {mockCallOutcomes.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Bar Chart */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Outcomes by Count</CardTitle>
                  <CardDescription>Total number of each outcome</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={mockCallOutcomes}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Calls & Meetings Over Time</CardTitle>
                <CardDescription>Daily performance for the last 7 days</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={mockCallsOverTime}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="calls"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 8 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="meetings"
                      stroke="#8b5cf6"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="languages" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Language Distribution</CardTitle>
                <CardDescription>Calls by language preference</CardDescription>
              </CardHeader>
              <CardContent>
                {languageLoading ? (
                  <ChartSkeleton />
                ) : (
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={mockLanguageData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="language" type="category" width={100} />
                      <Tooltip />
                      <Bar dataKey="calls" fill="#3b82f6" radius={[0, 8, 8, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="funnel" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Conversion Funnel</CardTitle>
                <CardDescription>
                  Lead journey from initial contact to closed deal
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={mockConversionFunnel} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="stage" type="category" width={120} />
                    <Tooltip />
                    <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                      {mockConversionFunnel.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>

                {/* Conversion Rates */}
                <div className="mt-6 grid gap-4 md:grid-cols-4">
                  <div className="rounded-lg border p-4 text-center">
                    <p className="text-2xl font-bold text-green-600">69%</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Leads to Calls
                    </p>
                  </div>
                  <div className="rounded-lg border p-4 text-center">
                    <p className="text-2xl font-bold text-blue-600">52%</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Calls to Interest
                    </p>
                  </div>
                  <div className="rounded-lg border p-4 text-center">
                    <p className="text-2xl font-bold text-purple-600">50%</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Interest to Meetings
                    </p>
                  </div>
                  <div className="rounded-lg border p-4 text-center">
                    <p className="text-2xl font-bold text-pink-600">50%</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Meetings to Closed
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
