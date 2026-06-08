// ─── User ───────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  displayName: string;
  avatarUrl: string | null;
  createdAt: string;
  settings: UserSettings;
}

export interface UserSettings {
  theme: 'dark' | 'light';
  notifications: boolean;
  weeklyReports: boolean;
  timezone: string;
}

// ─── Coding Session ─────────────────────────────────────
export interface CodingSession {
  id: string;
  userId: string;
  startTime: string;
  endTime: string | null;
  durationMinutes: number;
  languages: string[];
  editor: string;
  projectName: string;
  eventsCount: number;
  isActive: boolean;
}

// ─── Events ─────────────────────────────────────────────
export interface CodeEvent {
  id: string;
  sessionId: string;
  timestamp: string;
  eventType: 'keystroke' | 'paste' | 'autocomplete' | 'refactor' | 'save';
  language: string;
  filePath: string;
  linesChanged: number;
  charactersDelta: number;
}

export interface GitEvent {
  id: string;
  sessionId: string;
  timestamp: string;
  eventType: 'commit' | 'push' | 'pull' | 'merge' | 'branch' | 'rebase';
  repository: string;
  branch: string;
  message: string;
  filesChanged: number;
  additions: number;
  deletions: number;
}

export interface TerminalEvent {
  id: string;
  sessionId: string;
  timestamp: string;
  command: string;
  exitCode: number;
  durationMs: number;
  shell: string;
}

export interface ErrorEvent {
  id: string;
  sessionId: string;
  timestamp: string;
  errorType: 'syntax' | 'runtime' | 'type' | 'lint' | 'build' | 'test';
  language: string;
  message: string;
  filePath: string;
  lineNumber: number;
  resolved: boolean;
  resolutionTimeMs: number | null;
}

// ─── Skills ─────────────────────────────────────────────
export interface SkillSnapshot {
  id: string;
  userId: string;
  capturedAt: string;
  language: string;
  proficiencyScore: number; // 0-100
  linesWritten: number;
  hoursSpent: number;
  growthRate: number; // percentage change
  frameworks: FrameworkProficiency[];
}

export interface FrameworkProficiency {
  name: string;
  language: string;
  proficiency: number; // 0-100
  lastUsed: string;
}

// ─── AI Insights ────────────────────────────────────────
export interface AIInsight {
  id: string;
  userId: string;
  generatedAt: string;
  category: 'productivity' | 'quality' | 'learning' | 'health' | 'career';
  severity: 'info' | 'warning' | 'critical';
  title: string;
  body: string;
  actionable: boolean;
  actionLabel: string | null;
  dismissed: boolean;
}

// ─── Weekly Report ──────────────────────────────────────
export interface WeeklyReport {
  id: string;
  userId: string;
  weekStart: string;
  weekEnd: string;
  generatedAt: string;
  summary: string;
  totalHours: number;
  totalCommits: number;
  totalLinesWritten: number;
  topLanguages: LanguageStat[];
  highlights: ReportHighlight[];
  badges: ReportBadge[];
  productivityScore: number; // 0-100
  comparedToLastWeek: number; // percentage change
}

export interface LanguageStat {
  language: string;
  hours: number;
  linesWritten: number;
  percentage: number;
}

export interface ReportHighlight {
  title: string;
  description: string;
  metric: string;
  icon: string;
}

export interface ReportBadge {
  name: string;
  description: string;
  icon: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

// ─── Coach ──────────────────────────────────────────────
export interface CoachRecommendation {
  id: string;
  category: 'skill' | 'habit' | 'career' | 'health';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  estimatedImpact: string;
  resources: CoachResource[];
}

export interface CoachResource {
  title: string;
  url: string;
  type: 'article' | 'video' | 'course' | 'documentation';
}

export interface SkillGap {
  skill: string;
  currentLevel: number;
  targetLevel: number;
  gap: number;
  recommendation: string;
}

export interface CareerPath {
  title: string;
  description: string;
  matchScore: number;
  requiredSkills: string[];
  currentSkills: string[];
  timeline: string;
}

export interface CoachMessage {
  id: string;
  role: 'user' | 'coach';
  content: string;
  timestamp: string;
}

// ─── API Response Wrappers ──────────────────────────────
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  code: string;
  message: string;
  details: string | null;
}

// ─── Chart Data Types ───────────────────────────────────
export interface ActivityDay {
  date: string;
  hours: number;
  level: 0 | 1 | 2 | 3 | 4;
}

export interface SkillRadarPoint {
  skill: string;
  proficiency: number;
  fullMark: number;
}

export interface ProductivityDataPoint {
  date: string;
  hours: number;
  commits: number;
}

export interface ErrorFrequency {
  type: string;
  count: number;
  avgResolutionTime: number;
}

export interface HourlyActivity {
  hour: string;
  sessions: number;
  events: number;
}
