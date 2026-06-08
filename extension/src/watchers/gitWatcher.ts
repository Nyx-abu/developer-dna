import * as vscode from "vscode";
import * as crypto from "crypto";
import type { GitEvent, EventCallback } from "../types";

/**
 * Minimal type declarations for the VS Code built-in Git extension API.
 * We only declare what we actually use to avoid coupling to the full API.
 */
interface GitExtensionAPI {
  readonly state: "initialized" | "uninitialized";
  readonly repositories: GitRepository[];
  onDidOpenRepository: vscode.Event<GitRepository>;
}

interface GitRepository {
  readonly state: GitRepositoryState;
  readonly rootUri: vscode.Uri;
  onDidChangeRepository: vscode.Event<void>;
}

interface GitRepositoryState {
  readonly HEAD: GitBranchRef | undefined;
  readonly remotes: ReadonlyArray<GitRemote>;
}

interface GitBranchRef {
  readonly name?: string;
  readonly commit?: string;
  readonly ahead?: number;
  readonly behind?: number;
}

interface GitRemote {
  readonly name: string;
}

/**
 * Watches Git repository state changes and emits GitEvents.
 */
export class GitWatcher implements vscode.Disposable {
  private readonly disposables: vscode.Disposable[] = [];
  private lastBranches = new Map<string, string>();
  private lastCommits = new Map<string, string>();

  constructor(private readonly onEvent: EventCallback) {
    try {
      this.initGitExtension();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[DevDNA] GitWatcher init error: ${message}`);
    }
  }

  private initGitExtension(): void {
    const gitExtension = vscode.extensions.getExtension<{ getAPI(version: number): GitExtensionAPI }>(
      "vscode.git"
    );

    if (!gitExtension) {
      console.warn("[DevDNA] Git extension not found — GitWatcher disabled");
      return;
    }

    if (gitExtension.isActive) {
      this.setupGitAPI(gitExtension.exports.getAPI(1));
    } else {
      gitExtension.activate().then(
        (exports) => {
          this.setupGitAPI(exports.getAPI(1));
        },
        (err: unknown) => {
          const message = err instanceof Error ? err.message : String(err);
          console.error(`[DevDNA] Git extension activation failed: ${message}`);
        }
      );
    }
  }

  private setupGitAPI(api: GitExtensionAPI): void {
    if (api.state !== "initialized") {
      console.warn("[DevDNA] Git API not initialized yet");
      return;
    }

    for (const repo of api.repositories) {
      this.watchRepository(repo);
    }

    this.disposables.push(
      api.onDidOpenRepository((repo) => {
        this.watchRepository(repo);
      })
    );
  }

  private watchRepository(repo: GitRepository): void {
    const repoPath = repo.rootUri.fsPath;

    // Snapshot initial state
    const head = repo.state.HEAD;
    if (head?.name) {
      this.lastBranches.set(repoPath, head.name);
    }
    if (head?.commit) {
      this.lastCommits.set(repoPath, head.commit);
    }

    this.disposables.push(
      repo.onDidChangeRepository(() => {
        this.handleRepoChange(repo);
      })
    );
  }

  private handleRepoChange(repo: GitRepository): void {
    try {
      const repoPath = repo.rootUri.fsPath;
      const head = repo.state.HEAD;
      const currentBranch = head?.name ?? "HEAD";
      const currentCommit = head?.commit;

      const previousBranch = this.lastBranches.get(repoPath);
      const previousCommit = this.lastCommits.get(repoPath);

      // Detect branch change
      if (previousBranch && currentBranch !== previousBranch) {
        const event: GitEvent = {
          event_id: crypto.randomUUID(),
          event_type: "git_branch_change",
          timestamp: new Date().toISOString(),
          branch: currentBranch,
          repo_path: repoPath,
          ahead: head?.ahead,
          behind: head?.behind,
        };
        this.onEvent(event);
      }

      // Detect new commit
      if (currentCommit && currentCommit !== previousCommit) {
        const event: GitEvent = {
          event_id: crypto.randomUUID(),
          event_type: "git_commit",
          timestamp: new Date().toISOString(),
          branch: currentBranch,
          commit: currentCommit,
          repo_path: repoPath,
          ahead: head?.ahead,
          behind: head?.behind,
        };
        this.onEvent(event);
      }

      // Emit general state change if nothing specific detected
      if (
        currentBranch === previousBranch &&
        currentCommit === previousCommit
      ) {
        const event: GitEvent = {
          event_id: crypto.randomUUID(),
          event_type: "git_state_change",
          timestamp: new Date().toISOString(),
          branch: currentBranch,
          commit: currentCommit,
          repo_path: repoPath,
          ahead: head?.ahead,
          behind: head?.behind,
        };
        this.onEvent(event);
      }

      // Update snapshots
      this.lastBranches.set(repoPath, currentBranch);
      if (currentCommit) {
        this.lastCommits.set(repoPath, currentCommit);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[DevDNA] GitWatcher change error: ${message}`);
    }
  }

  dispose(): void {
    for (const d of this.disposables) {
      d.dispose();
    }
    this.disposables.length = 0;
    this.lastBranches.clear();
    this.lastCommits.clear();
  }
}
