import { ChatSession, ChatMessage } from '../types';

const SESSIONS_STORAGE_KEY = 'campusvault_chat_sessions';
const ACTIVE_SESSION_ID_KEY = 'campusvault_active_session_id';

export function getStoredSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSIONS_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((s): s is ChatSession => Boolean(s && typeof s === 'object' && s.id && Array.isArray(s.messages)))
      .map((s) => ({
        id: String(s.id),
        title: String(s.title || 'Academic Inquiry'),
        created_at: String(s.created_at || new Date().toISOString()),
        updated_at: String(s.updated_at || new Date().toISOString()),
        course_id: s.course_id || null,
        week_number: typeof s.week_number === 'number' ? s.week_number : null,
        messages: (s.messages || []).map((m: any, idx: number) => ({
          id: String(m?.id || `msg-${idx}`),
          role: m?.role === 'user' ? 'user' : 'assistant',
          content: String(m?.content || ''),
          timestamp: String(m?.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })),
          sources: Array.isArray(m?.sources) ? m.sources : [],
          auto_detected_week: m?.auto_detected_week,
          detected_topic: m?.detected_topic,
          language_mode: m?.language_mode
        }))
      }));
  } catch (err) {
    console.error('Failed to parse stored chat sessions:', err);
    return [];
  }
}

export function saveStoredSessions(sessions: ChatSession[]): void {
  try {
    localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(sessions));
  } catch (err) {
    console.error('Failed to save chat sessions to localStorage:', err);
  }
}

export function getActiveSessionId(): string | null {
  try {
    return localStorage.getItem(ACTIVE_SESSION_ID_KEY);
  } catch {
    return null;
  }
}

export function setActiveSessionId(id: string | null): void {
  try {
    if (id) {
      localStorage.setItem(ACTIVE_SESSION_ID_KEY, id);
    } else {
      localStorage.removeItem(ACTIVE_SESSION_ID_KEY);
    }
  } catch (err) {
    console.error('Failed to set active session ID:', err);
  }
}

export function createNewSession(
  courseId: string | null = null,
  weekNumber: number | null = null,
  initialMessages: ChatMessage[] = []
): ChatSession {
  const newSession: ChatSession = {
    id: `session_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
    title: 'New Academic Inquiry',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    course_id: courseId,
    week_number: weekNumber,
    messages: initialMessages
  };

  const sessions = getStoredSessions();
  sessions.unshift(newSession);
  saveStoredSessions(sessions);
  setActiveSessionId(newSession.id);
  return newSession;
}

export function updateSession(
  sessionId: string,
  updates: Partial<Omit<ChatSession, 'id' | 'created_at'>>
): void {
  const sessions = getStoredSessions();
  const index = sessions.findIndex(s => s.id === sessionId);
  if (index !== -1) {
    sessions[index] = {
      ...sessions[index],
      ...updates,
      updated_at: new Date().toISOString()
    };
    saveStoredSessions(sessions);
  }
}

export function deleteStoredSession(sessionId: string): ChatSession[] {
  const sessions = getStoredSessions().filter(s => s.id !== sessionId);
  saveStoredSessions(sessions);
  if (getActiveSessionId() === sessionId) {
    setActiveSessionId(sessions[0]?.id || null);
  }
  return sessions;
}

export function clearAllSessions(): void {
  try {
    localStorage.removeItem(SESSIONS_STORAGE_KEY);
    localStorage.removeItem(ACTIVE_SESSION_ID_KEY);
  } catch (err) {
    console.error('Failed to clear sessions:', err);
  }
}
