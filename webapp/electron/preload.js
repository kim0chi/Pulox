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

// Expose API client to renderer
contextBridge.exposeInMainWorld('puloxApi', {
  // Base URL will be fetched from main process
  baseUrl: null,

  // Initialize API client
  init: async function() {
    this.baseUrl = await ipcRenderer.invoke('get-api-url');
  },

  // Upload audio file
  uploadAudio: async function(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData
    });

    return response.json();
  },

  // Transcribe audio
  transcribe: async function(filename, language = null, modelSize = 'base') {
    const response = await fetch(`${this.baseUrl}/transcribe`, {
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
    const response = await fetch(`${this.baseUrl}/transcripts`);
    return response.json();
  },

  // Get specific transcript
  getTranscript: async function(transcriptId) {
    const response = await fetch(`${this.baseUrl}/transcripts/${transcriptId}`);
    return response.json();
  },

  // Save correction
  saveCorrection: async function(transcriptId, originalText, correctedText, metadata) {
    const response = await fetch(`${this.baseUrl}/corrections`, {
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
    const response = await fetch(`${this.baseUrl}/corrections/${transcriptId}`);
    return response.json();
  },

  // Get corrections list
  getCorrections: async function() {
    const response = await fetch(`${this.baseUrl}/corrections`);
    return response.json();
  },

  // Auto-correct text
  autoCorrect: async function(text, language = null, level = 'standard', useML = false) {
    const response = await fetch(`${this.baseUrl}/correct`, {
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
    return `${this.baseUrl}/audio/${filename}`;
  },

  // Health check
  healthCheck: async function() {
    if (!this.baseUrl) {
      await this.init();
    }
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  }
});
