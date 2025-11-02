import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getLeads, uploadLeadsCSV, createLead, startCampaign } from '../services/api';
import { PageHeader } from '@/components/PageHeader';
import { DataTable } from '@/components/DataTable';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { TableSkeleton } from '@/components/LoadingStates';
import { EmptyState } from '@/components/EmptyState';
import {
  Upload,
  Plus,
  MoreHorizontal,
  Edit,
  Trash2,
  Phone as PhoneIcon,
  Users,
  FileText,
  Rocket,
} from 'lucide-react';
import { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface Lead {
  id: number;
  name: string;
  phone: string;
  email?: string;
  company?: string;
  status: 'pending' | 'calling' | 'contacted' | 'meeting_scheduled' | 'not_interested';
  language?: string;
  created_at: string;
}

const statusColors = {
  pending: 'bg-gray-100 text-gray-800',
  calling: 'bg-blue-100 text-blue-800',
  contacted: 'bg-green-100 text-green-800',
  meeting_scheduled: 'bg-purple-100 text-purple-800',
  not_interested: 'bg-red-100 text-red-800',
};

const statusLabels = {
  pending: 'Pending',
  calling: 'Calling',
  contacted: 'Contacted',
  meeting_scheduled: 'Meeting Scheduled',
  not_interested: 'Not Interested',
};

export default function Leads() {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [addLeadDialogOpen, setAddLeadDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isAddingLead, setIsAddingLead] = useState(false);
  const [isStartingCampaign, setIsStartingCampaign] = useState(false);

  // Add Lead form state
  const [newLead, setNewLead] = useState({
    name: '',
    phone: '',
    email: '',
  });

  const { data: leadsData, isLoading, refetch } = useQuery({
    queryKey: ['leads'],
    queryFn: () => getLeads(1, 100),
  });

  const leads: Lead[] = leadsData?.leads || [];

  const columns: ColumnDef<Lead>[] = [
    {
      accessorKey: 'name',
      header: 'Name',
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue('name')}</div>
      ),
    },
    {
      accessorKey: 'phone',
      header: 'Phone',
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <PhoneIcon className="h-4 w-4 text-muted-foreground" />
          <span>{row.getValue('phone')}</span>
        </div>
      ),
    },
    {
      accessorKey: 'email',
      header: 'Email',
      cell: ({ row }) => {
        const email = row.getValue('email') as string;
        return email ? (
          <div className="text-sm text-muted-foreground">{email}</div>
        ) : (
          <span className="text-xs text-muted-foreground">—</span>
        );
      },
    },
    {
      accessorKey: 'company',
      header: 'Company',
      cell: ({ row }) => {
        const company = row.getValue('company') as string;
        return company || <span className="text-xs text-muted-foreground">—</span>;
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => {
        const status = row.getValue('status') as keyof typeof statusColors;
        return (
          <Badge variant="secondary" className={cn('font-medium', statusColors[status])}>
            {statusLabels[status]}
          </Badge>
        );
      },
    },
    {
      accessorKey: 'language',
      header: 'Language',
      cell: ({ row }) => {
        const language = row.getValue('language') as string;
        return language ? (
          <Badge variant="outline">{language.toUpperCase()}</Badge>
        ) : (
          <span className="text-xs text-muted-foreground">—</span>
        );
      },
    },
    {
      id: 'actions',
      cell: () => {
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <PhoneIcon className="mr-2 h-4 w-4" />
                Call Now
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem>
                <FileText className="mr-2 h-4 w-4" />
                View Details
              </DropdownMenuItem>
              <DropdownMenuItem className="text-destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  const handleFileUpload = async () => {
    if (!uploadFile) return;

    setIsUploading(true);
    try {
      await uploadLeadsCSV(uploadFile);
      toast.success('Leads uploaded successfully!');
      setUploadDialogOpen(false);
      setUploadFile(null);
      refetch();
    } catch (error) {
      toast.error('Failed to upload leads. Please try again.');
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'text/csv') {
      setUploadFile(file);
    } else {
      toast.error('Please upload a CSV file');
    }
  };

  const handleAddLead = async () => {
    // Validate required fields
    if (!newLead.name.trim()) {
      toast.error('Name is required');
      return;
    }
    if (!newLead.phone.trim()) {
      toast.error('Phone number is required');
      return;
    }

    // Basic phone validation (must start with + and have at least 10 digits)
    const phoneRegex = /^\+\d{10,}$/;
    if (!phoneRegex.test(newLead.phone.trim())) {
      toast.error('Phone number must start with + and include country code (e.g., +1234567890)');
      return;
    }

    setIsAddingLead(true);
    try {
      await createLead({
        name: newLead.name.trim(),
        phone: newLead.phone.trim(),
        email: newLead.email.trim() || undefined,
      });
      toast.success('Lead added successfully!');
      setAddLeadDialogOpen(false);
      setNewLead({ name: '', phone: '', email: '' }); // Reset form
      refetch(); // Refresh the leads list
    } catch (error) {
      toast.error('Failed to add lead. Please try again.');
      console.error(error);
    } finally {
      setIsAddingLead(false);
    }
  };

  const handleStartCampaign = async () => {
    // Filter pending leads
    const pendingLeads = leads.filter(lead => lead.status === 'pending');

    if (pendingLeads.length === 0) {
      toast.error('No pending leads to call. Please add leads or check their status.');
      return;
    }

    // Confirm action
    const confirmed = window.confirm(
      `Start campaign to call ${pendingLeads.length} pending lead(s)? Calls will be queued and initiated automatically.`
    );

    if (!confirmed) {
      return;
    }

    setIsStartingCampaign(true);
    try {
      const leadIds = pendingLeads.map(lead => lead.id);
      const response = await startCampaign({
        name: `Campaign ${new Date().toLocaleString()}`,
        lead_ids: leadIds,
      });

      toast.success(response.message || `Campaign started! ${response.queued_leads} leads queued for calling.`);

      // Refresh leads list to show updated statuses
      setTimeout(() => {
        refetch();
      }, 1000);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to start campaign. Please try again.';
      toast.error(errorMessage);
      console.error(error);
    } finally {
      setIsStartingCampaign(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Leads Management"
        description="Manage and organize your outbound call leads"
        actions={
          <>
            <Button variant="outline" onClick={() => setAddLeadDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Lead
            </Button>
            <Button variant="outline" onClick={() => setUploadDialogOpen(true)}>
              <Upload className="mr-2 h-4 w-4" />
              Upload CSV
            </Button>
            <Button
              onClick={handleStartCampaign}
              disabled={isStartingCampaign || leads.filter(l => l.status === 'pending').length === 0}
            >
              <Rocket className="mr-2 h-4 w-4" />
              {isStartingCampaign ? 'Starting Campaign...' : 'Start Campaign'}
            </Button>
          </>
        }
      />

      {isLoading ? (
        <TableSkeleton rows={10} />
      ) : leads.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No leads yet"
          description="Get started by uploading a CSV file with your leads or adding them manually"
          action={{
            label: 'Upload CSV',
            onClick: () => setUploadDialogOpen(true),
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
            data={leads}
            searchKey="name"
            searchPlaceholder="Search leads by name..."
          />
        </motion.div>
      )}

      {/* Upload CSV Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent className="sm:max-w-xl">
          <DialogHeader>
            <DialogTitle>Upload Leads from CSV</DialogTitle>
            <DialogDescription>
              Upload a CSV file containing lead information. Required columns: name, phone
            </DialogDescription>
          </DialogHeader>

          <div
            className={cn(
              'border-2 border-dashed rounded-lg p-12 text-center transition-colors',
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center gap-2">
              <div className="rounded-full bg-muted p-4">
                <Upload className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium">
                  {uploadFile ? uploadFile.name : 'Drag and drop your CSV file here'}
                </p>
                <p className="text-xs text-muted-foreground">or</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => document.getElementById('csv-upload')?.click()}
              >
                Browse Files
              </Button>
              <input
                id="csv-upload"
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) setUploadFile(file);
                }}
              />
            </div>
          </div>

          {uploadFile && (
            <div className="rounded-lg bg-muted p-4">
              <p className="text-sm font-medium">Selected file:</p>
              <p className="text-xs text-muted-foreground">{uploadFile.name}</p>
              <p className="text-xs text-muted-foreground">
                {(uploadFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setUploadDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleFileUpload} disabled={!uploadFile || isUploading}>
              {isUploading ? 'Uploading...' : 'Upload'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Lead Dialog */}
      <Dialog open={addLeadDialogOpen} onOpenChange={setAddLeadDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add New Lead</DialogTitle>
            <DialogDescription>
              Enter the lead information to add them to your outbound campaign
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                placeholder="John Doe"
                value={newLead.name}
                onChange={(e) => setNewLead({ ...newLead, name: e.target.value })}
                disabled={isAddingLead}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone *</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="+1234567890"
                value={newLead.phone}
                onChange={(e) => setNewLead({ ...newLead, phone: e.target.value })}
                disabled={isAddingLead}
              />
              <p className="text-xs text-muted-foreground">
                Include country code (e.g., +1 for US, +44 for UK)
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email (Optional)</Label>
              <Input
                id="email"
                type="email"
                placeholder="john@example.com"
                value={newLead.email}
                onChange={(e) => setNewLead({ ...newLead, email: e.target.value })}
                disabled={isAddingLead}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setAddLeadDialogOpen(false);
                setNewLead({ name: '', phone: '', email: '' });
              }}
              disabled={isAddingLead}
            >
              Cancel
            </Button>
            <Button onClick={handleAddLead} disabled={isAddingLead}>
              {isAddingLead ? 'Adding...' : 'Add Lead'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
