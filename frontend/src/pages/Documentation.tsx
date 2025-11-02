import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BookOpen,
  Code,
  Key,
  Shield,
  Zap,
  CheckCircle,
  AlertCircle,
  Copy,
  Check,
  ExternalLink,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';

export default function Documentation() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const pythonExample = `import requests

API_URL = "https://your-platform.com/api/leads/partner-transfer"
API_KEY = "your_api_key_here"

def transfer_leads(leads):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    payload = {"leads": leads}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Example usage
leads = [
    {
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john@example.com"
    }
]

result = transfer_leads(leads)
print(f"Created {result['created']} leads")`;

  const curlExample = `curl -X POST https://your-platform.com/api/leads/partner-transfer \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your_api_key_here" \\
  -d '{
    "leads": [
      {
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john@example.com"
      }
    ]
  }'`;

  const javascriptExample = `const axios = require('axios');

const API_URL = 'https://your-platform.com/api/leads/partner-transfer';
const API_KEY = 'your_api_key_here';

async function transferLeads(leads) {
  try {
    const response = await axios.post(
      API_URL,
      { leads },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        }
      }
    );

    console.log(\`Created \${response.data.created} leads\`);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data);
    throw error;
  }
}`;

  const responseExample = `{
  "success": true,
  "total_submitted": 10,
  "created": 8,
  "skipped": 2,
  "failed": 0,
  "errors": [
    {
      "index": 3,
      "phone": "+1234567890",
      "reason": "Phone number already exists (Lead ID: 42)"
    }
  ],
  "message": "Successfully processed 8 out of 10 leads"
}`;

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
            <BookOpen className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-4xl font-bold">API Documentation</h1>
            <p className="text-muted-foreground mt-1">
              Partner API Integration Guide
            </p>
          </div>
        </div>
      </motion.div>

      {/* Quick Start Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <Key className="h-8 w-8 text-primary mb-2" />
            <CardTitle>Get API Key</CardTitle>
            <CardDescription>
              Contact admin to create your partner account and receive your API key
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <Shield className="h-8 w-8 text-primary mb-2" />
            <CardTitle>Secure Auth</CardTitle>
            <CardDescription>
              All requests require API key authentication via X-API-Key header
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <Zap className="h-8 w-8 text-primary mb-2" />
            <CardTitle>Rate Limited</CardTitle>
            <CardDescription>
              Default limit: 100 leads per minute. Contact admin to adjust
            </CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Main Documentation */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="authentication">Authentication</TabsTrigger>
          <TabsTrigger value="endpoint">API Endpoint</TabsTrigger>
          <TabsTrigger value="examples">Code Examples</TabsTrigger>
          <TabsTrigger value="errors">Error Handling</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Partner API Overview</CardTitle>
              <CardDescription>
                Transfer leads securely to our AI Outbound Meeting Scheduler platform
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Key Features</h3>
                <div className="space-y-2">
                  {[
                    'Secure API key-based authentication',
                    'Bulk lead transfer in single request',
                    'Automatic language detection from phone numbers',
                    'Duplicate prevention and error reporting',
                    'Rate limiting protection',
                    'Real-time response with detailed status',
                  ].map((feature, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-lg font-semibold mb-3">Base URL</h3>
                <div className="bg-muted p-4 rounded-lg font-mono text-sm">
                  https://your-platform.com
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Endpoint</h3>
                <div className="flex items-center gap-2 bg-muted p-4 rounded-lg">
                  <Badge variant="default">POST</Badge>
                  <code className="flex-1 font-mono text-sm">/api/leads/partner-transfer</code>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Authentication Tab */}
        <TabsContent value="authentication" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Authentication</CardTitle>
              <CardDescription>
                How to authenticate your API requests
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">API Key Header</h3>
                <p className="text-muted-foreground mb-3">
                  Include your API key in the request headers:
                </p>
                <div className="bg-muted p-4 rounded-lg font-mono text-sm">
                  X-API-Key: your_api_key_here
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-lg font-semibold mb-3">Security Best Practices</h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-950 rounded-lg border border-amber-200 dark:border-amber-800">
                    <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-amber-900 dark:text-amber-100">Store API Keys Securely</p>
                      <p className="text-sm text-amber-700 dark:text-amber-200 mt-1">
                        Never hardcode API keys. Use environment variables or secret management systems.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                    <span>Always use HTTPS for API requests</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                    <span>Rotate API keys periodically</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                    <span>Implement retry logic with exponential backoff</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Endpoint Tab */}
        <TabsContent value="endpoint" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>POST /api/leads/partner-transfer</CardTitle>
              <CardDescription>
                Bulk transfer leads to the platform
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Request Body</h3>
                <div className="space-y-3">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <code className="text-sm font-semibold">leads</code>
                      <Badge variant="outline">Array (required)</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Array of lead objects to transfer</p>
                  </div>
                  <div className="border rounded-lg p-4 ml-4">
                    <div className="flex items-center justify-between mb-2">
                      <code className="text-sm">name</code>
                      <Badge variant="outline">String (required)</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Lead's full name</p>
                  </div>
                  <div className="border rounded-lg p-4 ml-4">
                    <div className="flex items-center justify-between mb-2">
                      <code className="text-sm">phone</code>
                      <Badge variant="outline">String (required)</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Phone number in international format (e.g., +1234567890)
                    </p>
                  </div>
                  <div className="border rounded-lg p-4 ml-4">
                    <div className="flex items-center justify-between mb-2">
                      <code className="text-sm">email</code>
                      <Badge variant="secondary">String (optional)</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Lead's email address</p>
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-lg font-semibold mb-3">Response Schema</h3>
                <div className="relative">
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute right-2 top-2"
                    onClick={() => copyToClipboard(responseExample, 'response')}
                  >
                    {copiedCode === 'response' ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                  <ScrollArea className="h-[400px] w-full rounded-lg border">
                    <pre className="p-4 text-sm">
                      <code>{responseExample}</code>
                    </pre>
                  </ScrollArea>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Examples Tab */}
        <TabsContent value="examples" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Code Examples
              </CardTitle>
              <CardDescription>
                Ready-to-use code snippets in multiple languages
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="python" className="space-y-4">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="python">Python</TabsTrigger>
                  <TabsTrigger value="javascript">JavaScript</TabsTrigger>
                  <TabsTrigger value="curl">cURL</TabsTrigger>
                </TabsList>

                <TabsContent value="python">
                  <div className="relative">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute right-2 top-2 z-10"
                      onClick={() => copyToClipboard(pythonExample, 'python')}
                    >
                      {copiedCode === 'python' ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                    <ScrollArea className="h-[500px] w-full rounded-lg border bg-muted">
                      <pre className="p-4 text-sm">
                        <code className="language-python">{pythonExample}</code>
                      </pre>
                    </ScrollArea>
                  </div>
                </TabsContent>

                <TabsContent value="javascript">
                  <div className="relative">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute right-2 top-2 z-10"
                      onClick={() => copyToClipboard(javascriptExample, 'javascript')}
                    >
                      {copiedCode === 'javascript' ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                    <ScrollArea className="h-[500px] w-full rounded-lg border bg-muted">
                      <pre className="p-4 text-sm">
                        <code className="language-javascript">{javascriptExample}</code>
                      </pre>
                    </ScrollArea>
                  </div>
                </TabsContent>

                <TabsContent value="curl">
                  <div className="relative">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute right-2 top-2 z-10"
                      onClick={() => copyToClipboard(curlExample, 'curl')}
                    >
                      {copiedCode === 'curl' ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                    <ScrollArea className="h-[500px] w-full rounded-lg border bg-muted">
                      <pre className="p-4 text-sm">
                        <code className="language-bash">{curlExample}</code>
                      </pre>
                    </ScrollArea>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Errors Tab */}
        <TabsContent value="errors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Error Codes & Handling</CardTitle>
              <CardDescription>
                Understanding API errors and how to handle them
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">HTTP Status Codes</h3>
                <div className="space-y-2">
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <Badge className="bg-green-500">200</Badge>
                    <div>
                      <p className="font-medium">Success</p>
                      <p className="text-sm text-muted-foreground">
                        Request processed (check response for per-lead status)
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <Badge variant="destructive">401</Badge>
                    <div>
                      <p className="font-medium">Unauthorized</p>
                      <p className="text-sm text-muted-foreground">
                        Invalid or missing API key
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <Badge variant="destructive">403</Badge>
                    <div>
                      <p className="font-medium">Forbidden</p>
                      <p className="text-sm text-muted-foreground">
                        Partner account is disabled
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <Badge variant="destructive">429</Badge>
                    <div>
                      <p className="font-medium">Too Many Requests</p>
                      <p className="text-sm text-muted-foreground">
                        Rate limit exceeded. Wait and retry.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <Badge variant="destructive">500</Badge>
                    <div>
                      <p className="font-medium">Server Error</p>
                      <p className="text-sm text-muted-foreground">
                        Contact support with request details
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Interactive API Explorer Link */}
      <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
        <CardContent className="flex items-center justify-between p-6">
          <div>
            <h3 className="text-lg font-semibold mb-1">Interactive API Explorer</h3>
            <p className="text-sm text-muted-foreground">
              Try out the API directly in your browser with Swagger UI
            </p>
          </div>
          <Button variant="default" asChild>
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
              Open API Docs
              <ExternalLink className="ml-2 h-4 w-4" />
            </a>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
