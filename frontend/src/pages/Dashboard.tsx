import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { getAnalyticsOverview, getRecentActivity, getActiveCampaigns } from '../services/api';
import { formatDistanceToNow } from 'date-fns';
import { PageHeader } from '@/components/PageHeader';
import { StatCard } from '@/components/StatCard';
import { StatCardsSkeleton } from '@/components/LoadingStates';
import { LeadStatusStats } from '@/components/LeadStatusStats';
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

  const { data: recentActivityData, isLoading: activityLoading } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => getRecentActivity(10),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: campaignsData, isLoading: campaignsLoading } = useQuery({
    queryKey: ['active-campaigns'],
    queryFn: getActiveCampaigns,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const recentActivity = recentActivityData?.activities || [];

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

      {/* Active Campaigns */}
      <Card>
        <CardHeader>
          <CardTitle>Active Campaigns</CardTitle>
          <CardDescription>Currently running call campaigns</CardDescription>
        </CardHeader>
        <CardContent>
          {campaignsLoading ? (
            <div className="flex items-center justify-center h-20">
              <p className="text-sm text-muted-foreground">Loading campaigns...</p>
            </div>
          ) : campaignsData?.campaigns && campaignsData.campaigns.length > 0 ? (
            <div className="space-y-6">
              {campaignsData.campaigns.map((campaign: any, index: number) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{campaign.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {campaign.completed} / {campaign.total} leads contacted
                      </p>
                    </div>
                    <Badge variant={campaign.is_active ? "default" : "secondary"}>
                      <PhoneCall className="mr-1 h-3 w-3" />
                      {campaign.is_active ? 'Active' : 'Idle'}
                    </Badge>
                  </div>
                  <div className="h-2 rounded-full bg-secondary">
                    <div
                      className="h-2 rounded-full bg-primary transition-all duration-500"
                      style={{ width: `${campaign.progress}%` }}
                    />
                  </div>
                  {campaign.is_active && (
                    <div className="flex gap-4 text-xs text-muted-foreground">
                      <span>Queued: {campaign.queued}</span>
                      <span>Calling: {campaign.calling}</span>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-32 text-center">
              <p className="text-sm text-muted-foreground mb-2">No active campaigns</p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => navigate('/leads')}
              >
                Start a Campaign
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lead Status Distribution */}
      <div className="grid gap-4 md:grid-cols-2">
        <LeadStatusStats />

        {/* Placeholder for additional stats component */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
            <CardDescription>
              Key performance indicators for your campaigns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Average Call Duration</span>
                <span className="text-sm text-muted-foreground">
                  {analytics?.average_call_duration || 0}s
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Success Rate</span>
                <span className="text-sm text-muted-foreground">
                  {analytics?.conversion_rate || 0}%
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Total Campaigns</span>
                <span className="text-sm text-muted-foreground">1 active</span>
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
            {activityLoading ? (
              <div className="flex items-center justify-center h-32">
                <p className="text-sm text-muted-foreground">Loading activity...</p>
              </div>
            ) : recentActivity.length > 0 ? (
              <div className="space-y-4">
                {recentActivity.map((activity: any, index: number) => {
                  const ActivityIcon = getActivityIcon(activity.type);
                  const StatusIcon = getStatusIcon(activity.status);

                  // Format time to relative format
                  const timeAgo = formatDistanceToNow(new Date(activity.time), { addSuffix: true });

                  return (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="flex items-start gap-4">
                        <div className={`rounded-full p-2 ${getStatusColor(activity.status)}`}>
                          <ActivityIcon className="h-4 w-4" />
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium">{activity.title}</p>
                            <span className="text-xs text-muted-foreground">
                              {timeAgo}
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
            ) : (
              <div className="flex items-center justify-center h-32">
                <p className="text-sm text-muted-foreground">No recent activity</p>
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
