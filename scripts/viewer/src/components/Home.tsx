import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { FileText, Clock, Database, ChevronRight, Loader2 } from 'lucide-react';

interface FileInfo {
  name: string;
  size: string;
  mtime: string;
  path: string;
}

interface HomeProps {
  onNavigate: (view: 'home' | 'table' | 'workflow') => void;
  onSelectFile: (file: string) => void;
}

export default function Home({ onNavigate, onSelectFile }: HomeProps) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/files')
      .then(res => res.json())
      .then(data => {
        if (data.error) throw new Error(data.error);
        setFiles(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-red-500">
        Error loading files: {error}
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8 max-w-5xl">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Enrichment Dashboard</h1>
        <p className="mt-2 text-slate-500">Select an enriched dataset to visualize and analyze.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {files.length === 0 ? (
           <div className="col-span-full text-center text-slate-500 py-12">
             No enriched files found in lead-list directory.
           </div>
        ) : (
          files.map((file) => (
            <Card key={file.name} className="group relative overflow-hidden transition-all hover:shadow-md hover:border-slate-300">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="rounded-full bg-blue-50 p-2.5">
                    <Database className="h-5 w-5 text-blue-600" />
                  </div>
                  <Badge variant="secondary" className="font-mono text-xs">
                    {file.size}
                  </Badge>
                </div>
                <CardTitle className="mt-4 text-base font-medium break-all line-clamp-2">
                  {file.name.replace('_enriched.csv', '')}
                </CardTitle>
                <CardDescription className="flex items-center gap-1.5 text-xs">
                  <Clock className="h-3 w-3" />
                  {new Date(file.mtime).toLocaleDateString()} {new Date(file.mtime).toLocaleTimeString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button 
                    className="w-full" 
                    onClick={() => {
                      onSelectFile(file.name);
                      onNavigate('table');
                    }}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    View Data
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}