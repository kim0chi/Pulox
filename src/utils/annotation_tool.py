"""
Simple Annotation Tool for Creating ASR Correction Pairs
Streamlit-based interface for annotating transcripts
"""
import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
import difflib
from typing import Dict, List, Tuple
import soundfile as sf
import numpy as np
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Pulox Annotation Tool",
    page_icon="📝",
    layout="wide"
)

class AnnotationTool:
    """Main annotation tool class"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.transcripts_dir = self.data_dir / "transcripts"
        self.corrections_dir = self.data_dir / "corrections"
        self.annotations_file = self.data_dir / "annotations.json"
        
        # Create directories
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.corrections_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing annotations
        self.annotations = self.load_annotations()
    
    def load_annotations(self) -> Dict:
        """Load existing annotations from file"""
        if self.annotations_file.exists():
            with open(self.annotations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_annotations(self):
        """Save annotations to file"""
        with open(self.annotations_file, 'w', encoding='utf-8') as f:
            json.dump(self.annotations, f, ensure_ascii=False, indent=2)
    
    def get_transcript_files(self) -> List[str]:
        """Get list of transcript files"""
        files = []
        for ext in ['*.json', '*.txt']:
            files.extend(self.transcripts_dir.glob(ext))
        return sorted([f.name for f in files])
    
    def load_transcript(self, filename: str) -> str:
        """Load transcript from file"""
        filepath = self.transcripts_dir / filename
        
        if filename.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('text', '')
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
    
    def save_correction(self, filename: str, original: str, corrected: str, metadata: Dict):
        """Save correction pair"""
        correction_id = filename.replace('.json', '').replace('.txt', '')
        
        correction_data = {
            'id': correction_id,
            'timestamp': datetime.now().isoformat(),
            'original': original,
            'corrected': corrected,
            'metadata': metadata,
            'changes': self.calculate_changes(original, corrected)
        }
        
        # Save to corrections directory
        output_path = self.corrections_dir / f"{correction_id}_corrected.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(correction_data, f, ensure_ascii=False, indent=2)
        
        # Update annotations tracking
        self.annotations[correction_id] = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'annotator': metadata.get('annotator', 'unknown')
        }
        self.save_annotations()
        
        return output_path
    
    def calculate_changes(self, original: str, corrected: str) -> Dict:
        """Calculate statistics about changes made"""
        orig_words = original.split()
        corr_words = corrected.split()
        
        # Use difflib to find changes
        matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
        changes = {
            'word_changes': 0,
            'additions': 0,
            'deletions': 0,
            'similarity_ratio': matcher.ratio()
        }
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes['word_changes'] += max(i2 - i1, j2 - j1)
            elif tag == 'delete':
                changes['deletions'] += i2 - i1
            elif tag == 'insert':
                changes['additions'] += j2 - j1
        
        return changes


def render_annotation_interface():
    """Main Streamlit interface"""
    
    st.title("🎓 Pulox Transcript Annotation Tool")
    st.markdown("### Correct ASR transcripts for English-Tagalog lectures")
    
    # Initialize tool
    if 'tool' not in st.session_state:
        st.session_state.tool = AnnotationTool()
    
    tool = st.session_state.tool
    
    # Sidebar for file selection
    with st.sidebar:
        st.header("📁 File Selection")
        
        # Get available transcript files
        transcript_files = tool.get_transcript_files()
        
        if not transcript_files:
            st.warning("No transcript files found in data/transcripts/")
            st.info("Place your ASR output files in the data/transcripts/ directory")
            return
        
        selected_file = st.selectbox(
            "Select transcript file:",
            transcript_files,
            key="file_selector"
        )
        
        st.divider()
        
        # Annotator information
        st.header("👤 Annotator Info")
        annotator_name = st.text_input("Your name:", key="annotator")
        
        # Statistics
        st.divider()
        st.header("📊 Statistics")
        total_files = len(transcript_files)
        completed = len([a for a in tool.annotations.values() if a['status'] == 'completed'])
        st.metric("Total Files", total_files)
        st.metric("Completed", completed)
        st.progress(completed / total_files if total_files > 0 else 0)
    
    # Main annotation area
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Original ASR Transcript")
        original_text = tool.load_transcript(selected_file)
        
        # Display with line numbers
        lines = original_text.split('\n')
        numbered_text = '\n'.join([f"{i+1:3d}: {line}" for i, line in enumerate(lines)])
        st.text_area(
            "Original (Read-only):",
            value=numbered_text,
            height=400,
            disabled=True,
            key="original_display"
        )
        
        # Quick stats
        st.caption(f"Words: {len(original_text.split())}")
        st.caption(f"Characters: {len(original_text)}")
    
    with col2:
        st.subheader("✏️ Corrected Transcript")
        
        # Pre-fill with original if no correction exists
        correction_file = selected_file.replace('.json', '').replace('.txt', '')
        if correction_file in tool.annotations:
            st.info("✅ This file has been annotated")
            # Load existing correction
            correction_path = tool.corrections_dir / f"{correction_file}_corrected.json"
            if correction_path.exists():
                with open(correction_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    default_text = existing['corrected']
            else:
                default_text = original_text
        else:
            default_text = original_text
        
        corrected_text = st.text_area(
            "Edit here:",
            value=default_text,
            height=400,
            key="corrected_input",
            help="Correct errors, add punctuation, fix code-switching issues"
        )
        
        # Calculate changes in real-time
        if corrected_text != original_text:
            changes = tool.calculate_changes(original_text, corrected_text)
            col2_1, col2_2, col2_3 = st.columns(3)
            with col2_1:
                st.caption(f"Changes: {changes['word_changes']}")
            with col2_2:
                st.caption(f"Additions: {changes['additions']}")
            with col2_3:
                st.caption(f"Deletions: {changes['deletions']}")
    
    # Annotation guidelines
    with st.expander("📋 Annotation Guidelines", expanded=False):
        st.markdown("""
        ### Correction Guidelines:
        
        1. **Spelling & Grammar**
           - Fix obvious typos and grammatical errors
           - Preserve speaker's language choice (don't translate)
        
        2. **Punctuation**
           - Add periods, commas, question marks
           - Use proper capitalization
        
        3. **Code-Switching**
           - Keep natural language mixing
           - Fix ASR errors in both languages
           - Mark unclear segments with [unclear]
        
        4. **Technical Terms**
           - Ensure correct spelling of technical terms
           - Maintain consistency (e.g., "x squared" → "x²")
        
        5. **Do NOT:**
           - Change meaning or add information
           - Translate between languages
           - Remove filler words unless garbled
        """)
    
    # Language detection helpers
    st.divider()
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🔍 Detect Language Segments", use_container_width=True):
            # Simple language detection
            lines = corrected_text.split('\n')
            tagged_lines = []
            for line in lines:
                if line.strip():
                    # Simple heuristic - can be improved
                    tagalog_words = ['ang', 'ng', 'mga', 'sa', 'na', 'ay', 'at', 'po', 'ba']
                    word_list = line.lower().split()
                    tagalog_count = sum(1 for w in word_list if w in tagalog_words)
                    
                    if tagalog_count > len(word_list) * 0.3:
                        tagged_lines.append(f"[TL] {line}")
                    elif tagalog_count > 0:
                        tagged_lines.append(f"[MIX] {line}")
                    else:
                        tagged_lines.append(f"[EN] {line}")
                else:
                    tagged_lines.append(line)
            
            st.code('\n'.join(tagged_lines), language=None)
    
    with col4:
        if st.button("🔤 Check Spelling", use_container_width=True):
            st.info("Spell check coming soon! For now, review manually.")
    
    with col5:
        if st.button("📊 Show Diff", use_container_width=True):
            # Show detailed diff
            d = difflib.unified_diff(
                original_text.splitlines(),
                corrected_text.splitlines(),
                lineterm='',
                fromfile='Original',
                tofile='Corrected'
            )
            diff_text = '\n'.join(d)
            if diff_text:
                st.code(diff_text, language='diff')
            else:
                st.info("No changes detected")
    
    # Metadata section
    st.divider()
    with st.expander("📌 Additional Metadata", expanded=False):
        col6, col7 = st.columns(2)
        
        with col6:
            subject = st.selectbox(
                "Subject:",
                ["Mathematics", "Science", "English", "Filipino", "History", "Computer Science", "Other"],
                key="subject"
            )

            audio_quality = st.select_slider(
                "Audio Quality:",
                options=["Poor", "Fair", "Good", "Excellent"],
                value="Good",
                key="quality"
            )

        with col7:
            primary_language = st.selectbox(
                "Primary Language:",
                ["English", "Tagalog", "Mixed (Equal)", "Mixed (More English)", "Mixed (More Tagalog)"],
                key="language"
            )
            
            difficulty = st.select_slider(
                "Transcription Difficulty:",
                options=["Easy", "Moderate", "Challenging", "Very Difficult"],
                value="Moderate",
                key="difficulty"
            )
        
        notes = st.text_area(
            "Notes (optional):",
            placeholder="Any special observations about this transcript...",
            key="notes"
        )
    
    # Save buttons
    st.divider()
    col8, col9, col10 = st.columns([2, 1, 1])
    
    with col8:
        if st.button("💾 Save Correction", type="primary", use_container_width=True):
            if not annotator_name:
                st.error("Please enter your name in the sidebar!")
            elif corrected_text == original_text:
                st.warning("No changes made to the transcript. Please make corrections first.")
            else:
                # Compile metadata
                metadata = {
                    'annotator': annotator_name,
                    'subject': st.session_state.get('subject', 'Unknown'),
                    'audio_quality': st.session_state.get('quality', 'Unknown'),
                    'primary_language': st.session_state.get('language', 'Unknown'),
                    'difficulty': st.session_state.get('difficulty', 'Unknown'),
                    'notes': st.session_state.get('notes', '')
                }
                
                # Save correction
                output_path = tool.save_correction(
                    selected_file,
                    original_text,
                    corrected_text,
                    metadata
                )
                
                st.success(f"✅ Saved correction to {output_path}")
                st.balloons()
                
                # Show summary
                changes = tool.calculate_changes(original_text, corrected_text)
                st.info(f"""
                **Correction Summary:**
                - Total changes: {changes['word_changes']} words
                - Additions: {changes['additions']}
                - Deletions: {changes['deletions']}
                - Similarity: {changes['similarity_ratio']:.1%}
                """)
    
    with col9:
        if st.button("⏭️ Next File", use_container_width=True):
            # Find next unannotated file
            current_idx = transcript_files.index(selected_file)
            next_idx = (current_idx + 1) % len(transcript_files)
            st.session_state.file_selector = transcript_files[next_idx]
            st.rerun()
    
    with col10:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.corrected_input = original_text
            st.rerun()
    
    # Export functionality
    st.divider()
    with st.expander("📤 Export Annotations", expanded=False):
        if st.button("Export All Corrections as CSV"):
            # Compile all corrections into DataFrame
            corrections_data = []
            for file in tool.corrections_dir.glob("*_corrected.json"):
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    corrections_data.append({
                        'id': data['id'],
                        'timestamp': data['timestamp'],
                        'annotator': data['metadata'].get('annotator', 'Unknown'),
                        'changes': data['changes']['word_changes'],
                        'similarity': data['changes']['similarity_ratio']
                    })
            
            if corrections_data:
                df = pd.DataFrame(corrections_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No corrections to export yet")


# Run the app
if __name__ == "__main__":
    render_annotation_interface()