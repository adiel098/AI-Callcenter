import { useQuery } from '@tanstack/react-query';
import { getAnalyticsOverview, getCallOutcomes, getLanguageDistribution, getVoicePerformance } from '../services/api';
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
  Mic,
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

  const { data: voicePerformanceData, isLoading: voiceLoading } = useQuery({
    queryKey: ['voice-performance'],
    queryFn: getVoicePerformance,
  });

  // Define color palette before using it
  const COLORS = ['#8b5cf6', '#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

  function getOutcomeColor(outcome: string): string {
    const colorMap: Record<string, string> = {
      'interested': '#10b981',        // Green - Meeting scheduled (success)
      'not_interested': '#ef4444',    // Red - Not interested
      'no_answer': '#6b7280',         // Gray - No answer
      'busy': '#3b82f6',              // Blue - Interested but no meeting yet
    };
    return colorMap[outcome] || COLORS[0];
  }

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
          <TabsTrigger value="voices">Voice Performance</TabsTrigger>
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

        <TabsContent value="voices" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Mic className="w-5 h-5 text-purple-500" />
                  <CardTitle>Voice Performance Comparison</CardTitle>
                </div>
                <CardDescription>
                  Analyze conversion rates and performance metrics by voice
                </CardDescription>
              </CardHeader>
              <CardContent>
                {voiceLoading ? (
                  <ChartSkeleton />
                ) : voicePerformanceData && voicePerformanceData.length > 0 ? (
                  <div className="space-y-6">
                    {/* Performance Table */}
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse">
                        <thead>
                          <tr className="border-b">
                            <th className="px-4 py-3 text-left text-sm font-semibold">Voice</th>
                            <th className="px-4 py-3 text-right text-sm font-semibold">Calls</th>
                            <th className="px-4 py-3 text-right text-sm font-semibold">Meetings</th>
                            <th className="px-4 py-3 text-right text-sm font-semibold">Conversion</th>
                            <th className="px-4 py-3 text-right text-sm font-semibold">Avg Duration</th>
                          </tr>
                        </thead>
                        <tbody>
                          {voicePerformanceData.map((voice: any, index: number) => (
                            <tr key={voice.voice_id} className="border-b hover:bg-muted/50 transition-colors">
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <div
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                                  />
                                  <span className="font-medium">{voice.voice_name}</span>
                                </div>
                              </td>
                              <td className="px-4 py-3 text-right font-mono">{voice.total_calls}</td>
                              <td className="px-4 py-3 text-right font-mono">{voice.meetings_booked}</td>
                              <td className="px-4 py-3 text-right">
                                <span
                                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    voice.conversion_rate >= 30
                                      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                                      : voice.conversion_rate >= 15
                                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                                      : 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
                                  }`}
                                >
                                  {voice.conversion_rate}%
                                </span>
                              </td>
                              <td className="px-4 py-3 text-right font-mono text-sm text-muted-foreground">
                                {voice.avg_duration}s
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Bar Chart */}
                    <div className="mt-6">
                      <h3 className="text-sm font-semibold mb-4">Conversion Rate Comparison</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={voicePerformanceData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="voice_name" />
                          <YAxis label={{ value: 'Conversion Rate (%)', angle: -90, position: 'insideLeft' }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'hsl(var(--background))',
                              border: '1px solid hsl(var(--border))',
                              borderRadius: '6px',
                            }}
                          />
                          <Bar dataKey="conversion_rate" fill="#8b5cf6" radius={[8, 8, 0, 0]}>
                            {voicePerformanceData.map((entry: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Insights */}
                    {voicePerformanceData.length > 1 && (
                      <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-2">
                          Insights
                        </h3>
                        <p className="text-sm text-purple-800 dark:text-purple-200">
                          {(() => {
                            const sorted = [...voicePerformanceData].sort((a: any, b: any) => b.conversion_rate - a.conversion_rate);
                            const best = sorted[0];
                            const worst = sorted[sorted.length - 1];
                            const diff = best.conversion_rate - worst.conversion_rate;
                            return `${best.voice_name} is performing ${diff.toFixed(1)}% better than ${worst.voice_name}. Consider using high-performing voices for important campaigns.`;
                          })()}
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <Mic className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    <p>No voice performance data available yet.</p>
                    <p className="text-sm mt-1">Make calls with voice settings configured to see analytics.</p>
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
