import * as vscode from 'vscode';
import { randomUUID } from 'crypto';
import WebSocket from 'ws';

let outputChannel: vscode.OutputChannel;
let currentSessionId: string | undefined;
let ws: WebSocket | undefined;

// Micro-batching setup
let eventBuffer: any[] = [];
let batchTimeout: NodeJS.Timeout | null = null;

function flushEvents() {
    if (eventBuffer.length === 0) return;
    
    if (ws && ws.readyState === WebSocket.OPEN) {
        // Send events over WebSocket
        ws.send(JSON.stringify({ events: eventBuffer }));
        eventBuffer = []; // Clear the buffer
    } else {
        // WebSocket not ready, wait for reconnect or next flush
        outputChannel.appendLine('WebSocket not connected. Holding events.');
    }
}

function queueEvent(event: any) {
    if (!currentSessionId) return; // Only track if session is active
    
    event.session_id = currentSessionId;
    event.timestamp = new Date().toISOString();
    eventBuffer.push(event);

    const config = vscode.workspace.getConfiguration('developerDna');
    const bufferSize = config.get<number>('bufferSize') || 50;

    // Flush immediately if buffer is full
    if (eventBuffer.length >= bufferSize) {
        if (batchTimeout) {
            clearTimeout(batchTimeout);
            batchTimeout = null;
        }
        flushEvents();
    } else if (!batchTimeout) {
        // Use a smaller debounce interval for micro-batching
        const flushIntervalMs = config.get<number>('flushIntervalMs') || 5000;
        batchTimeout = setTimeout(() => {
            flushEvents();
            batchTimeout = null;
        }, flushIntervalMs);
    }
}

function connectWebSocket(apiUrl: string, apiKey: string) {
    const wsUrl = apiUrl.replace(/^http/, 'ws').replace(/\/ingest\/?$/, '/ws/');
    
    outputChannel.appendLine(`Connecting to WebSocket: ${wsUrl}`);
    ws = new WebSocket(wsUrl, {
        headers: {
            'Authorization': `Bearer ${apiKey}`
        }
    });

    ws.on('open', () => {
        outputChannel.appendLine('WebSocket connection established.');
        vscode.window.showInformationMessage('Developer DNA: Connected to telemetry stream.');
        flushEvents(); // Flush any pending events
    });

    ws.on('error', (err) => {
        outputChannel.appendLine(`WebSocket error: ${err.message}`);
    });

    ws.on('close', () => {
        outputChannel.appendLine('WebSocket connection closed.');
    });
}

export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('Developer DNA');
    outputChannel.appendLine('Developer DNA is now active.');

    const config = vscode.workspace.getConfiguration('developerDna');
    const apiUrl = process.env.VSCODE_DEV_API_URL || config.get<string>('apiUrl') || 'http://localhost:8000/api/v1/events/ingest/';
    const apiKey = config.get<string>('apiKey') || '';

    const startSessionCmd = vscode.commands.registerCommand('developerDna.startSession', () => {
        currentSessionId = randomUUID();
        vscode.window.showInformationMessage(`Developer DNA: Session started (${currentSessionId})`);
        outputChannel.appendLine(`Session started: ${currentSessionId}`);
        connectWebSocket(apiUrl, apiKey);
    });

    const stopSessionCmd = vscode.commands.registerCommand('developerDna.stopSession', () => {
        if (!currentSessionId) {
            vscode.window.showWarningMessage('Developer DNA: No active session to stop.');
            return;
        }
        vscode.window.showInformationMessage(`Developer DNA: Session stopped (${currentSessionId})`);
        outputChannel.appendLine(`Session stopped: ${currentSessionId}`);
        currentSessionId = undefined;
        
        if (batchTimeout) {
            clearTimeout(batchTimeout);
            batchTimeout = null;
        }
        // Flush one last time if possible
        if (eventBuffer.length > 0 && ws && ws.readyState === WebSocket.OPEN) {
            flushEvents();
        }
        if (ws) {
            ws.close();
            ws = undefined;
        }
    });

    const showStatusCmd = vscode.commands.registerCommand('developerDna.showStatus', () => {
        const wsStatus = ws && ws.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected';
        const status = currentSessionId ? `Active (Session: ${currentSessionId}) [${wsStatus}]` : 'Inactive';
        vscode.window.showInformationMessage(`Developer DNA Status: ${status}`);
    });

    const sendTestEventCmd = vscode.commands.registerCommand('developerDna.sendTestEvent', () => {
        vscode.window.showInformationMessage('Developer DNA: Queuing test event...');
        queueEvent({
            event_type: 'test_event'
        });
    });

    // Listen for text document changes to track keystrokes
    const textDocumentChangeListener = vscode.workspace.onDidChangeTextDocument(event => {
        if (currentSessionId && event.contentChanges.length > 0) {
            queueEvent({
                event_type: 'keystroke',
                document: event.document.uri.toString(),
                changes: event.contentChanges.map(change => ({
                    textLength: change.text.length,
                    rangeLength: change.rangeLength
                }))
            });
        }
    });

    context.subscriptions.push(startSessionCmd, stopSessionCmd, showStatusCmd, sendTestEventCmd, textDocumentChangeListener);
}

export function deactivate() {
    if (ws) {
        ws.close();
    }
    if (outputChannel) {
        outputChannel.appendLine('Developer DNA is deactivating.');
        outputChannel.dispose();
    }
}
