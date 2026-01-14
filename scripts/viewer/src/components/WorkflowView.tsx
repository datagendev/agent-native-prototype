import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Loader2, CheckCircle, AlertCircle, BarChart3 } from 'lucide-react';

interface WorkflowViewProps {
  fileName: string | null;
}

export default function WorkflowView({ fileName }: WorkflowViewProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!fileName) return;
    setLoading(true);
    fetch(`/api/workflow?file=${fileName}`)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [fileName]);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!data) return <div className="p-8 text-center text-slate-500">No workflow data available.</div>;

  return (
    <div className="container mx-auto p-8 max-w-6xl space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Enrichment Analysis</h2>
        <Badge variant="outline" className="text-base px-3 py-1">
          {fileName}
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Rows</CardTitle>
            <BarChart3 className="h-4 w-4 text-slate-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.totalRows}</div>
            <p className="text-xs text-slate-500">Leads in dataset</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enriched Columns</CardTitle>
            <DatabaseIcon className="h-4 w-4 text-slate-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.enrichedColumns}</div>
            <p className="text-xs text-slate-500">Data points added</p>
          </CardContent>
        </Card>
      </div>

      <h3 className="text-lg font-semibold text-slate-900 mt-8 mb-4">Integrations Performance</h3>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(data.integrations).map(([key, value]: [string, any]) => (
          <Card key={key} className="overflow-hidden">
            <CardHeader className="bg-slate-50/50 pb-4 border-b">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-medium capitalize">
                  {key.replace(/_/g, ' ')}
                </CardTitle>
                <Badge 
                  variant={parseFloat(value.successRate) > 80 ? 'success' : parseFloat(value.successRate) > 50 ? 'warning' : 'destructive'}
                >
                  {value.successRate}%
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-500">Enriched</p>
                  <p className="font-medium text-slate-900 flex items-center gap-1">
                    <CheckCircle className="h-3 w-3 text-green-500" /> {value.populated}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500">Missing</p>
                  <p className="font-medium text-slate-900 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3 text-red-500" /> {value.empty}
                  </p>
                </div>
              </div>
              <div>
                 <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">Fields</p>
                 <div className="flex flex-wrap gap-1">
                    {value.columns.map((col: string) => (
                        <span key={col} className="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600 ring-1 ring-inset ring-slate-500/10">
                            {col}
                        </span>
                    ))}
                 </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function DatabaseIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s 9-1.34 9-3V5" />
    </svg>
  )
}