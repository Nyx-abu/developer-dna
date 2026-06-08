/**
 * Developer DNA — Shared type definitions
 */

/** Base event common to all telemetry types */
export interface BaseEvent {
  readonly event_id: string;
  readonly event_type: string;
  readonly timestamp: string;
  readonly user_id?: string;
}

/** File save / file open events */
export interface CodeEvent extends BaseEvent {
  readonly event_type: "file_save" | "file_open";
  readonly file_path: string;
  readonly language: string;
  readonly line_count: number;
  readonly char_count: number;
}

/** Git repository state changes */
export interface GitEvent extends BaseEvent {
  readonly event_type: "git_commit" | "git_branch_change" | "git_state_change";
  readonly branch: string;
  readonly commit?: string;
  readonly files_changed?: number;
  readonly ahead?: number;
  readonly behind?: number;
  readonly repo_path: string;
}

/** Terminal lifecycle & shell execution events */
export interface TerminalEvent extends BaseEvent {
  readonly event_type: "terminal_open" | "terminal_close" | "terminal_command";
  readonly terminal_name: string;
  readonly command?: string;
  readonly exit_code?: number;
  readonly duration_ms?: number;
  readonly exit_status?: string;
}

/** Diagnostics (errors / warnings) per file */
export interface ErrorEvent extends BaseEvent {
  readonly event_type: "diagnostics_change";
  readonly file_path: string;
  readonly error_count: number;
  readonly warning_count: number;
  readonly delta: number;
  readonly errors: ReadonlyArray<DiagnosticEntry>;
}

/** Single diagnostic entry */
export interface DiagnosticEntry {
  readonly message: string;
  readonly line: number;
  readonly source: string;
}

/** Session start / end events */
export interface SessionEvent extends BaseEvent {
  readonly event_type: "session_start" | "session_end";
  readonly session_type: "start" | "end";
  readonly duration_ms?: number;
}

/** Union of all event types the extension can emit */
export type DevDNAEvent =
  | CodeEvent
  | GitEvent
  | TerminalEvent
  | ErrorEvent
  | SessionEvent;

/** Extension configuration */
export interface DevDNAConfig {
  readonly apiUrl: string;
  readonly bufferSize: number;
  readonly flushIntervalMs: number;
}

/** Callback signature used by watchers to push events */
export type EventCallback = (event: DevDNAEvent) => void;
