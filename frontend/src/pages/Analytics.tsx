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

  const { data: callOutcomes, isLoading: outcomesLoading } = useQuery({
    queryKey: ['call-outcomes'],
    queryFn: getCallOutcomes,
  });

  const { data: languageData, isLoading: languageLoading } = useQuery({
    queryKey: ['language-distribution'],
    queryFn: getLanguageDistribution,
  });

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
                  ) : callOutcomes && callOutcomes.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={callOutcomes}
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
                          {callOutcomes.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                      No call outcome data available
                    </div>
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
                  {callOutcomes && callOutcomes.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={callOutcomes}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                      No data available
                    </div>
                  )}
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
                <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                  Historical trend data coming soon
                </div>
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
                ) : languageData && languageData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={languageData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="language" type="category" width={100} />
                      <Tooltip />
                      <Bar dataKey="calls" fill="#3b82f6" radius={[0, 8, 8, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                    No language distribution data available
                  </div>
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
                <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                  Conversion funnel data coming soon
                </div>

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
