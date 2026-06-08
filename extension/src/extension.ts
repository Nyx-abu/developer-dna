import * as vscode from 'vscode';
import { randomUUID } from 'crypto';

let outputChannel: vscode.OutputChannel;
let currentSessionId: string | undefined;

export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('Developer DNA');
    outputChannel.appendLine('Developer DNA is now active.');

    const apiUrl = process.env.VSCODE_DEV_API_URL || 'http://localhost:8000/api/v1';
    outputChannel.appendLine(`API URL configured to: ${apiUrl}`);

    const startSessionCmd = vscode.commands.registerCommand('developerDna.startSession', () => {
        currentSessionId = randomUUID();
        vscode.window.showInformationMessage(`Developer DNA: Session started (${currentSessionId})`);
        outputChannel.appendLine(`Session started: ${currentSessionId}`);
    });

    const stopSessionCmd = vscode.commands.registerCommand('developerDna.stopSession', () => {
        if (!currentSessionId) {
            vscode.window.showWarningMessage('Developer DNA: No active session to stop.');
            return;
        }
        vscode.window.showInformationMessage(`Developer DNA: Session stopped (${currentSessionId})`);
        outputChannel.appendLine(`Session stopped: ${currentSessionId}`);
        currentSessionId = undefined;
    });

    const showStatusCmd = vscode.commands.registerCommand('developerDna.showStatus', () => {
        const status = currentSessionId ? `Active (Session: ${currentSessionId})` : 'Inactive';
        vscode.window.showInformationMessage(`Developer DNA Status: ${status}`);
    });

    const sendTestEventCmd = vscode.commands.registerCommand('developerDna.sendTestEvent', async () => {
        vscode.window.showInformationMessage('Developer DNA: Sending test event...');
        try {
            const event = {
                event_type: 'test_event',
                timestamp: new Date().toISOString(),
                session_id: currentSessionId || randomUUID(),
            };
            const ingestUrl = `${apiUrl}/events/ingest/`;
            outputChannel.appendLine(`Sending test event to: ${ingestUrl}`);
            
            const response = await fetch(ingestUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ events: [event] })
            });

            if (response.ok) {
                vscode.window.showInformationMessage('Developer DNA: Test event sent successfully!');
                outputChannel.appendLine('Test event sent successfully.');
            } else {
                const errText = await response.text();
                vscode.window.showErrorMessage(`Developer DNA: Failed to send event. Status: ${response.status}`);
                outputChannel.appendLine(`Error response: ${errText}`);
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Developer DNA: Error sending event: ${error.message}`);
            outputChannel.appendLine(`Fetch Error: ${error.message}`);
        }
    });

    context.subscriptions.push(startSessionCmd, stopSessionCmd, showStatusCmd, sendTestEventCmd);
}

export function deactivate() {
    if (outputChannel) {
        outputChannel.appendLine('Developer DNA is deactivating.');
        outputChannel.dispose();
    }
}
