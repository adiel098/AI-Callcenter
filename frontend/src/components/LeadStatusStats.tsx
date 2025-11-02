import { useQuery } from '@tanstack/react-query'
import { getLeadStatusDistribution } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Clock,
  Phone,
  CheckCircle2,
  Calendar,
  XCircle,
  PhoneOff,
  AlertCircle,
  List
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

interface LeadStatus {
  status: string
  count: number
  percentage: number
}

interface LeadStatusData {
  statuses: LeadStatus[]
  total: number
}

// Status configuration with colors, icons, and labels
const statusConfig: Record<string, { label: string; icon: any; color: string; bgColor: string }> = {
  pending: {
    label: 'Pending',
    icon: Clock,
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-950'
  },
  queued: {
    label: 'Queued',
    icon: List,
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-100 dark:bg-blue-950'
  },
  calling: {
    label: 'Calling',
    icon: Phone,
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-100 dark:bg-purple-950'
  },
  contacted: {
    label: 'Contacted',
    icon: CheckCircle2,
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-950'
  },
  meeting_scheduled: {
    label: 'Meeting Scheduled',
    icon: Calendar,
    color: 'text-emerald-600 dark:text-emerald-400',
    bgColor: 'bg-emerald-100 dark:bg-emerald-950'
  },
  not_interested: {
    label: 'Not Interested',
    icon: XCircle,
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-950'
  },
  no_answer: {
    label: 'No Answer',
    icon: PhoneOff,
    color: 'text-orange-600 dark:text-orange-400',
    bgColor: 'bg-orange-100 dark:bg-orange-950'
  },
  failed: {
    label: 'Failed',
    icon: AlertCircle,
    color: 'text-gray-600 dark:text-gray-400',
    bgColor: 'bg-gray-100 dark:bg-gray-950'
  },
}

export function LeadStatusStats() {
  const { data, isLoading, error } = useQuery<LeadStatusData>({
    queryKey: ['lead-status-distribution'],
    queryFn: getLeadStatusDistribution,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Lead Status Distribution</CardTitle>
          <CardDescription>Current status of all leads in the system</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-2">
                <div className="flex items-center justify-between">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-16" />
                </div>
                <Skeleton className="h-2 w-full" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Lead Status Distribution</CardTitle>
          <CardDescription>Current status of all leads in the system</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <AlertCircle className="mr-2 h-5 w-5" />
            <p>Failed to load lead statistics</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const statuses = data?.statuses || []
  const total = data?.total || 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Lead Status Distribution</span>
          <Badge variant="outline" className="text-sm font-normal">
            Total: {total}
          </Badge>
        </CardTitle>
        <CardDescription>Current status of all leads in the system</CardDescription>
      </CardHeader>
      <CardContent>
        {statuses.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <List className="mb-3 h-12 w-12 opacity-20" />
            <p className="text-sm">No leads found</p>
          </div>
        ) : (
          <div className="space-y-6">
            {statuses
              .sort((a, b) => b.count - a.count) // Sort by count descending
              .map((statusItem) => {
                const config = statusConfig[statusItem.status] || {
                  label: statusItem.status,
                  icon: AlertCircle,
                  color: 'text-gray-600',
                  bgColor: 'bg-gray-100',
                }
                const Icon = config.icon

                return (
                  <div key={statusItem.status} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`rounded-full p-1.5 ${config.bgColor}`}>
                          <Icon className={`h-4 w-4 ${config.color}`} />
                        </div>
                        <span className="text-sm font-medium">{config.label}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-semibold">{statusItem.count}</span>
                        <Badge variant="secondary" className="text-xs">
                          {statusItem.percentage}%
                        </Badge>
                      </div>
                    </div>
                    <Progress
                      value={statusItem.percentage}
                      className="h-2"
                    />
                  </div>
                )
              })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
