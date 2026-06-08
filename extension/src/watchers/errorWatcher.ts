import * as vscode from "vscode";
import * as crypto from "crypto";
import type { ErrorEvent, DiagnosticEntry, EventCallback } from "../types";

/**
 * Watches diagnostic changes (errors/warnings) with 1-second debouncing.
 * Tracks per-file counts to compute deltas.
 */
export class ErrorWatcher implements vscode.Disposable {
  private readonly disposables: vscode.Disposable[] = [];
  private readonly previousCounts = new Map<string, { errors: number; warnings: number }>();
  private debounceTimer: ReturnType<typeof setTimeout> | undefined;

  private static readonly DEBOUNCE_MS = 1000;

  constructor(private readonly onEvent: EventCallback) {
    try {
      this.disposables.push(
        vscode.languages.onDidChangeDiagnostics((e) => {
          this.debounceDiagnostics(e.uris);
        })
      );
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[DevDNA] ErrorWatcher init error: ${message}`);
    }
  }

  private debounceDiagnostics(uris: readonly vscode.Uri[]): void {
    // Collect all URIs that changed during the debounce window
    if (this.debounceTimer !== undefined) {
      clearTimeout(this.debounceTimer);
    }

    // Store a copy of the URIs for processing after debounce
    const uriStrings = new Set(uris.map((u) => u.toString()));

    this.debounceTimer = setTimeout(() => {
      this.debounceTimer = undefined;
      this.processDiagnostics(uriStrings);
    }, ErrorWatcher.DEBOUNCE_MS);
  }

  private processDiagnostics(uriStrings: Set<string>): void {
    try {
      for (const uriString of uriStrings) {
        const uri = vscode.Uri.parse(uriString);

        // Skip non-file schemes
        if (uri.scheme !== "file") {
          continue;
        }

        const diagnostics = vscode.languages.getDiagnostics(uri);

        const errors = diagnostics.filter(
          (d) => d.severity === vscode.DiagnosticSeverity.Error
        );
        const warnings = diagnostics.filter(
          (d) => d.severity === vscode.DiagnosticSeverity.Warning
        );

        const errorCount = errors.length;
        const warningCount = warnings.length;
        const totalCount = errorCount + warningCount;

        const filePath = vscode.workspace.asRelativePath(uri, false);
        const previous = this.previousCounts.get(filePath);
        const previousTotal = previous
          ? previous.errors + previous.warnings
          : 0;
        const delta = totalCount - previousTotal;

        // Only emit if there's an actual change
        if (delta === 0 && previous !== undefined) {
          continue;
        }

        // Build diagnostic entries (cap at 20 to avoid bloated payloads)
        const entries: DiagnosticEntry[] = [
          ...errors,
          ...warnings,
        ]
          .slice(0, 20)
          .map((d) => ({
            message: d.message,
            line: d.range.start.line + 1, // Convert 0-indexed to 1-indexed
            source: d.source ?? "unknown",
          }));

        const event: ErrorEvent = {
          event_id: crypto.randomUUID(),
          event_type: "diagnostics_change",
          timestamp: new Date().toISOString(),
          file_path: filePath,
          error_count: errorCount,
          warning_count: warningCount,
          delta,
          errors: entries,
        };

        this.onEvent(event);

        // Update snapshot
        this.previousCounts.set(filePath, {
          errors: errorCount,
          warnings: warningCount,
        });
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[DevDNA] ErrorWatcher processing error: ${message}`);
    }
  }

  dispose(): void {
    if (this.debounceTimer !== undefined) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = undefined;
    }
    for (const d of this.disposables) {
      d.dispose();
    }
    this.disposables.length = 0;
    this.previousCounts.clear();
  }
}
