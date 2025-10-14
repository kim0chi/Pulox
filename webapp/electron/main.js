/**
 * Electron Main Process
 * Manages application lifecycle, windows, and Python backend
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');

// Configuration
const API_HOST = '127.0.0.1';
const API_PORT = 8000;
const API_URL = `http://${API_HOST}:${API_PORT}`;

let mainWindow;
let pythonProcess;

/**
 * Start Python FastAPI backend server
 */
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    console.log('Starting Python backend...');

    // Determine Python command (python or python3)
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    // Path to API script
    const apiScript = path.join(__dirname, '..', 'api.py');

    // Spawn Python process
    pythonProcess = spawn(pythonCmd, [apiScript], {
      cwd: path.join(__dirname, '..'),
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    pythonProcess.stdout.on('data', (data) => {
      console.log(`[Python] ${data.toString()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`[Python Error] ${data.toString()}`);
    });

    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python backend:', error);
      reject(error);
    });

    pythonProcess.on('close', (code) => {
      console.log(`Python backend exited with code ${code}`);
      if (code !== 0 && code !== null) {
        dialog.showErrorBox(
          'Backend Error',
          `Python backend crashed with code ${code}. Please check the console.`
        );
      }
    });

    // Wait for server to be ready
    let attempts = 0;
    const maxAttempts = 30;

    const checkServer = setInterval(async () => {
      attempts++;
      try {
        const response = await axios.get(`${API_URL}/health`);
        if (response.status === 200) {
          console.log('Python backend is ready!');
          clearInterval(checkServer);
          resolve();
        }
      } catch (error) {
        if (attempts >= maxAttempts) {
          clearInterval(checkServer);
          reject(new Error('Backend failed to start within timeout'));
        }
      }
    }, 1000);
  });
}

/**
 * Stop Python backend server
 */
function stopPythonBackend() {
  if (pythonProcess) {
    console.log('Stopping Python backend...');
    pythonProcess.kill('SIGTERM');
    pythonProcess = null;
  }
}

/**
 * Create main application window
 */
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    // icon: path.join(__dirname, 'assets', 'icon.png'), // Optional - uncomment when icon is added
    show: false // Don't show until ready
  });

  // Load main HTML
  const htmlPath = path.join(__dirname, 'renderer', 'index.html');
  console.log('Loading HTML from:', htmlPath);

  mainWindow.loadFile(htmlPath).catch(err => {
    console.error('Failed to load HTML:', err);
    dialog.showErrorBox('Load Error', `Failed to load app: ${err.message}`);
  });

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    console.log('Window ready, showing...');
    mainWindow.show();
  });

  // Log if window fails to load
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Window failed to load:', errorCode, errorDescription);
  });

  // Log renderer console messages
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[Renderer ${level}] ${message} (${sourceId}:${line})`);
  });

  // Handle window close
  mainWindow.on('close', (event) => {
    console.log('Window is closing...');
  });

  mainWindow.on('closed', () => {
    console.log('Window closed');
    mainWindow = null;
  });
}

/**
 * App lifecycle: Ready
 */
app.whenReady().then(async () => {
  console.log('Electron app ready, starting initialization...');
  try {
    // Start Python backend first
    console.log('Starting Python backend...');
    await startPythonBackend();
    console.log('Python backend started successfully');

    // Create main window
    console.log('Creating main window...');
    createMainWindow();
    console.log('Main window created');

    // macOS: Re-create window when dock icon clicked
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createMainWindow();
      }
    });
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start Pulox: ${error.message}\n\nCheck the console for details.`
    );
    app.quit();
  }
});

/**
 * App lifecycle: All windows closed
 */
app.on('window-all-closed', () => {
  // macOS: Keep app running until explicit quit
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

/**
 * App lifecycle: Before quit
 */
app.on('before-quit', () => {
  stopPythonBackend();
});

/**
 * IPC: Get API URL
 */
ipcMain.handle('get-api-url', () => {
  return API_URL;
});

/**
 * IPC: Open file dialog
 */
ipcMain.handle('open-file-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result.filePaths;
});

/**
 * IPC: Show save dialog
 */
ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result.filePath;
});

/**
 * IPC: Show error dialog
 */
ipcMain.handle('show-error', async (event, title, message) => {
  await dialog.showErrorBox(title, message);
});

/**
 * IPC: Show message dialog
 */
ipcMain.handle('show-message', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result.response;
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  dialog.showErrorBox('Error', `An unexpected error occurred: ${error.message}`);
});
