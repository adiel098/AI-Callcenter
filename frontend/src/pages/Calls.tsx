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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
  FileText,
} from 'lucide-react';
import { ColumnDef } from '@tanstack/react-table';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface Call {
  id: number;
  lead_id: number;
  lead_name?: string;
  phone?: string;
  outcome?: string;  // Backend field name (not status)
  duration?: number;
  started_at?: string;  // Backend field name (not created_at)
  ended_at?: string;
  summary?: string;
  transcript?: string;  // Backend returns plain text, not array
  twilio_call_sid?: string;
  recording_url?: string;
  language?: string;
}

// Match backend CallOutcome enum values
const outcomeConfig: Record<string, { label: string; color: string; icon: any }> = {
  completed: { label: 'Completed', color: 'bg-green-100 text-green-800', icon: CheckCircle2 },
  failed: { label: 'Failed', color: 'bg-red-100 text-red-800', icon: XCircle },
  no_answer: { label: 'No Answer', color: 'bg-yellow-100 text-yellow-800', icon: PhoneMissed },
  busy: { label: 'Busy', color: 'bg-orange-100 text-orange-800', icon: PhoneOff },
  in_progress: { label: 'In Progress', color: 'bg-blue-100 text-blue-800', icon: Phone },
  meeting_scheduled: { label: 'Meeting Scheduled', color: 'bg-purple-100 text-purple-800', icon: CheckCircle2 },
  not_interested: { label: 'Not Interested', color: 'bg-gray-100 text-gray-800', icon: XCircle },
  voicemail: { label: 'Voicemail', color: 'bg-yellow-100 text-yellow-800', icon: PhoneMissed },
  unknown: { label: 'Unknown', color: 'bg-gray-100 text-gray-800', icon: Phone },
};

export default function Calls() {
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);
  const [transcriptOpen, setTranscriptOpen] = useState(false);
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [summaryCall, setSummaryCall] = useState<Call | null>(null);

  const { data: callsData, isLoading } = useQuery({
    queryKey: ['calls'],
    queryFn: () => getCalls(1, 100),
  });

  // Backend returns array directly, not nested in 'calls' property
  const calls: Call[] = callsData || [];

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
        if (!duration) return <span className="text-xs text-muted-foreground">—</span>;
        const minutes = Math.floor(duration / 60);
        const seconds = Math.floor(duration % 60);
        return (
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>{minutes}:{seconds.toString().padStart(2, '0')}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'outcome',
      header: 'Outcome',
      cell: ({ row }) => {
        const outcome = row.getValue('outcome') as string;
        if (!outcome) return <span className="text-xs text-muted-foreground">—</span>;
        const config = outcomeConfig[outcome] || outcomeConfig.unknown;
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
      accessorKey: 'started_at',
      header: 'Date',
      cell: ({ row }) => {
        const date = row.getValue('started_at') as string;
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
      header: 'Actions',
      cell: ({ row }) => {
        const call = row.original;
        return (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSummaryCall(call);
                setSummaryOpen(true);
              }}
              disabled={!call.summary}
            >
              <FileText className="mr-1 h-3 w-3" />
              Summary
            </Button>
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
          </div>
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
                {selectedCall.outcome && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">Outcome</p>
                    <Badge
                      variant="secondary"
                      className={cn(
                        'font-medium',
                        (outcomeConfig[selectedCall.outcome] || outcomeConfig.unknown).color
                      )}
                    >
                      {(outcomeConfig[selectedCall.outcome] || outcomeConfig.unknown).label}
                    </Badge>
                  </div>
                )}
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Duration</p>
                  <p className="text-sm font-medium">
                    {selectedCall.duration ? `${Math.floor(selectedCall.duration / 60)}:${Math.floor(selectedCall.duration % 60).toString().padStart(2, '0')}` : '—'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Date</p>
                  <p className="text-sm font-medium">
                    {selectedCall.started_at ? format(new Date(selectedCall.started_at), 'MMM d, yyyy HH:mm') : '—'}
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
                <div className="space-y-2">
                  {selectedCall.transcript ? (
                    <div className="rounded-lg border p-4 bg-muted/30">
                      <pre className="text-sm whitespace-pre-wrap font-sans">
                        {selectedCall.transcript}
                      </pre>
                    </div>
                  ) : (
                    <div className="text-center text-sm text-muted-foreground py-8">
                      No transcript available for this call
                    </div>
                  )}
                </div>
              </ScrollArea>
            </div>
          )}
        </SheetContent>
      </Sheet>

      {/* Summary Dialog */}
      <Dialog open={summaryOpen} onOpenChange={setSummaryOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Call Summary
            </DialogTitle>
            <DialogDescription>
              {summaryCall?.lead_name} • {summaryCall?.phone}
            </DialogDescription>
          </DialogHeader>

          {summaryCall && (
            <div className="space-y-4">
              {/* Call Info */}
              <div className="grid grid-cols-3 gap-4 rounded-lg border p-4 bg-muted/50">
                {summaryCall.outcome && (
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">Outcome</p>
                    <Badge
                      variant="secondary"
                      className={cn(
                        'font-medium',
                        (outcomeConfig[summaryCall.outcome] || outcomeConfig.unknown).color
                      )}
                    >
                      {(outcomeConfig[summaryCall.outcome] || outcomeConfig.unknown).label}
                    </Badge>
                  </div>
                )}
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Duration</p>
                  <p className="text-sm font-medium">
                    {summaryCall.duration ? `${Math.floor(summaryCall.duration / 60)}:${Math.floor(summaryCall.duration % 60).toString().padStart(2, '0')}` : '—'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Date</p>
                  <p className="text-sm font-medium">
                    {summaryCall.started_at ? format(new Date(summaryCall.started_at), 'MMM d, yyyy') : '—'}
                  </p>
                </div>
              </div>

              {/* Summary Content */}
              <div className="rounded-lg border p-6 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-blue-950/20 dark:to-purple-950/20">
                <div className="flex items-start gap-3">
                  <div className="rounded-full bg-primary/10 p-2 mt-1">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <h3 className="text-sm font-semibold text-foreground">
                      AI-Generated Summary
                    </h3>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {summaryCall.summary || 'No summary available for this call.'}
                    </p>
                  </div>
                </div>
              </div>

              {summaryCall.outcome && (
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <span className="text-sm font-medium text-muted-foreground">Outcome Details</span>
                  <Badge
                    variant="outline"
                    className={cn(
                      'font-medium',
                      (outcomeConfig[summaryCall.outcome] || outcomeConfig.unknown).color
                    )}
                  >
                    {(outcomeConfig[summaryCall.outcome] || outcomeConfig.unknown).label}
                  </Badge>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setSummaryOpen(false);
                    setSelectedCall(summaryCall);
                    setTranscriptOpen(true);
                  }}
                >
                  View Full Transcript
                </Button>
                <Button
                  variant="default"
                  onClick={() => setSummaryOpen(false)}
                >
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
