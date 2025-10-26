/**
 * Preload Script
 * Exposes safe APIs to renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electron', {
  // Get API URL
  getApiUrl: () => ipcRenderer.invoke('get-api-url'),

  // File dialogs
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),

  // Message dialogs
  showError: (title, message) => ipcRenderer.invoke('show-error', title, message),
  showMessage: (options) => ipcRenderer.invoke('show-message', options)
});

// Shared API state
let apiBaseUrl = null;

// Expose API client to renderer
contextBridge.exposeInMainWorld('puloxApi', {
  // Initialize API client
  init: async function() {
    const url = await ipcRenderer.invoke('get-api-url');
    apiBaseUrl = url;
    return apiBaseUrl;
  },

  // Get current base URL
  get baseUrl() {
    return apiBaseUrl;
  },

  // Upload audio file
  uploadAudio: async function(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${apiBaseUrl}/upload`, {
      method: 'POST',
      body: formData
    });

    return response.json();
  },

  // Transcribe audio
  transcribe: async function(filename, language = null, modelSize = 'base') {
    const response = await fetch(`${apiBaseUrl}/transcribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_filename: filename,
        language: language,
        model_size: modelSize
      })
    });

    return response.json();
  },

  // Get transcripts list
  getTranscripts: async function() {
    const response = await fetch(`${apiBaseUrl}/transcripts`);
    return response.json();
  },

  // Get specific transcript
  getTranscript: async function(transcriptId) {
    const response = await fetch(`${apiBaseUrl}/transcripts/${transcriptId}`);
    return response.json();
  },

  // Save correction
  saveCorrection: async function(transcriptId, originalText, correctedText, metadata) {
    const response = await fetch(`${apiBaseUrl}/corrections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript_id: transcriptId,
        original_text: originalText,
        corrected_text: correctedText,
        metadata: metadata
      })
    });

    return response.json();
  },

  // Get correction
  getCorrection: async function(transcriptId) {
    const response = await fetch(`${apiBaseUrl}/corrections/${transcriptId}`);
    return response.json();
  },

  // Get corrections list
  getCorrections: async function() {
    const response = await fetch(`${apiBaseUrl}/corrections`);
    return response.json();
  },

  // Auto-correct text
  autoCorrect: async function(text, language = null, level = 'standard', useML = false) {
    const response = await fetch(`${apiBaseUrl}/correct`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        language: language,
        level: level,
        use_ml: useML
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Correction failed');
    }

    return response.json();
  },

  // Get audio URL
  getAudioUrl: function(filename) {
    return `${apiBaseUrl}/audio/${filename}`;
  },

  // Health check
  healthCheck: async function(timeout = 5000) {
    if (!apiBaseUrl) {
      await this.init();
    }

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(`${apiBaseUrl}/health`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error(`Health check timeout after ${timeout}ms`);
      }
      throw error;
    }
  }
});
