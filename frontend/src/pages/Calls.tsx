import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCalls } from '../services/api';
import { PageHeader } from '@/components/PageHeader';
import { DataTable } from '@/components/DataTable';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { TableSkeleton } from '@/components/LoadingStates';
import { EmptyState } from '@/components/EmptyState';
import {
  Phone,
  Clock,
  Calendar as CalendarIcon,
  User,
  Bot,
  CheckCircle2,
  XCircle,
  PhoneOff,
  PhoneMissed,
  Download,
} from 'lucide-react';
import { ColumnDef } from '@tanstack/react-table';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface Call {
  id: number;
  lead_name: string;
  phone: string;
  status: 'completed' | 'failed' | 'no_answer' | 'busy' | 'in_progress';
  outcome?: 'meeting_scheduled' | 'interested' | 'not_interested' | 'callback' | null;
  duration: number;
  created_at: string;
  transcript?: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
}

const statusConfig = {
  completed: { label: 'Completed', color: 'bg-green-100 text-green-800', icon: CheckCircle2 },
  failed: { label: 'Failed', color: 'bg-red-100 text-red-800', icon: XCircle },
  no_answer: { label: 'No Answer', color: 'bg-yellow-100 text-yellow-800', icon: PhoneMissed },
  busy: { label: 'Busy', color: 'bg-orange-100 text-orange-800', icon: PhoneOff },
  in_progress: { label: 'In Progress', color: 'bg-blue-100 text-blue-800', icon: Phone },
};

const outcomeConfig = {
  meeting_scheduled: { label: 'Meeting Scheduled', color: 'bg-purple-100 text-purple-800' },
  interested: { label: 'Interested', color: 'bg-green-100 text-green-800' },
  not_interested: { label: 'Not Interested', color: 'bg-gray-100 text-gray-800' },
  callback: { label: 'Callback Requested', color: 'bg-blue-100 text-blue-800' },
};

export default function Calls() {
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);
  const [transcriptOpen, setTranscriptOpen] = useState(false);

  const { data: callsData, isLoading } = useQuery({
    queryKey: ['calls'],
    queryFn: () => getCalls(1, 100),
  });

  const calls: Call[] = callsData?.calls || [];

  // Removed mock transcript - using real data from API

  const columns: ColumnDef<Call>[] = [
    {
      accessorKey: 'lead_name',
      header: 'Lead Name',
      cell: ({ row }) => {
        const name = row.getValue('lead_name') as string;
        return (
          <div className="flex items-center gap-2">
            <Avatar className="h-8 w-8">
              <AvatarFallback>{name?.charAt(0) || 'U'}</AvatarFallback>
            </Avatar>
            <span className="font-medium">{name || 'Unknown'}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'phone',
      header: 'Phone',
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <Phone className="h-4 w-4 text-muted-foreground" />
          <span>{row.getValue('phone') || '—'}</span>
        </div>
      ),
    },
    {
      accessorKey: 'duration',
      header: 'Duration',
      cell: ({ row }) => {
        const duration = row.getValue('duration') as number;
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        return (
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>{minutes}:{seconds.toString().padStart(2, '0')}</span>
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
        const Icon = config.icon;
        return (
          <Badge variant="secondary" className={cn('font-medium', config.color)}>
            <Icon className="mr-1 h-3 w-3" />
            {config.label}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'outcome',
      header: 'Outcome',
      cell: ({ row }) => {
        const outcome = row.getValue('outcome') as keyof typeof outcomeConfig | null;
        if (!outcome) return <span className="text-xs text-muted-foreground">—</span>;
        const config = outcomeConfig[outcome];
        return (
          <Badge variant="outline" className={cn('font-medium', config.color)}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'created_at',
      header: 'Date',
      cell: ({ row }) => {
        const date = row.getValue('created_at') as string;
        return (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <CalendarIcon className="h-4 w-4" />
            <span>{date ? format(new Date(date), 'MMM d, yyyy HH:mm') : '—'}</span>
          </div>
        );
      },
    },
    {
      id: 'actions',
      cell: ({ row }) => {
        const call = row.original;
        return (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSelectedCall(call);
              setTranscriptOpen(true);
            }}
          >
            View Transcript
          </Button>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Call History"
        description="View and manage all your outbound call records and transcripts"
      />

      {isLoading ? (
        <TableSkeleton rows={10} />
      ) : calls.length === 0 ? (
        <EmptyState
          icon={Phone}
          title="No calls yet"
          description="Call history will appear here once you start making outbound calls to your leads"
        />
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <DataTable
            columns={columns}
            data={calls}
            searchKey="lead_name"
            searchPlaceholder="Search by lead name..."
          />
        </motion.div>
      )}

      {/* Transcript Viewer Sheet */}
      <Sheet open={transcriptOpen} onOpenChange={setTranscriptOpen}>
        <SheetContent className="sm:max-w-2xl w-full">
          <SheetHeader>
            <SheetTitle>Call Transcript</SheetTitle>
            <SheetDescription>
              {selectedCall?.lead_name} • {selectedCall?.phone}
            </SheetDescription>
          </SheetHeader>

          {selectedCall && (
            <div className="mt-6 space-y-4">
              {/* Call Info */}
              <div className="grid grid-cols-2 gap-4 rounded-lg border p-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Status</p>
                  <Badge
                    variant="secondary"
                    className={cn(
                      'font-medium',
                      statusConfig[selectedCall.status].color
                    )}
                  >
                    {statusConfig[selectedCall.status].label}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Duration</p>
                  <p className="text-sm font-medium">
                    {Math.floor(selectedCall.duration / 60)}:
                    {(selectedCall.duration % 60).toString().padStart(2, '0')}
                  </p>
                </div>
                {selectedCall.outcome && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">Outcome</p>
                    <Badge
                      variant="outline"
                      className={cn(
                        'font-medium',
                        outcomeConfig[selectedCall.outcome].color
                      )}
                    >
                      {outcomeConfig[selectedCall.outcome].label}
                    </Badge>
                  </div>
                )}
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Date</p>
                  <p className="text-sm font-medium">
                    {format(new Date(selectedCall.created_at), 'MMM d, yyyy HH:mm')}
                  </p>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <h3 className="text-sm font-semibold">Conversation</h3>
                <Button variant="outline" size="sm">
                  <Download className="mr-2 h-4 w-4" />
                  Export
                </Button>
              </div>

              <Separator />

              {/* Transcript */}
              <ScrollArea className="h-[500px] pr-4">
                <div className="space-y-4">
                  {selectedCall.transcript?.map((message, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        'flex gap-3',
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      {message.role === 'assistant' && (
                        <Avatar className="h-8 w-8 mt-1">
                          <AvatarFallback className="bg-primary/10">
                            <Bot className="h-4 w-4 text-primary" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                      <div
                        className={cn(
                          'rounded-lg px-4 py-2 max-w-[80%]',
                          message.role === 'assistant'
                            ? 'bg-muted'
                            : 'bg-primary text-primary-foreground'
                        )}
                      >
                        <div className="flex items-baseline gap-2 mb-1">
                          <span className="text-xs font-medium">
                            {message.role === 'assistant' ? 'AI Assistant' : 'User'}
                          </span>
                          <span
                            className={cn(
                              'text-xs',
                              message.role === 'assistant'
                                ? 'text-muted-foreground'
                                : 'text-primary-foreground/70'
                            )}
                          >
                            {message.timestamp}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>
                      </div>
                      {message.role === 'user' && (
                        <Avatar className="h-8 w-8 mt-1">
                          <AvatarFallback>
                            <User className="h-4 w-4" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                    </motion.div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
