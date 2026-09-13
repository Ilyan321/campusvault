import React, { useState, useRef, useEffect } from 'react';
import { Course, SyllabusWeek, ChatMessage, NoteSource, ChatSession } from '../types';
import { queryRAG, streamQueryRAG, QueryMeta } from '../services/api';
import { MarkdownRenderer } from './MarkdownRenderer';
import {
  Send,
  FileText,
  Copy,
  Check,
  AlertTriangle,
  RotateCcw,
  BookOpen,
  ArrowUpRight,
  Terminal,
  Loader2,
  Sparkles,
  ChevronDown,
  X,
  Layers,
  Code2,
  HelpCircle,
  Zap,
  Flame
} from 'lucide-react';

interface ChatInterfaceProps {
  courses: Course[];
  selectedCourseId: string | null;
  selectedWeek: number | null;
  activeSession: ChatSession | null;
  onUpdateSessionMessages: (sessionId: string, newMessages: ChatMessage[], title?: string) => void;
  onSelectTopic: (courseId: string | null, week: number | null) => void;
  onOpenSources: (sources: NoteSource[]) => void;
  onOpenUpload: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  courses,
  selectedCourseId,
  selectedWeek,
  activeSession,
  onUpdateSessionMessages,
  onSelectTopic,
  onOpenSources,
  onOpenUpload
}) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [rateLimitError, setRateLimitError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const lastUserMsgRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentCourse = courses.find((c) => c.course_id === selectedCourseId);
  const currentWeekInfo = (currentCourse && selectedWeek !== null)
    ? currentCourse.syllabus_timeline.find((w) => w.week === selectedWeek)
    : null;

  const messages = activeSession?.messages || [];
  const hasUserMessages = messages.some(m => m.role === 'user');

  // Auto-resize textarea height as user types
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleContainerScroll = () => {
    if (!messagesContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 140;
    setShowScrollBottom(!isNearBottom);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (messages.length <= 1) {
      scrollToBottom();
    }
  }, [activeSession?.id]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading || isStreaming || !activeSession) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const newMessagesWithUser = [...messages, userMessage];
    const isFirstQuestion = messages.filter(m => m.role === 'user').length === 0;
    const sessionTitle = isFirstQuestion 
      ? (textToSend.trim().length > 38 ? `${textToSend.trim().slice(0, 38)}...` : textToSend.trim())
      : undefined;

    // Multi-turn history memory (last 4 turns)
    const historyPayload = newMessagesWithUser
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .slice(-4)
      .map(m => ({ role: m.role, content: m.content }));

    onUpdateSessionMessages(activeSession.id, newMessagesWithUser, sessionTitle);
    if (!queryText) setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setLoading(true);
    setRateLimitError(null);

    // Smoothly scroll to the new question
    setTimeout(() => {
      lastUserMsgRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 60);

    const assistantMsgId = `ai-${Date.now()}`;
    let accumulatedContent = '';
    let streamMeta: QueryMeta = {};

    try {
      setIsStreaming(true);
      
      await streamQueryRAG(
        {
          query: textToSend.trim(),
          week_number: selectedWeek,
          course_id: selectedCourseId || undefined,
          history: historyPayload
        },
        (token: string) => {
          accumulatedContent += token;
          setLoading(false);
          
          const assistantMessage: ChatMessage = {
            id: assistantMsgId,
            role: 'assistant',
            content: accumulatedContent,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            sources: streamMeta.sources || [],
            auto_detected_week: streamMeta.auto_detected_week,
            detected_topic: streamMeta.detected_topic,
            language_mode: streamMeta.language_mode,
            isStreaming: true
          };
          onUpdateSessionMessages(activeSession.id, [...newMessagesWithUser, assistantMessage]);
        },
        (meta: QueryMeta) => {
          streamMeta = meta;
        }
      );

      const finalAssistantMessage: ChatMessage = {
        id: assistantMsgId,
        role: 'assistant',
        content: accumulatedContent,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: streamMeta.sources || [],
        auto_detected_week: streamMeta.auto_detected_week,
        detected_topic: streamMeta.detected_topic,
        language_mode: streamMeta.language_mode,
        isStreaming: false
      };
      onUpdateSessionMessages(activeSession.id, [...newMessagesWithUser, finalAssistantMessage]);

    } catch (streamErr: any) {
      console.warn('Streaming error, falling back to sync RAG query:', streamErr);
      
      try {
        const response = await queryRAG({
          query: textToSend.trim(),
          week_number: selectedWeek,
          course_id: selectedCourseId || undefined,
          history: historyPayload
        });

        const assistantMessage: ChatMessage = {
          id: assistantMsgId,
          role: 'assistant',
          content: response.answer,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          sources: response.sources,
          auto_detected_week: response.agentic_meta?.auto_detected_week || response.week_number || undefined,
          detected_topic: response.agentic_meta?.detected_topic,
          language_mode: response.agentic_meta?.language_mode,
          isStreaming: false
        };

        onUpdateSessionMessages(activeSession.id, [...newMessagesWithUser, assistantMessage]);
      } catch (err: any) {
        console.error('Chat query error:', err);
        setRateLimitError('Server rate limit or connection issue. Please retry in a moment.');
      }
    } finally {
      setLoading(false);
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // High-Yield Study Tracks
  const studyTracks = [
    {
      title: 'Queue Underflow & Modulo Arithmetic',
      desc: 'C++ Circular queue implementation, front/rear formula & full-state condition',
      tag: 'CSE-212 · DSA',
      prompt: 'How do queue underflow and circular modulo arithmetic work in C++ with code and edge cases?'
    },
    {
      title: "Dijkstra's Shortest Path & Priority Queue",
      desc: 'Greedy trace with adjacency list, relaxation step, and min-heap complexity',
      tag: 'CSE-212 · Graphs',
      prompt: "Explain Dijkstra's shortest path algorithm step-by-step with a trace example and min-heap time complexity."
    },
    {
      title: 'CIDR Subnetting /26 & Host Calculation',
      desc: 'Network ID, broadcast address, and usable IP math for exam problem solving',
      tag: 'CSE-305 · Networks',
      prompt: 'How do you calculate network ID, broadcast address, and usable host IPs in a CIDR /26 subnet?'
    },
    {
      title: "Banker's Algorithm & Safe State Trace",
      desc: 'Deadlock avoidance, resource allocation graph, and need matrix computation',
      tag: 'CSE-310 · OS',
      prompt: "Explain the Banker's algorithm safe sequence calculation step-by-step with an example allocation and need matrix."
    },
    {
      title: 'Database Normalization: 1NF to BCNF',
      desc: 'Functional dependencies, lossless join decomposition, and anomaly elimination',
      tag: 'CSE-315 · DBMS',
      prompt: 'Explain database normalization from 1NF to BCNF with concrete table examples and functional dependencies.'
    },
    {
      title: 'Eigenvalues & Diagonalization',
      desc: 'Characteristic equation det(A - λI) = 0 and linear independence check',
      tag: 'MATH-201 · Math',
      prompt: 'How do you find eigenvalues and eigenvectors for a 2x2 matrix with full step-by-step mathematical derivation?'
    }
  ];

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-5.5rem)] blueprint-panel rounded overflow-hidden">
      
      {/* Context Top Bar */}
      <div className="px-4 py-2 border-b border-blueprint-border bg-blueprint-surface flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2.5">
          <span className="font-mono text-[10px] font-bold text-blueprint-brass px-2 py-0.5 border border-blueprint-border bg-blueprint-raised rounded">
            {selectedWeek !== null ? `WEEK ${String(selectedWeek).padStart(2, '0')}` : 'UNIVERSAL'}
          </span>
          <div>
            <h2 className="text-xs font-semibold text-blueprint-primary flex items-center gap-1.5">
              {selectedWeek !== null ? (currentWeekInfo?.core_topic || 'Syllabus Topic') : 'Universal Academic Knowledge Base'}
            </h2>
            <p className="text-[10px] font-mono text-blueprint-muted">
              {selectedWeek !== null ? `Course: ${currentCourse?.course_id || 'Active'} • Focus Scope` : 'Multi-course semantic grounding across verified notes'}
            </p>
          </div>
        </div>

        {/* Clear active topic filter if set */}
        {(selectedCourseId !== null || selectedWeek !== null) && (
          <button
            onClick={() => onSelectTopic(null, null)}
            className="flex items-center gap-1 px-2 py-1 rounded bg-blueprint-raised hover:bg-blueprint-subtle text-blueprint-secondary hover:text-blueprint-primary border border-blueprint-border text-[11px] font-mono transition"
            title="Reset to All Subjects (Auto-Detect)"
          >
            <X className="w-3 h-3" />
            <span>Reset Scope</span>
          </button>
        )}
      </div>

      {/* Messages Feed */}
      <div
        ref={messagesContainerRef}
        onScroll={handleContainerScroll}
        className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-5 relative"
      >
        {/* Interactive Launchpad (Shown when no user messages yet) */}
        {!hasUserMessages && (
          <div className="max-w-4xl mx-auto py-4 space-y-6">
            
            {/* Launchpad Header */}
            <div className="p-4 rounded border border-blueprint-border bg-blueprint-surface space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blueprint-brass" />
                <span className="font-mono text-xs font-bold text-blueprint-brass uppercase tracking-wider">
                  Universal Academic Assistant
                </span>
              </div>
              <h1 className="text-sm lg:text-base font-bold text-blueprint-primary">
                Instant Exam Grounding, Algorithm Tracing & Code Explanations
              </h1>
              <p className="text-xs text-blueprint-secondary leading-relaxed">
                Ground your queries across 6 verified engineering subjects. Choose a syllabus week from the left panel for targeted revision, or select a high-yield study track below to start immediately.
              </p>
            </div>

            {/* High-Yield Study Track Cards */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between text-[11px] font-mono text-blueprint-muted px-1">
                <span className="flex items-center gap-1.5 font-semibold text-blueprint-secondary">
                  <Flame className="w-3.5 h-3.5 text-blueprint-brass" />
                  HIGH-YIELD EXAM TOPICS & PROMPTS
                </span>
                <span>1-Click to Run</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {studyTracks.map((track, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(track.prompt)}
                    className="text-left p-3 rounded border border-blueprint-border hover:border-blueprint-borderLight bg-blueprint-surface hover:bg-blueprint-raised transition flex flex-col justify-between gap-2 group active:scale-[0.99]"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-mono font-bold text-blueprint-brass px-1.5 py-0.2 rounded bg-blueprint-raised border border-blueprint-border">
                          {track.tag}
                        </span>
                        <ArrowUpRight className="w-3.5 h-3.5 text-blueprint-muted group-hover:text-blueprint-brass transition-colors" />
                      </div>
                      <h3 className="text-xs font-semibold text-blueprint-primary group-hover:text-white">
                        {track.title}
                      </h3>
                      <p className="text-[11px] text-blueprint-muted mt-1 leading-relaxed line-clamp-2">
                        {track.desc}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* Existing Messages */}
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          const isLastUser = isUser && idx === messages.map(m => m.role).lastIndexOf('user');

          // Don't show initial placeholder greeting once user starts chatting
          if (!isUser && msg.id === 'msg-welcome' && hasUserMessages) {
            return null;
          }

          return (
            <div
              key={msg.id}
              ref={isLastUser ? lastUserMsgRef : undefined}
              className="max-w-4xl w-full min-w-0 space-y-1 mx-auto"
            >
              
              {/* Header Meta / Sender */}
              <div className="flex items-center justify-between text-[11px] font-mono text-blueprint-muted px-1">
                <div className="flex items-center gap-2">
                  <span className={`font-semibold ${isUser ? 'text-blueprint-cobalt font-mono' : 'text-blueprint-brass'}`}>
                    {isUser ? 'Student' : 'CampusVault'}
                  </span>
                  {!isUser && msg.auto_detected_week && msg.detected_topic && (
                    <span className="text-blueprint-muted">
                      [ROUTED: W{String(msg.auto_detected_week).padStart(2, '0')} // {msg.detected_topic}]
                    </span>
                  )}
                </div>
                <span>{msg.timestamp}</span>
              </div>

              {/* Message Body */}
              <div
                className={`p-4 rounded border text-xs lg:text-sm leading-relaxed w-full min-w-0 overflow-hidden break-words [overflow-wrap:anywhere] ${
                  isUser
                    ? 'bg-blueprint-surface border-blueprint-border text-blueprint-primary'
                    : 'bg-blueprint-surface/90 border-blueprint-border text-blueprint-primary'
                }`}
              >
                {/* Notice when answering via General AI parametric knowledge without local peer notes */}
                {!isUser && typeof msg?.id === 'string' && !msg.id.startsWith('msg-welcome') && (!msg.sources || msg.sources.length === 0) && msg.content && !msg.isStreaming && (
                  <div className="mb-3.5 pb-2.5 border-b border-blueprint-border/60 flex items-center justify-between gap-2 text-[11px] font-mono bg-blueprint-raised px-3 py-2 rounded border border-blueprint-border">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-3.5 h-3.5 text-blueprint-brass flex-shrink-0" />
                      <span className="text-blueprint-brass font-medium">Quick AI Overview</span>
                      <span className="text-blueprint-muted">· Parametric knowledge mode</span>
                    </div>
                    <span className="text-[10px] text-blueprint-muted hidden sm:inline font-mono">General Knowledge</span>
                  </div>
                )}

                {isUser ? (
                  <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere] font-sans text-blueprint-primary">{msg.content}</div>
                ) : (
                  <MarkdownRenderer content={msg.content} />
                )}

                {/* Sources & Citations */}
                {!isUser && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3.5 pt-3 border-t border-blueprint-border flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-1.5 text-[11px] font-mono text-blueprint-muted">
                      <FileText className="w-3.5 h-3.5 text-blueprint-secondary" />
                      <span>Grounding: Referenced {msg.sources.length} verified senior peer source{msg.sources.length > 1 ? 's' : ''}</span>
                    </div>
                    <button
                      onClick={() => onOpenSources(msg.sources!)}
                      className="text-[11px] font-mono font-medium px-2.5 py-1 rounded bg-blueprint-raised hover:bg-blueprint-subtle text-blueprint-primary border border-blueprint-border hover:border-blueprint-borderLight transition flex items-center gap-1 shadow-sm"
                    >
                      <span>Inspect Notes</span>
                      <ArrowUpRight className="w-3 h-3 text-blueprint-brass" />
                    </button>
                  </div>
                )}
              </div>

              {/* Message Utilities */}
              <div className="flex items-center justify-end px-1 text-[10px] font-mono text-blueprint-muted">
                {!isUser && (
                  <button
                    onClick={() => copyToClipboard(msg.content, msg.id)}
                    className="hover:text-blueprint-primary flex items-center gap-1 transition px-1.5 py-0.5 rounded hover:bg-blueprint-raised"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3 h-3 text-blueprint-emerald" />
                        <span className="text-blueprint-emerald">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                )}
              </div>

            </div>
          );
        })}

        {/* Structured Workstation Skeleton Screen */}
        {loading && (
          <div className="max-w-4xl mx-auto space-y-2 animate-pulse" aria-busy="true" aria-label="Loading grounding answer">
            <div className="flex items-center justify-between text-[11px] font-mono px-1">
              <div className="flex items-center gap-2">
                <span className="text-blueprint-brass font-semibold">❯ RETRIEVING PEER GROUNDING...</span>
                <div className="h-3 w-32 bg-blueprint-raised rounded border border-blueprint-border" />
              </div>
              <div className="h-3 w-12 bg-blueprint-raised rounded" />
            </div>

            <div className="p-4 rounded border border-blueprint-border bg-blueprint-surface/90 space-y-3">
              <div className="space-y-2">
                <div className="h-3.5 bg-blueprint-raised rounded w-full border border-blueprint-border/40" />
                <div className="h-3.5 bg-blueprint-raised rounded w-11/12 border border-blueprint-border/40" />
                <div className="h-3.5 bg-blueprint-raised rounded w-4/5 border border-blueprint-border/40" />
                <div className="h-3.5 bg-blueprint-raised rounded w-3/4 border border-blueprint-border/40" />
              </div>

              <div className="p-3 bg-blueprint-canvas rounded border border-blueprint-border space-y-2 my-2 font-mono">
                <div className="flex items-center justify-between pb-1.5 border-b border-blueprint-border/50">
                  <div className="h-2.5 w-24 bg-blueprint-raised rounded" />
                  <div className="h-2.5 w-10 bg-blueprint-raised rounded" />
                </div>
                <div className="h-3 bg-blueprint-raised/80 rounded w-2/3" />
                <div className="h-3 bg-blueprint-raised/80 rounded w-1/2" />
                <div className="h-3 bg-blueprint-raised/80 rounded w-3/5" />
              </div>

              <div className="pt-3 border-t border-blueprint-border flex items-center justify-between">
                <div className="h-3 w-44 bg-blueprint-raised rounded" />
                <div className="h-6 w-24 bg-blueprint-raised rounded border border-blueprint-border" />
              </div>
            </div>
          </div>
        )}

        {/* Rate Limit Error Banner */}
        {rateLimitError && (
          <div className="max-w-4xl mx-auto p-3 rounded border border-blueprint-ruby/40 bg-blueprint-surface text-blueprint-ruby text-xs flex items-center justify-between gap-3 font-mono">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{rateLimitError}</span>
            </div>
            <button
              onClick={() => handleSend()}
              className="flex items-center gap-1 font-semibold text-blueprint-primary hover:underline px-2 py-1 rounded bg-blueprint-raised border border-blueprint-border"
            >
              <RotateCcw className="w-3 h-3" />
              Retry
            </button>
          </div>
        )}

        {/* Floating Jump to Latest Button */}
        {showScrollBottom && (
          <div className="sticky bottom-2 flex justify-end pointer-events-none z-20 max-w-4xl mx-auto">
            <button
              type="button"
              onClick={scrollToBottom}
              className="pointer-events-auto flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blueprint-raised hover:bg-blueprint-subtle text-blueprint-primary border border-blueprint-brass/60 shadow-xl text-xs font-mono transition-all duration-150"
            >
              <span>Jump to latest</span>
              <ChevronDown className="w-3.5 h-3.5 text-blueprint-brass" />
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Multiline Composer Dock */}
      <div className="p-3 border-t border-blueprint-border bg-blueprint-surface">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="max-w-4xl mx-auto flex flex-col gap-2"
        >
          {/* Active Scope Indicator inside the dock */}
          <div className="flex items-center justify-between text-[10px] font-mono text-blueprint-muted px-1">
            <div className="flex items-center gap-1.5">
              <span className="text-blueprint-brass font-bold">FOCUS:</span>
              <span className="text-blueprint-secondary">
                {selectedWeek !== null 
                  ? `${currentCourse?.course_id || 'Course'} · Week ${selectedWeek} (${currentWeekInfo?.core_topic || 'Selected Topic'})` 
                  : 'Universal Multi-Subject Grounding'}
              </span>
            </div>
            <div className="hidden sm:flex items-center gap-2 text-blueprint-muted">
              <span><kbd className="px-1 py-0.5 rounded bg-blueprint-raised border border-blueprint-border text-[9px]">Enter</kbd> to send</span>
              <span><kbd className="px-1 py-0.5 rounded bg-blueprint-raised border border-blueprint-border text-[9px]">Shift+Enter</kbd> for newline</span>
            </div>
          </div>

          <div className="flex items-end gap-2 bg-blueprint-raised rounded border border-blueprint-border focus-within:border-blueprint-brass transition p-2">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask any computer science, algorithm, or engineering question..."
              disabled={loading}
              className="flex-1 bg-transparent text-blueprint-primary text-xs lg:text-sm resize-none focus:outline-none placeholder:text-blueprint-muted/60 max-h-40 leading-relaxed font-sans"
            />

            {input.trim() && (
              <button
                type="button"
                onClick={() => setInput('')}
                className="text-blueprint-muted hover:text-blueprint-primary p-1 rounded transition mb-0.5"
                title="Clear input"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}

            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-blueprint-primary hover:bg-white disabled:opacity-40 disabled:hover:bg-blueprint-primary text-blueprint-canvas font-semibold text-xs transition flex-shrink-0 active:scale-[0.98] shadow-sm mb-0.5"
            >
              <span>Send</span>
              <Send className="w-3.5 h-3.5 stroke-[2.2]" />
            </button>
          </div>
        </form>
      </div>

    </div>
  );
};

