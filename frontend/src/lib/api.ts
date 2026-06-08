import type {
  ApiResponse,
  PaginatedResponse,
  CodingSession,
  CodeEvent,
  SkillSnapshot,
  AIInsight,
  WeeklyReport,
  ErrorEvent,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new ApiRequestError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorBody
        );
      }

      const data = (await response.json()) as ApiResponse<T>;
      return data;
    } catch (error) {
      if (error instanceof ApiRequestError) {
        throw error;
      }
      throw new ApiRequestError(
        error instanceof Error ? error.message : 'Unknown error',
        0,
        null
      );
    }
  }

  // ─── Sessions ──────────────────────────────────────────
  async getSessions(
    page = 1,
    pageSize = 20
  ): Promise<ApiResponse<PaginatedResponse<CodingSession>>> {
    return this.request<PaginatedResponse<CodingSession>>(
      `/sessions?page=${page}&pageSize=${pageSize}`
    );
  }

  async getSession(id: string): Promise<ApiResponse<CodingSession>> {
    return this.request<CodingSession>(`/sessions/${id}`);
  }

  // ─── Code Events ──────────────────────────────────────
  async getCodeEvents(
    sessionId: string,
    page = 1,
    pageSize = 50
  ): Promise<ApiResponse<PaginatedResponse<CodeEvent>>> {
    return this.request<PaginatedResponse<CodeEvent>>(
      `/sessions/${sessionId}/events?page=${page}&pageSize=${pageSize}`
    );
  }

  // ─── Errors ───────────────────────────────────────────
  async getErrors(
    page = 1,
    pageSize = 50
  ): Promise<ApiResponse<PaginatedResponse<ErrorEvent>>> {
    return this.request<PaginatedResponse<ErrorEvent>>(
      `/errors?page=${page}&pageSize=${pageSize}`
    );
  }

  // ─── Skills ───────────────────────────────────────────
  async getSkills(): Promise<ApiResponse<SkillSnapshot[]>> {
    return this.request<SkillSnapshot[]>('/skills');
  }

  async getSkillHistory(
    language: string
  ): Promise<ApiResponse<SkillSnapshot[]>> {
    return this.request<SkillSnapshot[]>(
      `/skills/history?language=${encodeURIComponent(language)}`
    );
  }

  // ─── AI Insights ─────────────────────────────────────
  async getInsights(): Promise<ApiResponse<AIInsight[]>> {
    return this.request<AIInsight[]>('/insights');
  }

  async dismissInsight(id: string): Promise<ApiResponse<null>> {
    return this.request<null>(`/insights/${id}/dismiss`, {
      method: 'POST',
    });
  }

  // ─── Reports ─────────────────────────────────────────
  async getReports(
    page = 1,
    pageSize = 10
  ): Promise<ApiResponse<PaginatedResponse<WeeklyReport>>> {
    return this.request<PaginatedResponse<WeeklyReport>>(
      `/reports?page=${page}&pageSize=${pageSize}`
    );
  }

  async getReport(id: string): Promise<ApiResponse<WeeklyReport>> {
    return this.request<WeeklyReport>(`/reports/${id}`);
  }

  // ─── Analysis ────────────────────────────────────────
  async triggerAnalysis(): Promise<ApiResponse<{ jobId: string; status: string }>> {
    return this.request<{ jobId: string; status: string }>('/analysis/trigger', {
      method: 'POST',
    });
  }
}

export class ApiRequestError extends Error {
  public statusCode: number;
  public responseBody: string | null;

  constructor(message: string, statusCode: number, responseBody: string | null) {
    super(message);
    this.name = 'ApiRequestError';
    this.statusCode = statusCode;
    this.responseBody = responseBody;
  }
}

export const apiClient = new ApiClient(BASE_URL);
