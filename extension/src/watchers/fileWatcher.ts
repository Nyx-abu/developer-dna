import * as vscode from "vscode";
import * as crypto from "crypto";
import type { CodeEvent, EventCallback } from "../types";

/**
 * Watches file saves and active editor changes, emitting CodeEvents.
 */
export class FileWatcher implements vscode.Disposable {
  private readonly disposables: vscode.Disposable[] = [];

  constructor(private readonly onEvent: EventCallback) {
    try {
      this.disposables.push(
        vscode.workspace.onDidSaveTextDocument((doc) => {
          this.handleDocumentEvent(doc, "file_save");
        })
      );

      this.disposables.push(
        vscode.window.onDidChangeActiveTextEditor((editor) => {
          if (editor) {
            this.handleDocumentEvent(editor.document, "file_open");
          }
        })
      );

      // Emit for the currently active editor at startup
      const activeEditor = vscode.window.activeTextEditor;
      if (activeEditor) {
        this.handleDocumentEvent(activeEditor.document, "file_open");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[DevDNA] FileWatcher init error: ${message}`);
    }
  }

  private handleDocumentEvent(
    doc: vscode.TextDocument,
    eventType: "file_save" | "file_open"
  ): void {
    try {
      // Skip untitled or non-file schemes
      if (doc.uri.scheme !== "file") {
        return;
      }

      const workspaceFolder = vscode.workspace.getWorkspaceFolder(doc.uri);
      const filePath = workspaceFolder
        ? vscode.workspace.asRelativePath(doc.uri, false)
        : doc.uri.fsPath;

      const text = doc.getText();

      const event: CodeEvent = {
        event_id: crypto.randomUUID(),
        event_type: eventType,
        timestamp: new Date().toISOString(),
        file_path: filePath,
        language: doc.languageId,
        line_count: doc.lineCount,
        char_count: text.length,
      };

      this.onEvent(event);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[DevDNA] FileWatcher event error: ${message}`);
    }
  }

  dispose(): void {
    for (const d of this.disposables) {
      d.dispose();
    }
    this.disposables.length = 0;
  }
}
