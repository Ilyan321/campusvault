import { Course, AnalysisResult, NoteSource, WeekNoteInfo } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://campusvault-backend.onrender.com');

export const DEFAULT_COURSES: Course[] = [
  {
    course_id: "CSE-212",
    course_name: "Data Structures & Algorithms",
    department: "Computer Systems Engineering",
    syllabus_timeline: [
      { week: 1, core_topic: "Pointers & Dynamic Memory", grounding_keywords: ["malloc", "pointers", "arrays"] },
      { week: 3, core_topic: "Linked Lists (Singly & Doubly)", grounding_keywords: ["node", "head", "tail", "linked list"] },
      { week: 4, core_topic: "Stack Data Structure & Expression Parsing", grounding_keywords: ["stack", "push", "pop", "lifo"] },
      { week: 5, core_topic: "Queue Data Structure & Circular Implementations", grounding_keywords: ["queue", "enqueue", "dequeue", "circular queue", "modulo"] },
      { week: 8, core_topic: "Binary Search Trees & Traversals", grounding_keywords: ["bst", "inorder", "preorder", "postorder"] },
      { week: 12, core_topic: "Graph Traversals and Shortest Path", grounding_keywords: ["graph", "bfs", "dfs", "dijkstra"] },
      { week: 14, core_topic: "Sorting, Searching & Time Complexity", grounding_keywords: ["quicksort", "binary search", "big o"] }
    ]
  },
  {
    course_id: "CSE-305",
    course_name: "Data & Computer Networks",
    department: "Computer Systems Engineering",
    syllabus_timeline: [
      { week: 2, core_topic: "OSI 7-Layer Architecture & TCP/IP", grounding_keywords: ["osi", "transport", "network", "datalink"] },
      { week: 5, core_topic: "IP Addressing, CIDR & Subnetting", grounding_keywords: ["ipv4", "cidr", "subnet mask", "usable hosts"] },
      { week: 9, core_topic: "Routing Protocols (OSPF & RIP)", grounding_keywords: ["routing", "ospf", "rip", "distance vector"] },
      { week: 11, core_topic: "Transport Layer: TCP vs UDP Handshake", grounding_keywords: ["tcp", "udp", "three way handshake", "syn ack"] },
      { week: 14, core_topic: "Application Layer Protocols (HTTP, DNS, DHCP)", grounding_keywords: ["http", "https", "dns", "dhcp"] }
    ]
  },
  {
    course_id: "CSE-310",
    course_name: "Operating Systems",
    department: "Computer Systems Engineering",
    syllabus_timeline: [
      { week: 3, core_topic: "CPU Scheduling (FCFS, SJF, Round Robin)", grounding_keywords: ["scheduling", "round robin", "fcfs", "sjf", "gantt chart"] },
      { week: 6, core_topic: "Process Synchronization, Mutex & Semaphores", grounding_keywords: ["synchronization", "mutex", "semaphore", "critical section", "race condition"] },
      { week: 8, core_topic: "Deadlocks & Banker's Safety Algorithm", grounding_keywords: ["deadlock", "banker", "resource allocation", "safe state"] },
      { week: 12, core_topic: "Virtual Memory, Paging & Page Replacement", grounding_keywords: ["paging", "virtual memory", "tlb", "lru", "page fault"] }
    ]
  },
  {
    course_id: "CSE-315",
    course_name: "Database Systems & SQL",
    department: "Computer Systems Engineering",
    syllabus_timeline: [
      { week: 3, core_topic: "Relational Algebra & Advanced SQL Queries", grounding_keywords: ["relational algebra", "sql", "join", "group by", "having"] },
      { week: 6, core_topic: "Database Normalization (1NF, 2NF, 3NF, BCNF)", grounding_keywords: ["normalization", "1nf", "2nf", "3nf", "bcnf", "dependency"] },
      { week: 10, core_topic: "Transactions, ACID & Concurrency Control (2PL)", grounding_keywords: ["transaction", "acid", "2pl", "locking", "wal", "isolation"] },
      { week: 13, core_topic: "Database Indexing & B+ Trees vs Hash Index", grounding_keywords: ["indexing", "b+ tree", "hash index", "clustered"] }
    ]
  },
  {
    course_id: "CSE-204",
    course_name: "Digital Logic & Computer Architecture",
    department: "Computer Systems Engineering",
    syllabus_timeline: [
      { week: 2, core_topic: "Boolean Algebra & Karnaugh Maps (K-Maps)", grounding_keywords: ["boolean algebra", "k map", "sop", "pos", "dont care"] },
      { week: 5, core_topic: "Sequential Circuits & Flip-Flops (SR, JK, D, T)", grounding_keywords: ["flip flop", "jk", "sr latch", "d flip flop", "race around"] },
      { week: 9, core_topic: "CPU Pipelining & Pipeline Hazards", grounding_keywords: ["pipelining", "hazard", "data forwarding", "stall", "cpi"] },
      { week: 12, core_topic: "Cache Memory Mapping (Direct, Associative)", grounding_keywords: ["cache memory", "direct mapped", "associative", "hit", "miss"] }
    ]
  },
  {
    course_id: "MATH-201",
    course_name: "Linear Algebra & Applied Mathematics",
    department: "Basic Sciences & Humanities",
    syllabus_timeline: [
      { week: 2, core_topic: "Matrices, Gaussian Elimination & Linear Systems", grounding_keywords: ["matrix", "gaussian elimination", "row echelon", "rank", "determinant"] },
      { week: 6, core_topic: "Vector Spaces, Linear Independence & Basis", grounding_keywords: ["vector space", "linear independence", "basis", "dimension", "null space"] },
      { week: 10, core_topic: "Eigenvalues, Eigenvectors & Diagonalization", grounding_keywords: ["eigenvalue", "eigenvector", "characteristic equation", "diagonalization"] }
    ]
  }
];

/**
 * Exponential backoff retry utility for network robustness against Render free-tier cold starts and transient reconnects.
 */
async function fetchWithRetry(url: string, options: RequestInit, retries = 3, delayMs = 1200): Promise<Response> {
  let lastError: any = null;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, options);
      if (response.ok || response.status < 500) {
        return response;
      }
      throw new Error(`Server returned HTTP ${response.status}`);
    } catch (err: any) {
      lastError = err;
      if (attempt < retries) {
        const backoff = delayMs * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, backoff));
      }
    }
  }
  throw lastError || new Error(`Network request failed after ${retries} attempts.`);
}

export async function fetchSyllabus(): Promise<Course[]> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4500);
    const res = await fetch(`${API_BASE_URL}/api/syllabus`, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return Array.isArray(data) && data.length > 0 ? data : DEFAULT_COURSES;
  } catch (err) {
    return DEFAULT_COURSES;
  }
}

export async function analyzeFile(file: File, courseId?: string): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);
  if (courseId) {
    formData.append('course_id', courseId);
  }

  const res = await fetchWithRetry(`${API_BASE_URL}/api/ingest/analyze`, {
    method: 'POST',
    body: formData
  }, 3, 1000);

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to analyze note' }));
    throw new Error(errorData.detail || 'Analysis request failed');
  }

  return await res.json();
}

export async function confirmIngest(payload: {
  file_name: string;
  file_url?: string;
  course_id?: string;
  week_number?: number | null;
  topic?: string;
  content: string;
}): Promise<{ success: boolean; message: string; inserted_count: number }> {
  const res = await fetchWithRetry(`${API_BASE_URL}/api/ingest/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }, 3, 1200);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to confirm ingestion' }));
    throw new Error(err.detail || 'Ingestion confirmation failed');
  }

  return await res.json();
}

export interface QueryMeta {
  auto_detected_week?: number;
  detected_topic?: string;
  language_mode?: string;
  sources?: NoteSource[];
  expanded_queries?: string[];
  relevance_grade?: string;
  latency_seconds?: number;
}

export async function queryRAG(payload: {
  query: string;
  week_number?: number | null;
  course_id?: string | null;
  history?: Array<{ role: string; content: string }>;
}): Promise<{
  answer: string;
  week_number?: number | null;
  course_id?: string | null;
  sources: NoteSource[];
  agentic_meta?: QueryMeta;
}> {
  const res = await fetchWithRetry(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }, 2, 800);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to query RAG' }));
    throw new Error(err.detail || 'Query failed');
  }

  return await res.json();
}

/**
 * Real-time SSE Token Streaming query with live token-by-token rendering.
 */
export async function streamQueryRAG(
  payload: {
    query: string;
    week_number?: number | null;
    course_id?: string | null;
    history?: Array<{ role: string; content: string }>;
  },
  onToken: (token: string) => void,
  onMeta?: (meta: QueryMeta) => void,
  onError?: (err: Error) => void
): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/api/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok || !res.body) {
    throw new Error(`Streaming failed with status ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let fullText = '';
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith('data: ')) continue;
      const dataStr = trimmed.slice(6);
      try {
        const parsed = JSON.parse(dataStr);
        if (parsed.type === 'token') {
          fullText += parsed.content;
          onToken(parsed.content);
        } else if (parsed.type === 'meta' && onMeta) {
          onMeta(parsed);
        } else if (parsed.type === 'error' && onError) {
          onError(new Error(parsed.content));
        }
      } catch (e) {
        // Skip malformed SSE chunks
      }
    }
  }

  return fullText;
}

export async function triggerSeed(): Promise<{ success: boolean; message: string; seeded_topics: string[]; total_chunks: number }> {
  const res = await fetch(`${API_BASE_URL}/api/seed`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to seed notes database');
  return await res.json();
}

export async function fetchWeekNotes(courseId: string, weekNumber: number): Promise<WeekNoteInfo[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/notes?course_id=${encodeURIComponent(courseId)}&week_number=${weekNumber}`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error('Error fetching week notes:', err);
    return [];
  }
}

export interface FullNoteResponse {
  file_name: string;
  topic?: string;
  course_id?: string;
  week_number?: number;
  content: string;
  is_seed?: boolean;
}

export async function fetchFullNoteContent(fileName: string): Promise<FullNoteResponse | null> {
  try {
    const res = await fetchWithRetry(`${API_BASE_URL}/api/notes/content?file_name=${encodeURIComponent(fileName)}`, {
      method: 'GET'
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error('Error fetching full note content:', err);
    return null;
  }
}

export function getRawNoteUrl(fileName: string): string {
  return `${API_BASE_URL}/api/notes/raw/${encodeURIComponent(fileName)}`;
}

