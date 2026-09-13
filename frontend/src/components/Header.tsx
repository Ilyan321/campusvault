import React from 'react';
import { UploadCloud, BookOpen, Plus, Clock, Sparkles, Menu, Layers } from 'lucide-react';

interface HeaderProps {
  onOpenUpload: () => void;
  onOpenHistory: () => void;
  onOpenSyllabus: () => void;
  onNewChat: () => void;
  sessionCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenUpload,
  onOpenHistory,
  onOpenSyllabus,
  onNewChat,
  sessionCount
}) => {
  return (
    <header className="sticky top-0 z-30 w-full border-b border-blueprint-border bg-blueprint-surface px-2.5 sm:px-6 py-2 shadow-sm">
      <div className="max-w-[1600px] mx-auto flex items-center justify-between gap-1.5 sm:gap-3">
        
        {/* Brand & Identity + Mobile Menu Button */}
        <div className="flex items-center gap-1.5 sm:gap-2.5 flex-shrink-0">
          
          {/* Mobile Syllabus Drawer Trigger */}
          <button
            onClick={onOpenSyllabus}
            className="lg:hidden flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded border border-blueprint-border bg-blueprint-raised text-blueprint-brass hover:text-white transition active:scale-[0.98]"
            title="Browse Curriculum & Syllabus"
            aria-label="Open Syllabus Menu"
          >
            <Layers className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          </button>

          <div className="hidden xs:flex w-7 h-7 sm:w-8 sm:h-8 rounded bg-blueprint-raised border border-blueprint-border items-center justify-center text-blueprint-brass flex-shrink-0 shadow-sm">
            <BookOpen className="w-3.5 h-3.5 sm:w-4 sm:h-4 stroke-[2]" />
          </div>
          
          <span className="font-semibold text-xs sm:text-sm tracking-tight text-blueprint-primary">
            CampusVault
          </span>
          <span className="text-[11px] text-blueprint-muted hidden md:inline-flex items-center gap-1.5 border-l border-blueprint-border pl-2 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-blueprint-emerald animate-pulse" />
            <span>Grounded Knowledge Engine</span>
          </span>
        </div>

        {/* Right Action Controls */}
        <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
          
          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            className="flex items-center gap-1 px-2 sm:px-3 py-1.5 rounded border border-blueprint-border hover:border-blueprint-borderLight hover:bg-blueprint-raised text-blueprint-secondary hover:text-blueprint-primary font-mono text-xs transition active:scale-[0.98]"
            title="Start a new chat session"
          >
            <Plus className="w-3.5 h-3.5 text-blueprint-brass stroke-[2.5]" />
            <span className="hidden sm:inline">New Session</span>
          </button>

          {/* History Drawer Trigger */}
          <button
            onClick={onOpenHistory}
            className="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1.5 rounded border border-blueprint-border hover:border-blueprint-borderLight hover:bg-blueprint-raised text-blueprint-secondary hover:text-blueprint-primary font-mono text-xs transition active:scale-[0.98]"
            title="Open saved chat sessions"
          >
            <Clock className="w-3.5 h-3.5 text-blueprint-secondary stroke-[2]" />
            <span className="hidden sm:inline">History</span>
            {sessionCount > 0 && (
              <span className="text-[10px] bg-blueprint-subtle px-1.5 py-0.5 rounded border border-blueprint-border text-blueprint-primary font-mono font-medium">
                {sessionCount}
              </span>
            )}
          </button>

          {/* Upload Notes Button */}
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-1 px-2.5 sm:px-3.5 py-1.5 rounded bg-blueprint-primary hover:bg-white text-blueprint-canvas font-semibold text-xs transition active:scale-[0.98] shadow-sm"
          >
            <UploadCloud className="w-3.5 h-3.5 stroke-[2.2]" />
            <span className="hidden sm:inline">Upload Notes</span>
            <span className="sm:hidden">Upload</span>
          </button>
        </div>

      </div>
    </header>
  );
};



