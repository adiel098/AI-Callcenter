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
  Target,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';

export default function Analytics() {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: getAnalyticsOverview,
  });

  const { data: callOutcomesData, isLoading: outcomesLoading } = useQuery({
    queryKey: ['call-outcomes'],
    queryFn: getCallOutcomes,
  });

  const { data: languageDistData, isLoading: languageLoading } = useQuery({
    queryKey: ['language-distribution'],
    queryFn: getLanguageDistribution,
  });

  // Transform call outcomes for charts
  const callOutcomes = callOutcomesData?.outcomes?.map((item: any) => ({
    name: item.outcome,
    value: item.count,
    color: getOutcomeColor(item.outcome),
  })) || [];

  // Transform language distribution for charts
  const languageData = languageDistData?.languages?.map((item: any) => ({
    language: item.language.toUpperCase(),
    calls: item.count,
  })) || [];

  function getOutcomeColor(outcome: string): string {
    const colorMap: Record<string, string> = {
      'MEETING_SCHEDULED': '#10b981',
      'NOT_INTERESTED': '#ef4444',
      'NO_ANSWER': '#6b7280',
      'VOICEMAIL': '#f59e0b',
      'CALLBACK_REQUESTED': '#3b82f6',
      'INTERESTED': '#8b5cf6',
      'FAILED': '#dc2626',
      'COMPLETED': '#059669',
    };
    return colorMap[outcome] || COLORS[0];
  }

  const COLORS = ['#8b5cf6', '#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Analytics & Reports"
        description="Comprehensive insights into your outbound call campaigns"
      />

      {/* KPI Cards */}
      {analyticsLoading ? (
        <StatCardsSkeleton count={4} />
      ) : analytics ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Leads"
            value={analytics.total_leads}
            icon={Users}
            iconClassName="bg-blue-500/10 text-blue-500"
            description="All time"
          />
          <StatCard
            title="Total Calls"
            value={analytics.total_calls}
            icon={Phone}
            iconClassName="bg-green-500/10 text-green-500"
            description={`${analytics.calls_today} today`}
          />
          <StatCard
            title="Meetings Booked"
            value={analytics.total_meetings}
            icon={Calendar}
            iconClassName="bg-purple-500/10 text-purple-500"
            description={`${analytics.meetings_scheduled_today} today`}
          />
          <StatCard
            title="Conversion Rate"
            value={`${analytics.conversion_rate}%`}
            icon={Target}
            iconClassName="bg-indigo-500/10 text-indigo-500"
            description="Calls to meetings"
          />
        </div>
      ) : (
        <div className="text-center text-muted-foreground py-8">
          No analytics data available
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
                          {callOutcomes.map((entry: any, index: number) => (
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
                  Lead journey from initial contact to meeting
                </CardDescription>
              </CardHeader>
              <CardContent>
                {analytics ? (
                  <div className="space-y-6">
                    {/* Funnel Visualization */}
                    <div className="space-y-3">
                      <div className="relative">
                        <div className="bg-blue-500/10 border-2 border-blue-500 rounded-lg p-6 text-center">
                          <p className="text-3xl font-bold text-blue-600">{analytics.total_leads}</p>
                          <p className="text-sm text-muted-foreground mt-1">Total Leads</p>
                        </div>
                      </div>

                      <div className="relative mx-8">
                        <div className="bg-green-500/10 border-2 border-green-500 rounded-lg p-6 text-center">
                          <p className="text-3xl font-bold text-green-600">{analytics.total_calls}</p>
                          <p className="text-sm text-muted-foreground mt-1">Calls Made</p>
                          <p className="text-xs text-green-600 font-medium mt-2">
                            {analytics.total_leads > 0
                              ? `${((analytics.total_calls / analytics.total_leads) * 100).toFixed(1)}%`
                              : '0%'
                            } conversion
                          </p>
                        </div>
                      </div>

                      <div className="relative mx-16">
                        <div className="bg-purple-500/10 border-2 border-purple-500 rounded-lg p-6 text-center">
                          <p className="text-3xl font-bold text-purple-600">{analytics.total_meetings}</p>
                          <p className="text-sm text-muted-foreground mt-1">Meetings Booked</p>
                          <p className="text-xs text-purple-600 font-medium mt-2">
                            {analytics.total_calls > 0
                              ? `${analytics.conversion_rate}%`
                              : '0%'
                            } conversion
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Conversion Rates */}
                    <div className="mt-8 grid gap-4 md:grid-cols-2">
                      <div className="rounded-lg border p-4 text-center">
                        <p className="text-2xl font-bold text-green-600">
                          {analytics.total_leads > 0
                            ? `${((analytics.total_calls / analytics.total_leads) * 100).toFixed(1)}%`
                            : '0%'
                          }
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Leads to Calls
                        </p>
                      </div>
                      <div className="rounded-lg border p-4 text-center">
                        <p className="text-2xl font-bold text-purple-600">
                          {analytics.conversion_rate}%
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Calls to Meetings
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                    No conversion funnel data available
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
