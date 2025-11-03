import { useQuery } from '@tanstack/react-query';
import { getMeetings } from '../services/api';
import { PageHeader } from '@/components/PageHeader';
import { DataTable } from '@/components/DataTable';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TableSkeleton } from '@/components/LoadingStates';
import { EmptyState } from '@/components/EmptyState';
import {
  Calendar as CalendarIcon,
  Clock,
  Plus,
  ExternalLink,
  User,
} from 'lucide-react';
import { ColumnDef } from '@tanstack/react-table';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface Meeting {
  id: number;
  lead_id: number;
  lead_name: string;
  email: string;
  scheduled_at: string;
  duration: number | null;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  meeting_link?: string;
  notes?: string;
  calendar_event_id?: string;
  call_id?: number;
}

const statusConfig = {
  scheduled: { label: 'Scheduled', color: 'bg-blue-100 text-blue-800' },
  confirmed: { label: 'Confirmed', color: 'bg-green-100 text-green-800' },
  completed: { label: 'Completed', color: 'bg-gray-100 text-gray-800' },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-800' },
  no_show: { label: 'No Show', color: 'bg-orange-100 text-orange-800' },
};

export default function Meetings() {
  const { data: meetingsData, isLoading } = useQuery({
    queryKey: ['meetings'],
    queryFn: () => getMeetings(1, 100),
  });

  const meetings: Meeting[] = meetingsData?.meetings || [];

  const columns: ColumnDef<Meeting>[] = [
    {
      accessorKey: 'lead_name',
      header: 'Lead',
      cell: ({ row }) => {
        const name = row.getValue('lead_name') as string;
        const email = row.original.email;
        return (
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{name}</span>
            </div>
            <p className="text-xs text-muted-foreground">{email}</p>
          </div>
        );
      },
    },
    {
      accessorKey: 'scheduled_at',
      header: 'Date & Time',
      cell: ({ row }) => {
        const date = row.getValue('scheduled_at') as string;
        return (
          <div className="flex items-center gap-2">
            <CalendarIcon className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium">
                {format(new Date(date), 'MMM d, yyyy')}
              </p>
              <p className="text-xs text-muted-foreground">
                {format(new Date(date), 'h:mm a')}
              </p>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'duration',
      header: 'Duration',
      cell: ({ row }) => {
        const duration = row.getValue('duration') as number | null;
        return (
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>{duration || 30} min</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => {
        const status = row.getValue('status') as keyof typeof statusConfig;
        const config = statusConfig[status];
        return (
          <Badge variant="secondary" className={cn('font-medium', config.color)}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      id: 'actions',
      cell: ({ row }) => {
        const meeting = row.original;
        return (
          <div className="flex items-center gap-2">
            {meeting.meeting_link && (
              <Button variant="outline" size="sm" asChild>
                <a href={meeting.meeting_link} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Join
                </a>
              </Button>
            )}
            <Button variant="ghost" size="sm">
              Details
            </Button>
          </div>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Meetings"
        description="Manage and track all scheduled meetings with leads"
        actions={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Schedule Meeting
          </Button>
        }
      />

      {isLoading ? (
        <TableSkeleton rows={5} />
      ) : meetings.length === 0 ? (
        <EmptyState
          icon={CalendarIcon}
          title="No meetings scheduled"
          description="Scheduled meetings will appear here once leads book time with you"
          action={{
            label: 'Schedule Meeting',
            onClick: () => {},
          }}
        />
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <DataTable
            columns={columns}
            data={meetings}
            searchKey="lead_name"
            searchPlaceholder="Search by lead name..."
          />
        </motion.div>
      )}

      {/* Upcoming Meetings Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Meetings</CardTitle>
          <CardDescription>Next meetings in your schedule</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {meetings.slice(0, 3).map((meeting) => {
              return (
                <motion.div
                  key={meeting.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ scale: 1.02 }}
                  className="rounded-lg border p-4 space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <p className="font-medium">{meeting.lead_name}</p>
                      <p className="text-xs text-muted-foreground">{meeting.email}</p>
                    </div>
                    <CalendarIcon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <CalendarIcon className="h-4 w-4" />
                      {format(new Date(meeting.scheduled_at), 'MMM d, yyyy')}
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      {format(new Date(meeting.scheduled_at), 'h:mm a')} • {meeting.duration || 30} min
                    </div>
                  </div>
                  <Badge
                    variant="secondary"
                    className={cn('w-full justify-center', statusConfig[meeting.status].color)}
                  >
                    {statusConfig[meeting.status].label}
                  </Badge>
                  {meeting.meeting_link && (
                    <Button variant="outline" size="sm" className="w-full" asChild>
                      <a
                        href={meeting.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="mr-2 h-4 w-4" />
                        Join
                      </a>
                    </Button>
                  )}
                </motion.div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
