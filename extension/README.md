# Developer DNA - VS Code Extension

Developer DNA telemetry extension. It tracks your coding events (keystrokes, file saves, git commits, terminal errors) and sends them to your local Developer DNA backend.

## Testing Locally

1. Open the `extension/` directory in VS Code.
2. Ensure you have run `npm install` inside the `extension/` directory.
3. Press `F5` to open a new VS Code window (Extension Development Host).
4. In the new window, open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).
5. Run the command **"Developer DNA: Start Session"** to initialize a tracking session.
6. Run the command **"Developer DNA: Send Test Event"** to manually fire an event to the backend API (`http://localhost:8000/api/v1/events/ingest/`).
7. Open the **Output** panel (`Ctrl+Shift+U` / `Cmd+Shift+U`) and select **Developer DNA** from the dropdown to view telemetry logs and verify events were sent successfully.

## Configuration

- `developerDna.apiUrl`: Defaults to `http://localhost:8000/api/v1/events/ingest/`. Change this if your backend is hosted elsewhere.
- `developerDna.bufferSize`: Number of events to batch before sending (default: 50).
- `developerDna.flushIntervalMs`: Time between flushes in ms (default: 30000).
