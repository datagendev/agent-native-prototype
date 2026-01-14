import React, { useState } from 'react';
import Home from './components/Home';
import TableView from './components/TableView';
import WorkflowView from './components/WorkflowView';
import { Button } from './components/ui/button';
import { Home as HomeIcon, Table as TableIcon, Activity } from 'lucide-react';

type View = 'home' | 'table' | 'workflow';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('home');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const handleNavigate = (view: View) => {
    setCurrentView(view);
  };

  const handleSelectFile = (file: string) => {
    setSelectedFile(file);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100">
      {/* Navigation */}
      {currentView !== 'home' && (
        <header className="sticky top-0 z-30 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
          <div className="container flex h-14 items-center">
            <div className="mr-4 flex">
              <Button 
                variant="ghost" 
                className="mr-2 gap-2"
                onClick={() => {
                  setCurrentView('home');
                  setSelectedFile(null);
                }}
              >
                <HomeIcon className="h-4 w-4" />
                <span className="hidden font-bold sm:inline-block">Dashboard</span>
              </Button>
            </div>
            
            <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                <nav className="flex items-center space-x-2">
                    <Button 
                        variant={currentView === 'table' ? 'secondary' : 'ghost'}
                        size="sm"
                        onClick={() => setCurrentView('table')}
                    >
                        <TableIcon className="mr-2 h-4 w-4" />
                        Data Table
                    </Button>
                    <Button 
                        variant={currentView === 'workflow' ? 'secondary' : 'ghost'}
                        size="sm"
                        onClick={() => setCurrentView('workflow')}
                    >
                        <Activity className="mr-2 h-4 w-4" />
                        Analysis
                    </Button>
                </nav>
            </div>
          </div>
        </header>
      )}

      {/* Views */}
      <main>
        {currentView === 'home' && <Home onNavigate={handleNavigate} onSelectFile={handleSelectFile} />}
        {currentView === 'table' && <TableView fileName={selectedFile} />}
        {currentView === 'workflow' && <WorkflowView fileName={selectedFile} />}
      </main>
    </div>
  );
}