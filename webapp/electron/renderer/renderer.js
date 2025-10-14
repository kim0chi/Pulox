/**
 * Pulox Renderer Process
 * Frontend logic for the Electron application
 */

// Global state
let currentFile = null;
let currentTranscriptId = null;
let transcripts = [];

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  console.log('Pulox app initializing...');

  // Initialize API client
  await window.puloxApi.init();
  console.log('API client initialized, base URL:', window.puloxApi.baseUrl);

  // Check backend connection
  await checkBackendConnection();

  // Setup event listeners
  setupNavigation();
  setupUploadHandlers();
  setupTranscriptHandlers();
  setupAnnotationHandlers();
  setupSettingsHandlers();

  // Load initial data
  loadTranscripts();

  console.log('Pulox app ready!');
});

// ============================================================================
// Backend Connection
// ============================================================================

async function checkBackendConnection(retries = 10, delay = 500) {
  const statusIndicator = document.getElementById('connection-status');
  const statusText = document.getElementById('status-text');

  statusText.textContent = 'Connecting...';

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      console.log(`Connection attempt ${attempt}/${retries}...`);
      const health = await window.puloxApi.healthCheck();

      if (health.status === 'healthy') {
        console.log('Backend connected successfully!');
        statusIndicator.classList.add('connected');
        statusIndicator.classList.remove('disconnected');
        statusText.textContent = 'Connected';

        // Update settings page
        const apiUrl = await window.electron.getApiUrl();
        document.getElementById('api-url').textContent = apiUrl;
        document.getElementById('backend-status').textContent = 'Connected ✓';
        return true;
      }
    } catch (error) {
      console.log(`Connection attempt ${attempt} failed:`, error.message);

      if (attempt < retries) {
        // Wait before next attempt
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  // All retries failed
  console.error('Backend connection failed after all retries');
  statusIndicator.classList.add('disconnected');
  statusIndicator.classList.remove('connected');
  statusText.textContent = 'Disconnected';

  const apiUrl = await window.electron.getApiUrl();
  document.getElementById('api-url').textContent = apiUrl;
  document.getElementById('backend-status').textContent = 'Disconnected ✗';

  await window.electron.showError(
    'Connection Error',
    `Could not connect to Python backend at ${apiUrl}\n\nThe backend may still be starting. Please wait a moment and click "Check Connection" in Settings.`
  );

  return false;
}

// ============================================================================
// Navigation
// ============================================================================

function setupNavigation() {
  const navButtons = document.querySelectorAll('.nav-btn');
  const tabs = document.querySelectorAll('.tab-content');

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Remove active class from all buttons and tabs
      navButtons.forEach(b => b.classList.remove('active'));
      tabs.forEach(t => t.classList.remove('active'));

      // Add active class to clicked button and corresponding tab
      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab') + '-tab';
      document.getElementById(tabId).classList.add('active');
    });
  });
}

// ============================================================================
// Upload & Transcription
// ============================================================================

function setupUploadHandlers() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const selectFileBtn = document.getElementById('select-file-btn');
  const transcribeBtn = document.getElementById('transcribe-btn');
  const uploadAnotherBtn = document.getElementById('upload-another-btn');

  // Click to select file
  selectFileBtn.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('click', (e) => {
    if (e.target === dropZone || e.target.classList.contains('drop-zone-content')) {
      fileInput.click();
    }
  });

  // File input change
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });

  // Drag and drop
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    if (e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  });

  // Transcribe button
  transcribeBtn.addEventListener('click', handleTranscribe);

  // Upload another button
  uploadAnotherBtn.addEventListener('click', resetUploadForm);
}

function handleFileSelect(file) {
  console.log('File selected:', file.name);

  // Validate file type
  const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/x-m4a', 'audio/flac', 'audio/ogg', 'audio/webm'];
  const validExtensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm'];

  const hasValidType = validTypes.some(type => file.type.includes(type.split('/')[1]));
  const hasValidExt = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

  if (!hasValidType && !hasValidExt) {
    window.electron.showError(
      'Invalid File',
      'Please select a valid audio file (WAV, MP3, M4A, FLAC, OGG, WEBM)'
    );
    return;
  }

  currentFile = file;

  // Show file info
  document.querySelector('.drop-zone').style.display = 'none';
  document.getElementById('file-info').style.display = 'block';

  document.getElementById('file-name').textContent = file.name;
  document.getElementById('file-size').textContent = formatFileSize(file.size);
}

async function handleTranscribe() {
  if (!currentFile) {
    window.electron.showError('No File', 'Please select an audio file first.');
    return;
  }

  const language = document.getElementById('language-select').value;
  const modelSize = document.getElementById('model-select').value;

  // Hide file info, show progress
  document.getElementById('file-info').style.display = 'none';
  document.getElementById('progress-section').style.display = 'block';

  const progressFill = document.getElementById('progress-fill');
  const progressText = document.getElementById('progress-text');

  try {
    // Step 1: Upload file
    progressText.textContent = 'Uploading file...';
    progressFill.style.width = '20%';

    const uploadResult = await window.puloxApi.uploadAudio(currentFile);
    console.log('Upload result:', uploadResult);

    // Step 2: Transcribe
    progressText.textContent = 'Transcribing audio... This may take a few minutes.';
    progressFill.style.width = '50%';

    const transcribeResult = await window.puloxApi.transcribe(
      uploadResult.filename,
      language || null,
      modelSize
    );
    console.log('Transcribe result:', transcribeResult);

    // Step 3: Complete
    progressText.textContent = 'Transcription complete!';
    progressFill.style.width = '100%';

    // Show result
    setTimeout(() => {
      document.getElementById('progress-section').style.display = 'none';
      showTranscriptionResult(transcribeResult);
    }, 500);

  } catch (error) {
    console.error('Transcription error:', error);
    window.electron.showError(
      'Transcription Failed',
      `Error: ${error.message || 'Unknown error occurred'}`
    );

    // Reset form
    resetUploadForm();
  }
}

function showTranscriptionResult(result) {
  document.getElementById('result-section').style.display = 'block';

  document.getElementById('result-language').textContent = result.language || 'Unknown';
  document.getElementById('result-duration').textContent = result.duration.toFixed(2);
  document.getElementById('transcript-text').textContent = result.text;

  currentTranscriptId = result.id;

  // Setup annotate button
  document.getElementById('annotate-btn').addEventListener('click', () => {
    openAnnotationEditor(result.id);
    // Switch to annotations tab
    document.querySelector('[data-tab="annotations"]').click();
  });
}

function resetUploadForm() {
  currentFile = null;
  document.querySelector('.drop-zone').style.display = 'block';
  document.getElementById('file-info').style.display = 'none';
  document.getElementById('progress-section').style.display = 'none';
  document.getElementById('result-section').style.display = 'none';
  document.getElementById('file-input').value = '';
  document.getElementById('progress-fill').style.width = '0%';
}

// ============================================================================
// Transcripts Management
// ============================================================================

function setupTranscriptHandlers() {
  document.getElementById('refresh-transcripts-btn').addEventListener('click', loadTranscripts);
}

async function loadTranscripts() {
  const listContainer = document.getElementById('transcripts-list');
  listContainer.innerHTML = '<p class="loading-text">Loading transcripts...</p>';

  try {
    const result = await window.puloxApi.getTranscripts();
    transcripts = result.transcripts || [];

    if (transcripts.length === 0) {
      listContainer.innerHTML = '<p class="loading-text">No transcripts yet. Upload an audio file to get started!</p>';
      return;
    }

    listContainer.innerHTML = '';

    transcripts.forEach(transcript => {
      const card = createTranscriptCard(transcript);
      listContainer.appendChild(card);
    });

  } catch (error) {
    console.error('Failed to load transcripts:', error);
    listContainer.innerHTML = '<p class="loading-text">Failed to load transcripts.</p>';
  }
}

function createTranscriptCard(transcript) {
  const card = document.createElement('div');
  card.className = 'transcript-card';

  const badge = transcript.has_correction
    ? '<span class="transcript-badge annotated">✓ Annotated</span>'
    : '<span class="transcript-badge pending">Pending</span>';

  card.innerHTML = `
    <div class="transcript-card-header">
      <h3>${transcript.id}</h3>
      ${badge}
    </div>
    <div class="transcript-meta">
      <span>📁 ${transcript.audio_file}</span>
      <span>🌐 ${transcript.language.toUpperCase()}</span>
      <span>⏱️ ${transcript.duration.toFixed(2)}s</span>
    </div>
    <div class="transcript-actions">
      <button class="btn btn-primary view-btn" data-id="${transcript.id}">👁️ View</button>
      <button class="btn btn-secondary annotate-btn" data-id="${transcript.id}">✏️ Annotate</button>
    </div>
  `;

  // Event listeners
  card.querySelector('.view-btn').addEventListener('click', () => {
    viewTranscript(transcript.id);
  });

  card.querySelector('.annotate-btn').addEventListener('click', () => {
    openAnnotationEditor(transcript.id);
    document.querySelector('[data-tab="annotations"]').click();
  });

  return card;
}

async function viewTranscript(transcriptId) {
  try {
    const transcript = await window.puloxApi.getTranscript(transcriptId);

    // Show in a message box
    await window.electron.showMessage({
      type: 'info',
      title: `Transcript: ${transcriptId}`,
      message: transcript.text.substring(0, 500) + (transcript.text.length > 500 ? '...' : ''),
      buttons: ['OK']
    });

  } catch (error) {
    console.error('Failed to load transcript:', error);
    window.electron.showError('Error', 'Failed to load transcript');
  }
}

// ============================================================================
// Annotation Editor
// ============================================================================

function setupAnnotationHandlers() {
  document.getElementById('save-annotation-btn').addEventListener('click', saveAnnotation);
  document.getElementById('cancel-annotation-btn').addEventListener('click', closeAnnotationEditor);
  document.getElementById('play-audio-btn').addEventListener('click', playCurrentAudio);
  document.getElementById('auto-correct-btn').addEventListener('click', autoCorrectText);
}

async function openAnnotationEditor(transcriptId) {
  try {
    // Load transcript
    const transcript = await window.puloxApi.getTranscript(transcriptId);

    // Show editor
    document.getElementById('annotation-selector').style.display = 'none';
    document.getElementById('annotation-editor').style.display = 'block';

    // Set data
    document.getElementById('current-transcript-id').textContent = transcriptId;
    document.getElementById('original-text').value = transcript.text;

    // Check if correction exists
    try {
      const correction = await window.puloxApi.getCorrection(transcriptId);
      document.getElementById('corrected-text').value = correction.corrected;
    } catch {
      // No existing correction, start with original
      document.getElementById('corrected-text').value = transcript.text;
    }

    currentTranscriptId = transcriptId;

  } catch (error) {
    console.error('Failed to open annotation editor:', error);
    window.electron.showError('Error', 'Failed to load transcript for annotation');
  }
}

function closeAnnotationEditor() {
  document.getElementById('annotation-selector').style.display = 'block';
  document.getElementById('annotation-editor').style.display = 'none';
  currentTranscriptId = null;
}

async function saveAnnotation() {
  const annotatorName = document.getElementById('annotator-name').value.trim();

  if (!annotatorName) {
    window.electron.showError('Missing Information', 'Please enter your name');
    return;
  }

  const originalText = document.getElementById('original-text').value;
  const correctedText = document.getElementById('corrected-text').value;

  if (originalText === correctedText) {
    const response = await window.electron.showMessage({
      type: 'warning',
      title: 'No Changes',
      message: 'You have not made any changes to the transcript. Save anyway?',
      buttons: ['Cancel', 'Save Anyway']
    });

    if (response === 0) return; // Cancel
  }

  const metadata = {
    annotator: annotatorName,
    subject: document.getElementById('subject-select').value,
    audio_quality: document.getElementById('quality-select').value,
    primary_language: document.getElementById('language-dist-select').value,
    notes: document.getElementById('notes-input').value
  };

  try {
    const result = await window.puloxApi.saveCorrection(
      currentTranscriptId,
      originalText,
      correctedText,
      metadata
    );

    console.log('Annotation saved:', result);

    await window.electron.showMessage({
      type: 'info',
      title: 'Success',
      message: `Annotation saved successfully!\n\nChanges: ${result.changes.word_changes} words\nSimilarity: ${(result.changes.similarity_ratio * 100).toFixed(1)}%`,
      buttons: ['OK']
    });

    // Refresh transcripts list
    loadTranscripts();

    // Close editor
    closeAnnotationEditor();

  } catch (error) {
    console.error('Failed to save annotation:', error);
    window.electron.showError('Save Failed', 'Failed to save annotation: ' + error.message);
  }
}

async function playCurrentAudio() {
  if (!currentTranscriptId) return;

  try {
    const transcript = await window.puloxApi.getTranscript(currentTranscriptId);
    const audioUrl = window.puloxApi.getAudioUrl(transcript.audio_file);

    // Create audio element
    const audio = new Audio(audioUrl);
    audio.play();

    // Show notification
    console.log('Playing audio:', audioUrl);

  } catch (error) {
    console.error('Failed to play audio:', error);
    window.electron.showError('Playback Error', 'Failed to play audio file');
  }
}

async function autoCorrectText() {
  const correctedTextArea = document.getElementById('corrected-text');
  const originalText = correctedTextArea.value;

  if (!originalText || !originalText.trim()) {
    window.electron.showError('No Text', 'There is no text to correct');
    return;
  }

  try {
    // Show loading state
    const autoCorrectBtn = document.getElementById('auto-correct-btn');
    const originalBtnText = autoCorrectBtn.textContent;
    autoCorrectBtn.disabled = true;
    autoCorrectBtn.textContent = 'Correcting...';

    // Get correction settings (can be enhanced with UI controls later)
    const level = 'standard';  // Can add a dropdown for this
    const useML = false;  // ML requires model download, start with rules only

    // Call auto-correct API
    const result = await window.puloxApi.autoCorrect(originalText, null, level, useML);

    // Restore button
    autoCorrectBtn.disabled = false;
    autoCorrectBtn.textContent = originalBtnText;

    // If no changes, show message
    if (result.original_text === result.corrected_text) {
      await window.electron.showMessage({
        type: 'info',
        title: 'No Corrections',
        message: 'No errors were found in the text.',
        buttons: ['OK']
      });
      return;
    }

    // Show before/after comparison
    const changesCount = result.summary.total_changes;
    const response = await window.electron.showMessage({
      type: 'question',
      title: 'Auto-Correction Results',
      message: `Found ${changesCount} potential correction(s).\n\nApply these corrections?`,
      detail: `Method: ${result.method}\nLanguage: ${result.language}\nConfidence: ${(result.confidence_score * 100).toFixed(1)}%`,
      buttons: ['Cancel', 'Apply Corrections']
    });

    // Apply if user confirms
    if (response === 1) {  // Apply Corrections button
      correctedTextArea.value = result.corrected_text;

      // Show success message with changes
      let changesList = '';
      if (result.changes && result.changes.length > 0) {
        const topChanges = result.changes.slice(0, 5);  // Show first 5 changes
        changesList = topChanges.map(c => `• ${c.description}`).join('\n');
        if (result.changes.length > 5) {
          changesList += `\n... and ${result.changes.length - 5} more`;
        }
      }

      await window.electron.showMessage({
        type: 'info',
        title: 'Corrections Applied',
        message: `${changesCount} correction(s) applied successfully!`,
        detail: changesList || 'See corrected text in the editor.',
        buttons: ['OK']
      });
    }

  } catch (error) {
    console.error('Auto-correction failed:', error);
    window.electron.showError('Correction Failed', `Auto-correction failed: ${error.message}`);

    // Restore button
    const autoCorrectBtn = document.getElementById('auto-correct-btn');
    autoCorrectBtn.disabled = false;
    autoCorrectBtn.textContent = '🔧 Auto-Correct';
  }
}

// ============================================================================
// Settings
// ============================================================================

function setupSettingsHandlers() {
  document.getElementById('check-backend-btn').addEventListener('click', checkBackendConnection);

  // Load saved settings
  const savedModel = localStorage.getItem('defaultModel') || 'base';
  document.getElementById('default-model-select').value = savedModel;

  // Save settings on change
  document.getElementById('default-model-select').addEventListener('change', (e) => {
    localStorage.setItem('defaultModel', e.target.value);
    document.getElementById('model-select').value = e.target.value;
  });
}

// ============================================================================
// Utility Functions
// ============================================================================

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Export for debugging
window.puloxDebug = {
  checkBackendConnection,
  loadTranscripts,
  currentFile,
  currentTranscriptId,
  transcripts
};
