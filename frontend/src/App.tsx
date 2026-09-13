import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TimelineSidebar } from './components/TimelineSidebar';
import { ChatInterface } from './components/ChatInterface';
import { UploadModal } from './components/UploadModal';
import { SourceSlideout } from './components/SourceSlideout';
import { HistoryDrawer } from './components/HistoryDrawer';
import { Course, NoteSource, ChatSession, ChatMessage } from './types';
import { fetchSyllabus, DEFAULT_COURSES } from './services/api';
import { CheckCircle2, X } from 'lucide-react';
import {
  getStoredSessions,
  getActiveSessionId,
  setActiveSessionId,
  createNewSession,
  updateSession,
  deleteStoredSession,
  clearAllSessions
} from './services/sessionStore';

export function App() {
  const [courses, setCourses] = useState<Course[]>(DEFAULT_COURSES);
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null);
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [sources, setSources] = useState<NoteSource[]>([]);
  const [activeSourceIndex, setActiveSourceIndex] = useState<number>(0);
  const [isSlideoutOpen, setIsSlideoutOpen] = useState<boolean>(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [isMobileSyllabusOpen, setIsMobileSyllabusOpen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Chat Session Management
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionIdState] = useState<string | null>(null);

  const loadSyllabus = async () => {
    try {
      const syllabusList = await fetchSyllabus();
      if (syllabusList && syllabusList.length > 0) {
        setCourses(syllabusList);
      }
    } catch (err) {
      console.error('Failed to sync live syllabus:', err);
    }
  };

  useEffect(() => {
    loadSyllabus();

    // Load Chat Sessions from localStorage
    const stored = getStoredSessions();
    if (stored.length > 0) {
      setSessions(stored);
      const activeId = getActiveSessionId();
      if (activeId && stored.some(s => s.id === activeId)) {
        setActiveSessionIdState(activeId);
        const active = stored.find(s => s.id === activeId);
        if (active) {
          setSelectedCourseId(active.course_id);
          setSelectedWeek(active.week_number);
        }
      } else {
        setActiveSessionIdState(stored[0].id);
        setActiveSessionId(stored[0].id);
        setSelectedCourseId(stored[0].course_id);
        setSelectedWeek(stored[0].week_number);
      }
    } else {
      const initialGreeting: ChatMessage = {
        id: 'msg-welcome',
        role: 'assistant',
        content: `Welcome to CampusVault — Universal Academic Assistant.\n\nAsk any question across your curriculum (e.g., Data Structures, Operating Systems, Computer Networks). You can select a specific syllabus week on the left or type your question directly for autonomous cross-course retrieval.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      const newSess = createNewSession(null, null, [initialGreeting]);
      setSessions([newSess]);
      setActiveSessionIdState(newSess.id);
    }
  }, []);

  const handleNewChat = () => {
    const initialGreeting: ChatMessage = {
      id: `msg-welcome-${Date.now()}`,
      role: 'assistant',
      content: `Ready for a new inquiry. Ask any question or select a syllabus week to begin.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    const newSess = createNewSession(null, null, [initialGreeting]);
    setSessions(prev => [newSess, ...prev.filter(s => s.id !== newSess.id)]);
    setActiveSessionIdState(newSess.id);
    setSelectedCourseId(null);
    setSelectedWeek(null);
  };

  const handleSelectSession = (session: ChatSession) => {
    setActiveSessionIdState(session.id);
    setActiveSessionId(session.id);
    setSelectedCourseId(session.course_id);
    setSelectedWeek(session.week_number);
  };

  const handleDeleteSession = (sessionId: string) => {
    const remaining = deleteStoredSession(sessionId);
    setSessions(remaining);
    if (activeSessionId === sessionId) {
      if (remaining.length > 0) {
        setActiveSessionIdState(remaining[0].id);
        setSelectedCourseId(remaining[0].course_id);
        setSelectedWeek(remaining[0].week_number);
      } else {
        handleNewChat();
      }
    }
  };

  const handleClearAll = () => {
    clearAllSessions();
    const initialGreeting: ChatMessage = {
      id: `msg-welcome-${Date.now()}`,
      role: 'assistant',
      content: `Chat history cleared. How can I assist you with your academic studies?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    const newSess = createNewSession(null, null, [initialGreeting]);
    setSessions([newSess]);
    setActiveSessionIdState(newSess.id);
    setSelectedCourseId(null);
    setSelectedWeek(null);
    setIsHistoryOpen(false);
  };

  const handleUpdateSessionMessages = (
    sessionId: string,
    newMessages: ChatMessage[],
    title?: string
  ) => {
    const updates: Partial<ChatSession> = {
      messages: newMessages,
      course_id: selectedCourseId,
      week_number: selectedWeek
    };
    if (title) updates.title = title;

    updateSession(sessionId, updates);
    setSessions(prev =>
      prev.map(s => (s.id === sessionId ? { ...s, ...updates, updated_at: new Date().toISOString() } : s))
    );
  };

  const handleSelectTopic = (courseId: string | null, week: number | null) => {
    setSelectedCourseId(courseId);
    setSelectedWeek(week);
    if (activeSessionId) {
      updateSession(activeSessionId, { course_id: courseId, week_number: week });
      setSessions(prev =>
        prev.map(s => (s.id === activeSessionId ? { ...s, course_id: courseId, week_number: week } : s))
      );
    }
  };

  const handleOpenSources = (newSources: NoteSource[]) => {
    setSources(newSources);
    setActiveSourceIndex(0);
    setIsSlideoutOpen(true);
  };

  const handleUploadSuccess = (fileName: string) => {
    setToastMessage(fileName);
    loadSyllabus();
    setTimeout(() => {
      setToastMessage(null);
    }, 5000);
  };

  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0] || null;

  return (
    <div className="min-h-screen bg-blueprint-canvas flex flex-col text-blueprint-primary selection:bg-blueprint-brass/30 selection:text-amber-200">
      
      {/* Top Navigation */}
      <Header
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onOpenSyllabus={() => setIsMobileSyllabusOpen(true)}
        onNewChat={handleNewChat}
        sessionCount={sessions.length}
      />

      {/* Floating Global Toast Notification */}
      {toastMessage && (
        <div className="fixed top-14 right-4 z-50 flex items-center gap-3 bg-blueprint-raised border border-blueprint-emerald/60 text-blueprint-primary px-4 py-3 rounded shadow-2xl animate-in fade-in slide-in-from-top duration-200 max-w-md">
          <div className="w-8 h-8 rounded-full bg-blueprint-emerald/20 border border-blueprint-emerald/40 flex items-center justify-center text-blueprint-emerald flex-shrink-0">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-blueprint-primary font-sans">
              Material Indexed Successfully
            </p>
            <p className="text-[11px] font-mono text-blueprint-secondary truncate">
              "{toastMessage}" is now active for grounding!
            </p>
          </div>
          <button
            onClick={() => setToastMessage(null)}
            className="text-blueprint-muted hover:text-blueprint-primary p-1 rounded hover:bg-blueprint-subtle transition"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Main App Workspace */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto p-2 sm:p-3 lg:p-4 flex flex-col lg:flex-row gap-3 relative">
        
        {/* Left: Universal Syllabus Timeline Navigation with Search */}
        <TimelineSidebar
          courses={courses}
          selectedCourseId={selectedCourseId}
          selectedWeek={selectedWeek}
          onSelectTopic={handleSelectTopic}
          isMobileOpen={isMobileSyllabusOpen}
          onCloseMobile={() => setIsMobileSyllabusOpen(false)}
        />

        {/* Center: Universal Contextual Chat Interface */}
        <ChatInterface
          courses={courses}
          selectedCourseId={selectedCourseId}
          selectedWeek={selectedWeek}
          activeSession={activeSession}
          onUpdateSessionMessages={handleUpdateSessionMessages}
          onSelectTopic={handleSelectTopic}
          onOpenSources={handleOpenSources}
          onOpenUpload={() => setIsUploadOpen(true)}
        />

      </main>

      {/* History Drawer (Slide-over panel) */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onClearAll={handleClearAll}
      />

      {/* Senior Ingestion Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        courses={courses}
        onUploadSuccess={handleUploadSuccess}
      />

      {/* Source Slideout Panel */}
      <SourceSlideout
        isOpen={isSlideoutOpen}
        onClose={() => setIsSlideoutOpen(false)}
        sources={sources}
        activeSourceIndex={activeSourceIndex}
        onSelectSourceIndex={(idx) => setActiveSourceIndex(idx)}
      />

    </div>
  );
}

export default App;

