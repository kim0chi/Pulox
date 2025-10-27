/**
 * Pulox Renderer Process
 * Frontend logic for the Electron application
 */

// Global state
let currentFile = null;
let currentTranscriptId = null;
let transcripts = [];
let audioElement = null;
let wordTimestamps = [];
let isProgressBarDragging = false;
let isSeeking = false;

// Word correction state
let selectedWordIndex = -1;
let selectedWordElement = null;
let editHistory = [];
let historyIndex = -1;
const MAX_HISTORY = 50;

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
  setupWordCorrectionHandlers();

  // Load initial data
  loadTranscripts();

  console.log('Pulox app ready!');
});

// ============================================================================
// Backend Connection
// ============================================================================

async function checkBackendConnection(retries = 3, delay = 1500) {
  console.log('[Health Check] Starting connection check...');

  const statusIndicator = document.getElementById('connection-status');
  const statusText = document.getElementById('status-text');

  if (statusText) {
    statusText.textContent = 'Connecting...';
  }

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      console.log(`[Health Check] Attempt ${attempt}/${retries}...`);
      if (statusText) {
        statusText.textContent = `Connecting... (${attempt}/${retries})`;
      }

      // Call health check with 3 second timeout
      // The healthCheck function handles its own initialization internally
      const health = await window.puloxApi.healthCheck(3000);
      console.log('[Health Check] Response:', health);

      if (health && health.status === 'healthy') {
        console.log('[Health Check] Backend is healthy!');
        if (statusIndicator) {
          statusIndicator.classList.add('connected');
          statusIndicator.classList.remove('disconnected');
        }
        if (statusText) {
          statusText.textContent = 'Connected';
        }

        // Update settings page
        const apiUrl = await window.electron.getApiUrl();
        const apiUrlElement = document.getElementById('api-url');
        const backendStatusElement = document.getElementById('backend-status');
        if (apiUrlElement) apiUrlElement.textContent = apiUrl;
        if (backendStatusElement) backendStatusElement.textContent = 'Connected ✓';
        return true;
      } else {
        console.warn('[Health Check] Unexpected health response:', health);
        throw new Error('Invalid health check response');
      }
    } catch (error) {
      const errorType = error.message.includes('timeout') ? 'timeout' :
                       error.message.includes('fetch') ? 'network' :
                       error.message.includes('Failed to fetch') ? 'network' : 'unknown';
      console.error(`[Health Check] Attempt ${attempt}/${retries} failed (${errorType}):`, error.message);

      if (attempt < retries) {
        // Wait before next attempt (longer delay for timeouts)
        const retryDelay = errorType === 'timeout' ? delay * 2 : delay;
        console.log(`[Health Check] Waiting ${retryDelay}ms before retry...`);
        if (statusText) {
          statusText.textContent = `Retrying... (${attempt}/${retries})`;
        }
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }

  // All retries failed
  console.error('[Health Check] All attempts failed');
  if (statusIndicator) {
    statusIndicator.classList.add('disconnected');
    statusIndicator.classList.remove('connected');
  }
  if (statusText) {
    statusText.textContent = 'Disconnected';
  }

  const apiUrl = await window.electron.getApiUrl();
  const apiUrlElement = document.getElementById('api-url');
  const backendStatusElement = document.getElementById('backend-status');
  if (apiUrlElement) apiUrlElement.textContent = apiUrl;
  if (backendStatusElement) backendStatusElement.textContent = 'Disconnected ✗';

  await window.electron.showError(
    'Connection Error',
    `Could not connect to Python backend at ${apiUrl}\n\nThe backend may still be starting. Please wait a moment and try again.`
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
  document.getElementById('auto-correct-btn').addEventListener('click', autoCorrectText);

  // Audio player controls
  document.getElementById('play-pause-btn').addEventListener('click', togglePlayPause);

  // Progress bar interactions
  const progressBar = document.querySelector('.audio-progress-bar');
  if (progressBar) {
    progressBar.addEventListener('click', handleProgressBarClick);
  }

  const progressHandle = document.getElementById('audio-progress-handle');
  if (progressHandle) {
    progressHandle.addEventListener('mousedown', startProgressDrag);
  }
  document.addEventListener('mousemove', handleProgressDrag);
  document.addEventListener('mouseup', stopProgressDrag);
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

    // Reconstruct full text from segments if transcript.text is undefined
    let fullText = transcript.text;
    if (!fullText && transcript.segments && transcript.segments.length > 0) {
      fullText = transcript.segments.map(seg => seg.text).join(' ');
    }

    // Keep hidden textareas for compatibility
    document.getElementById('original-text').value = fullText || '';

    // Check if correction exists (add safety guard for undefined text)
    let correctedText = fullText || '';
    try {
      const correction = await window.puloxApi.getCorrection(transcriptId);
      correctedText = correction.corrected;
      document.getElementById('corrected-text').value = correction.corrected;
    } catch {
      // No existing correction, start with original (use fullText, not transcript.text!)
      document.getElementById('corrected-text').value = fullText || '';
    }

    currentTranscriptId = transcriptId;

    // Initialize audio player with word-level sync (this populates wordTimestamps)
    initializeAudioPlayer(transcript);

    // If fullText is still empty, reconstruct from wordTimestamps
    if (!fullText && wordTimestamps.length > 0) {
      fullText = wordTimestamps.map(w => w.word).join(' ');
      document.getElementById('original-text').value = fullText;
    }

    // If correctedText is still empty, use the reconstructed fullText
    if (!correctedText && fullText) {
      correctedText = fullText;
      document.getElementById('corrected-text').value = fullText;
    }

    // Debug logging
    console.log('[Annotation Editor] Full text length:', (fullText || '').length);
    console.log('[Annotation Editor] Corrected text length:', (correctedText || '').length);
    console.log('[Annotation Editor] Word timestamps count:', wordTimestamps.length);

    // Render word-level editors after audio player is ready
    renderWordLevelEditors(transcript, correctedText);

  } catch (error) {
    console.error('Failed to open annotation editor:', error);
    window.electron.showError('Error', 'Failed to load transcript for annotation');
  }
}

function closeAnnotationEditor() {
  document.getElementById('annotation-selector').style.display = 'block';
  document.getElementById('annotation-editor').style.display = 'none';
  currentTranscriptId = null;

  // Clean up audio player
  if (audioElement) {
    audioElement.pause();
    audioElement.src = '';
    audioElement = null;
  }
  wordTimestamps = [];
  document.getElementById('audio-player-section').style.display = 'none';
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

// ============================================================================
// Word-Level Transcript Editors
// ============================================================================

function renderWordLevelEditors(transcript, correctedText) {
  // Render original transcript with word-level data
  renderOriginalTranscriptEditor();

  // Render corrected transcript
  renderCorrectedTranscriptEditor(correctedText);

  // Note: Diff highlighting removed - only show highlights after auto-correct
  // User preference: clean interface, only highlight changes made by auto-correct
}

function renderOriginalTranscriptEditor() {
  const container = document.getElementById('original-text-editor');
  if (!container || wordTimestamps.length === 0) return;

  container.innerHTML = '';

  wordTimestamps.forEach((wordData, index) => {
    const wordSpan = document.createElement('span');
    wordSpan.className = 'editor-word';
    wordSpan.textContent = wordData.word;
    wordSpan.dataset.index = index;
    wordSpan.dataset.start = wordData.start;
    wordSpan.dataset.end = wordData.end;
    wordSpan.dataset.confidence = wordData.confidence;

    // Add confidence-based styling
    if (wordData.confidence >= 0.8) {
      wordSpan.classList.add('confidence-high');
    } else if (wordData.confidence >= 0.5) {
      wordSpan.classList.add('confidence-medium');
    } else {
      wordSpan.classList.add('confidence-low');
    }

    // Add tooltip with word info
    const tooltip = document.createElement('span');
    tooltip.className = 'editor-word-tooltip';
    tooltip.textContent = `${formatTime(wordData.start)} | Confidence: ${(wordData.confidence * 100).toFixed(0)}%`;
    wordSpan.appendChild(tooltip);

    // Click to sync audio
    wordSpan.addEventListener('click', () => {
      // Check if audio is ready before seeking
      if (!audioElement) {
        console.warn('[Word Click] No audio element');
        showTemporaryMessage('⏸ Audio player not initialized');
        return;
      }

      if (audioElement.readyState < 1) {
        console.warn('[Word Click] Audio not ready yet, waiting for metadata...');
        showTemporaryMessage('⏳ Audio loading... please wait');
        return;
      }

      const startTime = parseFloat(wordSpan.dataset.start);
      console.log(`[Word Click Original] Word: "${wordSpan.textContent}", dataset.start: "${wordSpan.dataset.start}", parsed: ${startTime}`);
      if (!isNaN(startTime) && startTime >= 0) {
        console.log(`[Word Click] Seeking to ${startTime.toFixed(2)}s for word: "${wordSpan.textContent}"`);
        seekToTime(startTime, wordSpan.textContent);
      } else {
        console.warn(`[Word Click] Invalid timestamp for word: "${wordSpan.textContent}"`, wordSpan.dataset.start);
      }
    });

    container.appendChild(wordSpan);
    container.appendChild(document.createTextNode(' '));
  });
}

function renderCorrectedTranscriptEditor(correctedText) {
  const container = document.getElementById('corrected-text-editor');
  if (!container) return;

  // Save initial state for undo/redo
  editHistory = [];
  historyIndex = -1;

  container.innerHTML = '';

  // Split corrected text into words and filter out empty strings
  const words = (correctedText || '').trim().split(/\s+/).filter(word => word.length > 0);

  // If no words, don't render anything
  if (words.length === 0) {
    container.textContent = 'No text to display. Please check the transcript.';
    return;
  }

  words.forEach((word, index) => {
    const wordSpan = document.createElement('span');
    wordSpan.className = 'editor-word';
    wordSpan.textContent = word;
    wordSpan.dataset.index = index;

    // Try to match with original word for timing info
    if (index < wordTimestamps.length) {
      const originalData = wordTimestamps[index];
      wordSpan.dataset.start = originalData.start;
      wordSpan.dataset.end = originalData.end;
    }

    // Attach word correction handlers
    attachWordHandlers(wordSpan, index);

    container.appendChild(wordSpan);
    container.appendChild(document.createTextNode(' '));
  });

  // Update hidden textarea
  updateCorrectedTextarea();

  // Save initial state
  saveState();

  // Click outside to deselect
  container.addEventListener('click', (e) => {
    if (e.target === container) {
      deselectWord();
    }
  });
}

function updateCorrectedTextarea() {
  const container = document.getElementById('corrected-text-editor');
  const textarea = document.getElementById('corrected-text');

  if (container && textarea) {
    // Extract text from word spans
    const words = Array.from(container.querySelectorAll('.editor-word'))
      .map(span => span.textContent.trim())
      .filter(word => word.length > 0);

    textarea.value = words.join(' ');
  }
}

function highlightAutoCorrectChanges(beforeText, afterText) {
  /**
   * Highlight only the changes made by auto-correct
   * Compares the corrected text BEFORE vs AFTER auto-correct was applied
   */
  const correctedContainer = document.getElementById('corrected-text-editor');
  if (!correctedContainer) return;

  // Split into words
  const beforeWords = beforeText.trim().split(/\s+/).filter(w => w.length > 0).map(w => w.toLowerCase());
  const afterWords = afterText.trim().split(/\s+/).filter(w => w.length > 0).map(w => w.toLowerCase());

  // If identical, no highlighting needed
  if (beforeWords.join(' ') === afterWords.join(' ')) {
    return;
  }

  // Clear previous auto-correct highlights
  correctedContainer.querySelectorAll('.editor-word').forEach(span => {
    span.classList.remove('auto-corrected');
  });

  // Compute diff
  const diffResult = computeDiff(beforeWords, afterWords);
  const correctedSpans = correctedContainer.querySelectorAll('.editor-word');

  // Highlight words that were changed by auto-correct
  diffResult.forEach(change => {
    if (change.type === 'insert' || change.type === 'replace') {
      if (correctedSpans[change.newIndex]) {
        correctedSpans[change.newIndex].classList.add('auto-corrected');
        correctedSpans[change.newIndex].style.backgroundColor = '#90EE90';  // Light green
        correctedSpans[change.newIndex].style.fontWeight = 'bold';
      }
    }
  });

  console.log(`[Auto-Correct] Highlighted ${diffResult.length} word change(s)`);
}

function updateDiffHighlighting() {
  const originalContainer = document.getElementById('original-text-editor');
  const correctedContainer = document.getElementById('corrected-text-editor');

  if (!originalContainer || !correctedContainer) return;

  const originalWords = Array.from(originalContainer.querySelectorAll('.editor-word'))
    .map(span => span.textContent.trim().toLowerCase());
  const correctedWords = Array.from(correctedContainer.querySelectorAll('.editor-word'))
    .map(span => span.textContent.trim().toLowerCase());

  // Clear all previous diff classes first
  originalContainer.querySelectorAll('.editor-word').forEach(span => {
    span.classList.remove('word-deleted', 'word-modified');
  });
  correctedContainer.querySelectorAll('.editor-word').forEach(span => {
    span.classList.remove('word-added', 'word-modified');
  });

  // Check if texts are actually different - if not, skip highlighting
  const originalText = originalWords.join(' ');
  const correctedText = correctedWords.join(' ');

  if (originalText === correctedText) {
    // Texts are identical, no highlighting needed
    return;
  }

  // Use a more sophisticated diff algorithm - sequence matching
  // This handles insertions and deletions better than simple index comparison
  const diffResult = computeDiff(originalWords, correctedWords);

  // Apply highlighting based on diff results
  const originalSpans = originalContainer.querySelectorAll('.editor-word');
  const correctedSpans = correctedContainer.querySelectorAll('.editor-word');

  diffResult.forEach(change => {
    if (change.type === 'delete') {
      // Word was in original but removed in corrected
      if (originalSpans[change.oldIndex]) {
        originalSpans[change.oldIndex].classList.add('word-deleted');
      }
    } else if (change.type === 'insert') {
      // Word was added in corrected
      if (correctedSpans[change.newIndex]) {
        correctedSpans[change.newIndex].classList.add('word-added');
      }
    } else if (change.type === 'replace') {
      // Word was modified
      if (originalSpans[change.oldIndex]) {
        originalSpans[change.oldIndex].classList.add('word-modified');
      }
      if (correctedSpans[change.newIndex]) {
        correctedSpans[change.newIndex].classList.add('word-modified');
      }
    }
  });
}

// Compute diff between two word arrays using dynamic programming
function computeDiff(oldWords, newWords) {
  const changes = [];

  // Build edit distance matrix
  const m = oldWords.length;
  const n = newWords.length;
  const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

  // Initialize base cases
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;

  // Fill matrix
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (oldWords[i - 1] === newWords[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = 1 + Math.min(
          dp[i - 1][j],     // delete
          dp[i][j - 1],     // insert
          dp[i - 1][j - 1]  // replace
        );
      }
    }
  }

  // Backtrack to find actual changes
  let i = m, j = n;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && oldWords[i - 1] === newWords[j - 1]) {
      // No change
      i--;
      j--;
    } else if (i > 0 && j > 0 && dp[i][j] === dp[i - 1][j - 1] + 1) {
      // Replace
      changes.push({ type: 'replace', oldIndex: i - 1, newIndex: j - 1 });
      i--;
      j--;
    } else if (j > 0 && (i === 0 || dp[i][j] === dp[i][j - 1] + 1)) {
      // Insert
      changes.push({ type: 'insert', newIndex: j - 1 });
      j--;
    } else {
      // Delete
      changes.push({ type: 'delete', oldIndex: i - 1 });
      i--;
    }
  }

  return changes;
}

// ============================================================================
// Audio Player with Word-Level Synchronization
// ============================================================================

// Timing configuration for accurate word synchronization
const LOOKAHEAD_MS = 80;           // Highlight words slightly early (accounts for perception delay)
const TIMING_TOLERANCE_MS = 100;   // Tolerance window for timing inaccuracies (±100ms)
const SHOW_UPCOMING_WORDS = 1;     // Number of upcoming words to show as preview
const MIN_CONFIDENCE = 0.3;        // Minimum confidence threshold for timing adjustments

// Cache for performance optimization
let lastActiveWordIndex = -1;

function initializeAudioPlayer(transcript) {
  try {
    // Get audio element
    audioElement = document.getElementById('sync-audio');
    if (!audioElement) {
      console.error('Audio element not found');
      return;
    }

    // Show loading indicator
    const audioPlayerSection = document.getElementById('audio-player-section');
    if (audioPlayerSection) {
      audioPlayerSection.classList.add('audio-loading');
      const existingIndicator = audioPlayerSection.querySelector('.audio-loading-indicator');
      if (!existingIndicator) {
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'audio-loading-indicator';
        loadingIndicator.innerHTML = '<span style="color: #3498db;">⏳ Loading audio... (word clicks will be enabled when ready)</span>';
        loadingIndicator.style.cssText = 'padding: 10px; text-align: center; background: #ecf0f1; border-radius: 5px; margin-bottom: 10px;';
        audioPlayerSection.insertBefore(loadingIndicator, audioPlayerSection.firstChild);
      }
    }

    // Set audio source
    const audioUrl = window.puloxApi.getAudioUrl(transcript.audio_file);
    audioElement.src = audioUrl;

    // Extract word-level timestamps from segments
    wordTimestamps = [];
    lastActiveWordIndex = -1; // Reset cache
    let wordIndex = 0;

    if (transcript.segments && transcript.segments.length > 0) {
      transcript.segments.forEach((segment, segmentIndex) => {
        if (segment.words && segment.words.length > 0) {
          // Use word-level timestamps with confidence scores
          segment.words.forEach((wordData) => {
            wordTimestamps.push({
              word: wordData.word,
              start: wordData.start,
              end: wordData.end,
              confidence: wordData.probability || 1.0, // Store confidence score
              index: wordIndex++,
              segmentIndex: segmentIndex
            });
          });
        } else {
          // Fallback: no word-level data, use segment text
          const words = segment.text.trim().split(/\s+/);
          const segmentDuration = segment.end - segment.start;
          const timePerWord = segmentDuration / words.length;

          words.forEach((word, i) => {
            wordTimestamps.push({
              word: word,
              start: segment.start + (i * timePerWord),
              end: segment.start + ((i + 1) * timePerWord),
              confidence: 0.5, // Lower confidence for estimated timestamps
              index: wordIndex++,
              segmentIndex: segmentIndex
            });
          });
        }
      });
    }

    // Render word transcript
    renderWordTranscript();

    // Set up audio event listeners
    audioElement.addEventListener('loadedmetadata', () => {
      console.log('[Audio] Metadata loaded, readyState:', audioElement.readyState);
      updateTotalTime();

      // Remove loading indicator - audio is ready
      const audioPlayerSection = document.getElementById('audio-player-section');
      if (audioPlayerSection) {
        const loadingIndicator = audioPlayerSection.querySelector('.audio-loading-indicator');
        if (loadingIndicator) {
          loadingIndicator.remove();
          console.log('[Audio] Loading indicator removed - audio ready');
        }
        audioPlayerSection.classList.remove('audio-loading');
        audioPlayerSection.classList.add('audio-ready');
      }
    });
    audioElement.addEventListener('canplay', () => {
      console.log('[Audio] Can play, readyState:', audioElement.readyState);
    });
    audioElement.addEventListener('canplaythrough', () => {
      console.log('[Audio] Can play through, readyState:', audioElement.readyState);
    });
    audioElement.addEventListener('timeupdate', handleAudioTimeUpdate);
    audioElement.addEventListener('ended', handleAudioEnded);
    audioElement.addEventListener('play', updatePlayButton);
    audioElement.addEventListener('pause', updatePlayButton);
    audioElement.addEventListener('seeked', handleSeeked);
    audioElement.addEventListener('seeking', handleSeeking);

    // Show audio player section
    document.getElementById('audio-player-section').style.display = 'block';

    console.log(`Audio player initialized with ${wordTimestamps.length} words`);

    // Debug: Log first few word timestamps to verify data
    if (wordTimestamps.length > 0) {
      console.log('[Audio Player] Sample word timestamps:');
      const sampleSize = Math.min(5, wordTimestamps.length);
      for (let i = 0; i < sampleSize; i++) {
        const w = wordTimestamps[i];
        console.log(`  [${i}] "${w.word}" -> ${w.start.toFixed(2)}s - ${w.end.toFixed(2)}s (confidence: ${(w.confidence * 100).toFixed(0)}%)`);
      }
    }

  } catch (error) {
    console.error('Failed to initialize audio player:', error);
    window.electron.showError('Audio Error', 'Failed to initialize audio player');
  }
}

// Helper function for safe audio seeking
// Track pending seek to prevent race conditions
let pendingSeekHandler = null;

function seekToTime(time, wordText = '') {
  if (!audioElement) {
    console.warn('[Seek] No audio element available');
    return false;
  }

  // Cancel any previous pending seek
  if (pendingSeekHandler) {
    audioElement.removeEventListener('loadedmetadata', pendingSeekHandler);
    audioElement.removeEventListener('canplay', pendingSeekHandler);
    pendingSeekHandler = null;
    console.log('[Seek] Cancelled previous pending seek');
  }

  const readyStateNames = ['HAVE_NOTHING', 'HAVE_METADATA', 'HAVE_CURRENT_DATA', 'HAVE_FUTURE_DATA', 'HAVE_ENOUGH_DATA'];
  const currentState = readyStateNames[audioElement.readyState] || 'UNKNOWN';

  console.log(`[Seek] Attempting to seek to ${time.toFixed(2)}s for word "${wordText}"`);
  console.log(`[Seek] Current audio time: ${audioElement.currentTime.toFixed(2)}s`);
  console.log(`[Seek] Audio readyState: ${audioElement.readyState} (${currentState})`);
  console.log(`[Seek] Audio duration: ${audioElement.duration}s`);
  console.log(`[Seek] Audio paused: ${audioElement.paused}`);
  console.log(`[Seek] Audio src: ${audioElement.src}`);

  // Check if audio has loaded enough to seek (need at least HAVE_METADATA)
  if (audioElement.readyState >= 1) {
    // Audio has metadata - can seek immediately
    console.log(`[Seek] Audio ready, setting currentTime from ${audioElement.currentTime.toFixed(2)}s to ${time.toFixed(2)}s`);
    isSeeking = true;
    audioElement.currentTime = time;
    console.log(`[Seek] After setting, currentTime is now: ${audioElement.currentTime.toFixed(2)}s`);
    if (audioElement.paused) {
      console.log(`[Seek] Audio was paused, calling play()`);
      audioElement.play().catch(err => console.error('[Seek] Play failed:', err));
    }
    return true;
  } else {
    // Audio not ready yet - wait for metadata to load
    console.warn(`[Seek] Audio not ready (readyState: ${audioElement.readyState}), waiting for metadata...`);

    // Create handler for when audio is ready
    const onReady = () => {
      console.log(`[Seek] Metadata loaded, now seeking to ${time.toFixed(2)}s`);
      isSeeking = true;
      audioElement.currentTime = time;
      if (audioElement.paused) {
        audioElement.play().catch(err => console.error('[Seek] Play failed:', err));
      }
      // Clear pending handler
      pendingSeekHandler = null;
      audioElement.removeEventListener('loadedmetadata', onReady);
      audioElement.removeEventListener('canplay', onReady);
    };

    // Store handler reference to allow cancellation
    pendingSeekHandler = onReady;
    audioElement.addEventListener('loadedmetadata', onReady);
    audioElement.addEventListener('canplay', onReady);
    return false;
  }
}

function renderWordTranscript() {
  const container = document.getElementById('word-transcript');
  if (!container) return;

  container.innerHTML = '';

  wordTimestamps.forEach((wordData, index) => {
    const wordSpan = document.createElement('span');
    wordSpan.className = 'word';
    wordSpan.textContent = wordData.word;
    wordSpan.dataset.index = index;
    wordSpan.dataset.start = wordData.start;
    wordSpan.dataset.end = wordData.end;

    // Add segment start marker for first word of each segment
    if (index > 0 && wordData.segmentIndex !== wordTimestamps[index - 1].segmentIndex) {
      wordSpan.classList.add('segment-start');
    }

    // Click to seek
    wordSpan.addEventListener('click', () => {
      // Check if audio is ready before seeking
      if (!audioElement) {
        console.warn('[Word Transcript Click] No audio element');
        showTemporaryMessage('⏸ Audio player not initialized');
        return;
      }

      if (audioElement.readyState < 1) {
        console.warn('[Word Transcript Click] Audio not ready yet');
        showTemporaryMessage('⏳ Audio loading... please wait');
        return;
      }

      const startTime = parseFloat(wordSpan.dataset.start);
      console.log(`[Word Transcript Click] Word: "${wordSpan.textContent}", dataset.start: "${wordSpan.dataset.start}", parsed: ${startTime}`);
      if (!isNaN(startTime) && startTime >= 0) {
        console.log(`[Word Transcript Click] Seeking to ${startTime.toFixed(2)}s for word: "${wordSpan.textContent}"`);
        seekToTime(startTime, wordSpan.textContent);
      } else {
        console.warn(`[Word Transcript Click] Invalid timestamp for word: "${wordSpan.textContent}"`, wordSpan.dataset.start);
      }
    });

    container.appendChild(wordSpan);
    container.appendChild(document.createTextNode(' '));
  });
}

function togglePlayPause() {
  if (!audioElement) return;

  if (audioElement.paused) {
    audioElement.play();
  } else {
    audioElement.pause();
  }
}

function updatePlayButton() {
  const playIcon = document.getElementById('play-icon');
  if (!playIcon || !audioElement) return;

  playIcon.textContent = audioElement.paused ? '▶' : '⏸';
}

function handleAudioTimeUpdate() {
  // Skip updates if dragging progress bar or manually seeking
  if (!audioElement || isProgressBarDragging || isSeeking) return;

  const currentTime = audioElement.currentTime;
  const duration = audioElement.duration;

  // Update progress bar
  if (duration > 0) {
    const progressPercent = (currentTime / duration) * 100;
    const progressFill = document.getElementById('audio-progress-fill');
    const progressHandle = document.getElementById('audio-progress-handle');

    if (progressFill) {
      progressFill.style.width = progressPercent + '%';
    }
    if (progressHandle) {
      progressHandle.style.left = progressPercent + '%';
    }
  }

  // Update current time display
  updateCurrentTime(currentTime);

  // Highlight current word
  highlightCurrentWord(currentTime);
}

function highlightCurrentWord(currentTime) {
  if (wordTimestamps.length === 0) return;

  // Apply perceptual lookahead for better sync feel
  const adjustedTime = currentTime + (LOOKAHEAD_MS / 1000);

  // Find the active word using optimized search
  let activeWordIndex = findActiveWord(adjustedTime);

  // If no exact match, find closest word within tolerance
  if (activeWordIndex === -1) {
    activeWordIndex = findClosestWord(adjustedTime);
  }

  // Only update if the active word changed (performance optimization)
  if (activeWordIndex === lastActiveWordIndex) return;
  lastActiveWordIndex = activeWordIndex;

  // Calculate upcoming word indices for preview
  const upcomingIndices = [];
  for (let i = 1; i <= SHOW_UPCOMING_WORDS; i++) {
    if (activeWordIndex + i < wordTimestamps.length) {
      upcomingIndices.push(activeWordIndex + i);
    }
  }

  // Update word highlighting with context
  const wordElements = document.querySelectorAll('.word-transcript .word');
  wordElements.forEach((wordEl, index) => {
    // Remove all classes
    wordEl.classList.remove('active', 'upcoming');

    if (index === activeWordIndex) {
      // Highlight active word
      wordEl.classList.add('active');
      // Auto-scroll to keep active word visible
      wordEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    } else if (upcomingIndices.includes(index)) {
      // Preview upcoming words
      wordEl.classList.add('upcoming');
    }
  });

  // Also highlight words in the editor panels (bidirectional sync)
  highlightEditorWords(activeWordIndex);
}

function highlightEditorWords(activeWordIndex) {
  // Highlight in original editor
  const originalWords = document.querySelectorAll('#original-text-editor .editor-word');
  originalWords.forEach((wordEl, index) => {
    if (index === activeWordIndex) {
      wordEl.classList.add('editor-active');
      // Auto-scroll to keep visible
      wordEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    } else {
      wordEl.classList.remove('editor-active');
    }
  });

  // Highlight in corrected editor (if index matches)
  const correctedWords = document.querySelectorAll('#corrected-text-editor .editor-word');
  if (activeWordIndex < correctedWords.length) {
    correctedWords.forEach((wordEl, index) => {
      if (index === activeWordIndex) {
        wordEl.classList.add('editor-active');
        // Auto-scroll to keep visible
        wordEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      } else {
        wordEl.classList.remove('editor-active');
      }
    });
  }
}

// Binary search to find word containing the given time
function findActiveWord(time) {
  let left = 0;
  let right = wordTimestamps.length - 1;

  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const word = wordTimestamps[mid];

    // Calculate tolerance based on confidence score
    const tolerance = word.confidence >= MIN_CONFIDENCE
      ? TIMING_TOLERANCE_MS / 1000
      : (TIMING_TOLERANCE_MS * 1.5) / 1000; // Wider tolerance for low confidence

    const startWithTolerance = word.start - tolerance;
    const endWithTolerance = word.end + tolerance;

    if (time >= startWithTolerance && time < endWithTolerance) {
      return mid; // Found matching word
    } else if (time < startWithTolerance) {
      right = mid - 1;
    } else {
      left = mid + 1;
    }
  }

  return -1; // No word found within tolerance
}

// Find closest word when no exact match (fallback for gaps)
function findClosestWord(time) {
  if (wordTimestamps.length === 0) return -1;

  let closestIndex = 0;
  let minDistance = Math.abs(time - wordTimestamps[0].start);

  for (let i = 1; i < wordTimestamps.length; i++) {
    const distance = Math.abs(time - wordTimestamps[i].start);
    if (distance < minDistance) {
      minDistance = distance;
      closestIndex = i;
    }
  }

  // Only return if reasonably close (within 1 second)
  return minDistance < 1.0 ? closestIndex : -1;
}

function updateCurrentTime(seconds) {
  const timeDisplay = document.getElementById('current-time');
  if (timeDisplay) {
    timeDisplay.textContent = formatTime(seconds);
  }
}

function updateTotalTime() {
  if (!audioElement) return;

  const timeDisplay = document.getElementById('total-time');
  if (timeDisplay) {
    timeDisplay.textContent = formatTime(audioElement.duration);
  }
}

function handleAudioEnded() {
  updatePlayButton();
  // Reset to beginning
  if (audioElement) {
    audioElement.currentTime = 0;
  }
}

function handleSeeking() {
  // Called when seek operation starts
  isSeeking = true;
}

function handleSeeked() {
  // Called when seek operation completes
  isSeeking = false;

  // Force an immediate update of UI with the new position
  if (audioElement) {
    const currentTime = audioElement.currentTime;
    const duration = audioElement.duration;

    // Update progress bar
    if (duration > 0) {
      const progressPercent = (currentTime / duration) * 100;
      const progressFill = document.getElementById('audio-progress-fill');
      const progressHandle = document.getElementById('audio-progress-handle');

      if (progressFill) {
        progressFill.style.width = progressPercent + '%';
      }
      if (progressHandle) {
        progressHandle.style.left = progressPercent + '%';
      }
    }

    updateCurrentTime(currentTime);
    highlightCurrentWord(currentTime);
  }
}

function handleProgressBarClick(event) {
  if (!audioElement) return;

  const progressBar = event.currentTarget;
  const rect = progressBar.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const percentage = clickX / rect.width;
  const newTime = percentage * audioElement.duration;

  isSeeking = true;
  audioElement.currentTime = newTime;
}

function startProgressDrag(event) {
  event.preventDefault();
  isProgressBarDragging = true;
  isSeeking = true;
}

function handleProgressDrag(event) {
  if (!isProgressBarDragging || !audioElement) return;

  const progressBar = document.querySelector('.audio-progress-bar');
  if (!progressBar) return;

  const rect = progressBar.getBoundingClientRect();
  const dragX = Math.max(0, Math.min(event.clientX - rect.left, rect.width));
  const percentage = dragX / rect.width;
  const newTime = percentage * audioElement.duration;

  // Update visuals immediately
  const progressPercent = percentage * 100;
  const progressFill = document.getElementById('audio-progress-fill');
  const progressHandle = document.getElementById('audio-progress-handle');

  if (progressFill) {
    progressFill.style.width = progressPercent + '%';
  }
  if (progressHandle) {
    progressHandle.style.left = progressPercent + '%';
  }

  updateCurrentTime(newTime);
}

function stopProgressDrag() {
  if (!isProgressBarDragging) return;

  isProgressBarDragging = false;

  // Set the actual audio time
  if (audioElement) {
    const progressBar = document.querySelector('.audio-progress-bar');
    const progressHandle = document.getElementById('audio-progress-handle');

    if (progressBar && progressHandle) {
      const handleLeft = parseFloat(progressHandle.style.left) || 0;
      const newTime = (handleLeft / 100) * audioElement.duration;
      audioElement.currentTime = newTime;
    }
  }
}

function formatTime(seconds) {
  if (isNaN(seconds) || seconds === Infinity) {
    return '0:00';
  }

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

async function autoCorrectText() {
  const correctedTextArea = document.getElementById('corrected-text');
  const originalText = correctedTextArea.value;

  if (!originalText || !originalText.trim()) {
    window.electron.showError('No Text', 'There is no text to correct');
    return;
  }

  try {
    // Save the BEFORE state for comparison
    const textBeforeCorrection = originalText;

    // Get correction settings from UI FIRST (needed for loading state)
    const level = 'standard';  // Can add a dropdown for this
    const useMlCheckbox = document.getElementById('use-ml-correction');
    const useML = useMlCheckbox ? useMlCheckbox.checked : false;

    console.log(`[Auto-Correct] Using ML mode: ${useML}`);

    // Show loading state
    const autoCorrectBtn = document.getElementById('auto-correct-btn');
    const originalBtnText = autoCorrectBtn.textContent;
    autoCorrectBtn.disabled = true;

    // Different message for ML mode (first time may take longer for model download)
    if (useML) {
      autoCorrectBtn.textContent = 'Loading ML Model...';
    } else {
      autoCorrectBtn.textContent = 'Correcting...';
    }

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
      // Update textarea
      correctedTextArea.value = result.corrected_text;

      // Re-render the word-level editor to show the corrected text visually
      renderCorrectedTranscriptEditor(result.corrected_text);

      // Highlight only the changes made by auto-correct
      // By showing inline what changed in the corrected text itself
      highlightAutoCorrectChanges(textBeforeCorrection, result.corrected_text);

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
// Word Correction System
// ============================================================================

function setupWordCorrectionHandlers() {
  // Modal handlers
  document.getElementById('close-modal-btn').addEventListener('click', closeWordEditorModal);
  document.getElementById('cancel-modal-btn').addEventListener('click', closeWordEditorModal);
  document.getElementById('apply-correction-btn').addEventListener('click', applyWordCorrection);
  document.getElementById('delete-word-btn').addEventListener('click', deleteSelectedWord);
  document.getElementById('split-word-btn').addEventListener('click', splitSelectedWord);

  // Modal overlay click to close
  document.querySelector('.modal-overlay').addEventListener('click', closeWordEditorModal);

  // Context menu handlers
  document.getElementById('context-edit').addEventListener('click', () => {
    hideContextMenu();
    openWordEditorModal();
  });
  document.getElementById('context-delete').addEventListener('click', () => {
    hideContextMenu();
    deleteSelectedWord();
  });
  document.getElementById('context-split').addEventListener('click', () => {
    hideContextMenu();
    splitSelectedWord();
  });
  document.getElementById('context-merge').addEventListener('click', () => {
    hideContextMenu();
    mergeWithNextWord();
  });
  document.getElementById('context-mark-correct').addEventListener('click', () => {
    hideContextMenu();
    markWordAsReviewed();
  });

  // Global keyboard shortcuts
  document.addEventListener('keydown', handleGlobalKeyboard);

  // Hide context menu on click outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.context-menu')) {
      hideContextMenu();
    }
  });
}

function handleGlobalKeyboard(event) {
  // Only handle shortcuts when corrected editor is visible
  const correctedEditor = document.getElementById('corrected-text-editor');
  if (!correctedEditor || correctedEditor.offsetParent === null) return;

  // Ctrl+Z - Undo
  if (event.ctrlKey && event.key === 'z' && !event.shiftKey) {
    event.preventDefault();
    undo();
  }

  // Ctrl+Shift+Z or Ctrl+Y - Redo
  if ((event.ctrlKey && event.shiftKey && event.key === 'Z') || (event.ctrlKey && event.key === 'y')) {
    event.preventDefault();
    redo();
  }

  // Delete/Backspace - Delete selected word (if a word is selected)
  if ((event.key === 'Delete' || event.key === 'Backspace') && selectedWordElement && !event.target.matches('input, textarea')) {
    event.preventDefault();
    deleteSelectedWord();
  }

  // Escape - Deselect word / Close modal
  if (event.key === 'Escape') {
    const modal = document.getElementById('word-editor-modal');
    if (modal.style.display !== 'none') {
      closeWordEditorModal();
    } else {
      deselectWord();
    }
  }

  // Enter - Open modal for selected word
  if (event.key === 'Enter' && selectedWordElement && !event.target.matches('input, textarea')) {
    event.preventDefault();
    openWordEditorModal();
  }
}

// Word Selection System
function selectWord(wordElement, index) {
  // Deselect previous word
  if (selectedWordElement) {
    selectedWordElement.classList.remove('word-selected');
  }

  // Select new word
  selectedWordElement = wordElement;
  selectedWordIndex = index;
  wordElement.classList.add('word-selected');
}

function deselectWord() {
  if (selectedWordElement) {
    selectedWordElement.classList.remove('word-selected');
    selectedWordElement = null;
    selectedWordIndex = -1;
  }
}

// Modal Functions
function openWordEditorModal() {
  if (!selectedWordElement) return;

  const modal = document.getElementById('word-editor-modal');
  const input = document.getElementById('modal-word-input');
  const originalWord = document.getElementById('modal-original-word');
  const wordTime = document.getElementById('modal-word-time');
  const wordConfidence = document.getElementById('modal-word-confidence');

  // Get word data
  const wordText = selectedWordElement.textContent.trim();
  const wordStart = selectedWordElement.dataset.start;
  const wordEnd = selectedWordElement.dataset.end;
  const index = parseInt(selectedWordElement.dataset.index);

  // Fill modal with word info
  originalWord.textContent = wordText;
  input.value = wordText;

  // Get timing and confidence from original word data
  if (index < wordTimestamps.length) {
    const wordData = wordTimestamps[index];
    wordTime.textContent = `${formatTime(wordData.start)} - ${formatTime(wordData.end)}`;
    wordConfidence.textContent = `${(wordData.confidence * 100).toFixed(0)}%`;
  } else if (wordStart && wordEnd) {
    wordTime.textContent = `${formatTime(parseFloat(wordStart))} - ${formatTime(parseFloat(wordEnd))}`;
    wordConfidence.textContent = 'N/A';
  } else {
    wordTime.textContent = 'N/A';
    wordConfidence.textContent = 'N/A';
  }

  // Show modal
  modal.style.display = 'flex';

  // Focus input and select text
  setTimeout(() => {
    input.focus();
    input.select();
  }, 100);

  // Handle Enter key in input
  input.onkeydown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      applyWordCorrection();
    } else if (e.key === 'Escape') {
      closeWordEditorModal();
    }
  };
}

function closeWordEditorModal() {
  const modal = document.getElementById('word-editor-modal');
  modal.style.display = 'none';
}

function applyWordCorrection() {
  if (!selectedWordElement) return;

  const input = document.getElementById('modal-word-input');
  const newText = input.value.trim();

  if (!newText) {
    window.electron.showError('Invalid Input', 'Word cannot be empty. Use Delete button to remove the word.');
    return;
  }

  // Save state for undo
  saveState();

  // Update word
  selectedWordElement.textContent = newText;

  // Update diff and textarea
  updateCorrectedTextarea();
  updateDiffHighlighting();

  // Close modal
  closeWordEditorModal();
}

// Word Operations
function deleteSelectedWord() {
  if (!selectedWordElement) return;

  // Save state for undo
  saveState();

  // Remove word and its following space
  const nextNode = selectedWordElement.nextSibling;
  if (nextNode && nextNode.nodeType === Node.TEXT_NODE) {
    nextNode.remove();
  }
  selectedWordElement.remove();

  // Clear selection
  selectedWordElement = null;
  selectedWordIndex = -1;

  // Update
  updateCorrectedTextarea();
  updateDiffHighlighting();

  // Close modal if open
  closeWordEditorModal();
}

function splitSelectedWord() {
  if (!selectedWordElement) return;

  const wordText = selectedWordElement.textContent.trim();

  // Split word feature temporarily disabled in Electron (prompt() not supported)
  // As a workaround, split at the middle of the word
  const splitPos = Math.floor(wordText.length / 2);

  if (wordText.length < 2) {
    window.electron.showError('Cannot Split', 'Word is too short to split.');
    return;
  }

  // Save state for undo
  saveState();

  // Split the word
  const firstPart = wordText.substring(0, splitPos);
  const secondPart = wordText.substring(splitPos);

  // Create new word spans
  const container = selectedWordElement.parentElement;
  const index = parseInt(selectedWordElement.dataset.index);

  // First word
  selectedWordElement.textContent = firstPart;

  // Second word
  const secondWord = document.createElement('span');
  secondWord.className = 'editor-word';
  secondWord.textContent = secondPart;
  secondWord.dataset.index = index + 1;

  // Insert after first word
  const spaceNode = document.createTextNode(' ');
  selectedWordElement.after(spaceNode);
  spaceNode.after(secondWord);

  // Update indices of following words
  let currentIndex = index + 2;
  let nextSibling = secondWord.nextSibling;
  while (nextSibling) {
    if (nextSibling.classList && nextSibling.classList.contains('editor-word')) {
      nextSibling.dataset.index = currentIndex++;
    }
    nextSibling = nextSibling.nextSibling;
  }

  // Attach event handlers to new word
  attachWordHandlers(secondWord, index + 1);

  // Update
  updateCorrectedTextarea();
  updateDiffHighlighting();

  // Close modal
  closeWordEditorModal();
}

function mergeWithNextWord() {
  if (!selectedWordElement) return;

  // Find next word element
  let nextWord = selectedWordElement.nextSibling;
  while (nextWord && !nextWord.classList?.contains('editor-word')) {
    nextWord = nextWord.nextSibling;
  }

  if (!nextWord) {
    window.electron.showError('Cannot Merge', 'No next word to merge with.');
    return;
  }

  // Save state for undo
  saveState();

  // Merge words
  const mergedText = selectedWordElement.textContent.trim() + nextWord.textContent.trim();
  selectedWordElement.textContent = mergedText;

  // Remove space and next word
  let nodeToRemove = selectedWordElement.nextSibling;
  while (nodeToRemove && nodeToRemove !== nextWord) {
    const next = nodeToRemove.nextSibling;
    nodeToRemove.remove();
    nodeToRemove = next;
  }
  nextWord.remove();

  // Update indices
  let currentIndex = parseInt(selectedWordElement.dataset.index) + 1;
  let nextSibling = selectedWordElement.nextSibling;
  while (nextSibling) {
    if (nextSibling.classList && nextSibling.classList.contains('editor-word')) {
      nextSibling.dataset.index = currentIndex++;
    }
    nextSibling = nextSibling.nextSibling;
  }

  // Update
  updateCorrectedTextarea();
  updateDiffHighlighting();
}

function markWordAsReviewed() {
  if (!selectedWordElement) return;

  selectedWordElement.classList.toggle('word-reviewed');
  deselectWord();
}

// Context Menu
function showContextMenu(event, wordElement, index) {
  event.preventDefault();
  event.stopPropagation();

  // Select the word
  selectWord(wordElement, index);

  // Position and show context menu
  const menu = document.getElementById('word-context-menu');
  menu.style.display = 'block';
  menu.style.left = event.pageX + 'px';
  menu.style.top = event.pageY + 'px';

  // Ensure menu stays within viewport
  setTimeout(() => {
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
      menu.style.left = (event.pageX - rect.width) + 'px';
    }
    if (rect.bottom > window.innerHeight) {
      menu.style.top = (event.pageY - rect.height) + 'px';
    }
  }, 0);
}

function hideContextMenu() {
  const menu = document.getElementById('word-context-menu');
  menu.style.display = 'none';
}

// Edit History (Undo/Redo)
function saveState() {
  const container = document.getElementById('corrected-text-editor');
  if (!container) return;

  // Save current state
  const state = {
    html: container.innerHTML,
    selectedIndex: selectedWordIndex
  };

  // Remove any states after current position (when editing after undo)
  editHistory = editHistory.slice(0, historyIndex + 1);

  // Add new state
  editHistory.push(state);

  // Limit history size
  if (editHistory.length > MAX_HISTORY) {
    editHistory.shift();
  } else {
    historyIndex++;
  }
}

function undo() {
  if (historyIndex <= 0) {
    console.log('Nothing to undo');
    return;
  }

  historyIndex--;
  restoreState(editHistory[historyIndex]);
}

function redo() {
  if (historyIndex >= editHistory.length - 1) {
    console.log('Nothing to redo');
    return;
  }

  historyIndex++;
  restoreState(editHistory[historyIndex]);
}

function restoreState(state) {
  const container = document.getElementById('corrected-text-editor');
  if (!container) return;

  // Restore HTML
  container.innerHTML = state.html;

  // Reattach event handlers to all words
  const words = container.querySelectorAll('.editor-word');
  words.forEach((word, index) => {
    attachWordHandlers(word, index);
  });

  // Restore selection if applicable
  if (state.selectedIndex >= 0 && state.selectedIndex < words.length) {
    selectWord(words[state.selectedIndex], state.selectedIndex);
  } else {
    deselectWord();
  }

  // Update
  updateCorrectedTextarea();
  updateDiffHighlighting();
}

// Attach event handlers to word elements
function attachWordHandlers(wordElement, index) {
  // Single click - select word
  wordElement.addEventListener('click', (e) => {
    // Only select if not currently editing (contenteditable)
    if (document.activeElement !== wordElement) {
      e.stopPropagation();
      // Select the word for editing
      selectWord(wordElement, index);
    }
  });

  // Double click - open modal
  wordElement.addEventListener('dblclick', (e) => {
    e.preventDefault();
    e.stopPropagation();
    selectWord(wordElement, index);
    openWordEditorModal();
  });

  // Right click - context menu
  wordElement.addEventListener('contextmenu', (e) => {
    showContextMenu(e, wordElement, index);
  });

  // Input event - update on edit
  wordElement.addEventListener('input', () => {
    updateCorrectedTextarea();
    updateDiffHighlighting();
  });

  // Focus - select word
  wordElement.addEventListener('focus', () => {
    selectWord(wordElement, index);
  });
}

// ============================================================================
// Settings
// ============================================================================

function setupSettingsHandlers() {
  document.getElementById('check-backend-btn').addEventListener('click', () => checkBackendConnection());

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

// ============================================================================
// Utility Functions
// ============================================================================

function showTemporaryMessage(message, duration = 2000) {
  /**
   * Show a temporary message overlay to the user
   * Useful for quick feedback without modal dialogs
   */
  const messageDiv = document.createElement('div');
  messageDiv.className = 'temporary-message';
  messageDiv.textContent = message;
  messageDiv.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #3498db;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    z-index: 10000;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    font-size: 14px;
    font-weight: 500;
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
  `;

  document.body.appendChild(messageDiv);

  // Fade in
  requestAnimationFrame(() => {
    messageDiv.style.opacity = '1';
  });

  // Fade out and remove
  setTimeout(() => {
    messageDiv.style.opacity = '0';
    setTimeout(() => messageDiv.remove(), 300);
  }, duration);
}

// Export for debugging
window.puloxDebug = {
  checkBackendConnection,
  loadTranscripts,
  currentFile,
  currentTranscriptId,
  transcripts
};
