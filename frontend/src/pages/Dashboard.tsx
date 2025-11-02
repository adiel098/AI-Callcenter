import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { getAnalyticsOverview } from '../services/api';
import { PageHeader } from '@/components/PageHeader';
import { StatCard } from '@/components/StatCard';
import { StatCardsSkeleton } from '@/components/LoadingStates';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Users,
  Phone,
  Calendar,
  Flame,
  Sparkles,
  TrendingUp,
  Upload,
  Rocket,
  BarChart3,
  CheckCircle2,
  Clock,
  AlertCircle,
  PhoneCall,
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const navigate = useNavigate();

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: getAnalyticsOverview,
  });

  // Mock recent activity data - replace with real API call
  const recentActivity = [
    {
      id: 1,
      type: 'call',
      title: 'Call completed with John Doe',
      description: 'Meeting scheduled for next week',
      time: '2 minutes ago',
      status: 'success',
    },
    {
      id: 2,
      type: 'meeting',
      title: 'Meeting scheduled with Jane Smith',
      description: 'Tuesday at 2:00 PM',
      time: '15 minutes ago',
      status: 'success',
    },
    {
      id: 3,
      type: 'lead',
      title: '25 new leads uploaded',
      description: 'CSV import completed',
      time: '1 hour ago',
      status: 'info',
    },
    {
      id: 4,
      type: 'call',
      title: 'Call failed with Bob Johnson',
      description: 'No answer',
      time: '2 hours ago',
      status: 'error',
    },
    {
      id: 5,
      type: 'call',
      title: 'Call in progress with Alice Williams',
      description: 'Duration: 3:45',
      time: 'Just now',
      status: 'pending',
    },
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'call':
        return Phone;
      case 'meeting':
        return Calendar;
      case 'lead':
        return Users;
      default:
        return Clock;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return CheckCircle2;
      case 'error':
        return AlertCircle;
      case 'pending':
        return Clock;
      default:
        return Clock;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-500/10 text-green-500';
      case 'error':
        return 'bg-red-500/10 text-red-500';
      case 'pending':
        return 'bg-yellow-500/10 text-yellow-500';
      default:
        return 'bg-blue-500/10 text-blue-500';
    }
  };

  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description="Real-time metrics and insights for your AI outbound campaigns"
      />

      {/* Stats Grid */}
      {isLoading ? (
        <StatCardsSkeleton count={6} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <StatCard
            title="Total Leads"
            value={analytics?.total_leads || 0}
            icon={Users}
            iconClassName="bg-blue-500/10 text-blue-500"
            trend={{ value: 12, label: 'from last month' }}
          />
          <StatCard
            title="Calls Made"
            value={analytics?.total_calls || 0}
            icon={Phone}
            iconClassName="bg-green-500/10 text-green-500"
            trend={{ value: 8, label: 'from last month' }}
          />
          <StatCard
            title="Meetings Scheduled"
            value={analytics?.total_meetings || 0}
            icon={Calendar}
            iconClassName="bg-purple-500/10 text-purple-500"
            trend={{ value: 15, label: 'from last month' }}
          />
          <StatCard
            title="Calls Today"
            value={analytics?.calls_today || 0}
            icon={Flame}
            iconClassName="bg-orange-500/10 text-orange-500"
            description="Active right now"
          />
          <StatCard
            title="Meetings Today"
            value={analytics?.meetings_scheduled_today || 0}
            icon={Sparkles}
            iconClassName="bg-pink-500/10 text-pink-500"
            description="Scheduled for today"
          />
          <StatCard
            title="Conversion Rate"
            value={`${analytics?.conversion_rate || 0}%`}
            icon={TrendingUp}
            iconClassName="bg-indigo-500/10 text-indigo-500"
            trend={{ value: 3, label: 'from last month' }}
          />
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Quick Actions */}
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Manage your campaigns and leads efficiently
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  className="w-full h-24 flex-col gap-2"
                  variant="outline"
                  onClick={() => navigate('/leads')}
                >
                  <Upload className="h-8 w-8" />
                  <span>Upload Leads</span>
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  className="w-full h-24 flex-col gap-2"
                  variant="outline"
                  onClick={() => navigate('/leads')}
                >
                  <Rocket className="h-8 w-8" />
                  <span>Start Campaign</span>
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  className="w-full h-24 flex-col gap-2"
                  variant="outline"
                  onClick={() => navigate('/analytics')}
                >
                  <BarChart3 className="h-8 w-8" />
                  <span>View Analytics</span>
                </Button>
              </motion.div>
            </div>
          </CardContent>
        </Card>

        {/* Active Campaigns */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Active Campaigns</CardTitle>
            <CardDescription>Currently running call campaigns</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Q1 Outreach</p>
                  <p className="text-xs text-muted-foreground">125 / 500 calls</p>
                </div>
                <Badge variant="secondary">
                  <PhoneCall className="mr-1 h-3 w-3" />
                  Active
                </Badge>
              </div>
              <div className="h-2 rounded-full bg-secondary">
                <div className="h-2 rounded-full bg-primary" style={{ width: '25%' }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest updates from your outbound campaigns
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-4">
              {recentActivity.map((activity, index) => {
                const ActivityIcon = getActivityIcon(activity.type);
                const StatusIcon = getStatusIcon(activity.status);

                return (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`rounded-full p-2 ${getStatusColor(activity.status)}`}>
                        <ActivityIcon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium">{activity.title}</p>
                          <span className="text-xs text-muted-foreground">
                            {activity.time}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {activity.description}
                        </p>
                      </div>
                      <StatusIcon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    {index < recentActivity.length - 1 && (
                      <Separator className="my-4" />
                    )}
                  </motion.div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
