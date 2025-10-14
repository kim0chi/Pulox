# UCLM High School Data Collection Plan

## Overview
Systematic collection of English-Tagalog classroom lecture recordings for the Pulox system.

## Phase 1: Preparation (Week 1)

### 1. Administrative Requirements
- [ ] Draft formal request letter to UCLM administration
- [ ] Prepare project presentation for faculty
- [ ] Create consent forms for:
  - Teachers (recording permission)
  - Students (voice in recordings)
  - Parents/guardians (for minors)
- [ ] Establish data privacy protocols

### 2. Technical Setup
- [ ] Recording equipment checklist:
  - Primary: Zoom H4n/H6 recorder or similar
  - Backup: High-quality lapel microphone + smartphone
  - Audio format: 44.1kHz, 16-bit WAV (convert to 16kHz for Whisper)
- [ ] Test recording setup in actual classroom
- [ ] Create recording protocol document

### 3. Subject Selection Criteria
Target diverse subjects with natural code-switching:
- **Science** (Biology, Chemistry, Physics) - technical terms in English
- **Mathematics** - mixed terminology
- **Filipino/Araling Panlipunan** - primarily Tagalog
- **English Literature** - primarily English
- **Computer Science** - heavy English technical terms

## Phase 2: Data Collection (Weeks 2-4)

### Recording Schedule Template

| Week | Subject | Teacher | Duration | Language Mix (Est.) |
|------|---------|---------|----------|-------------------|
| 1 | Mathematics | TBD | 60 min | 60% EN, 40% TL |
| 1 | Biology | TBD | 45 min | 70% EN, 30% TL |
| 1 | Filipino | TBD | 45 min | 20% EN, 80% TL |
| 2 | Physics | TBD | 60 min | 65% EN, 35% TL |
| 2 | History | TBD | 45 min | 40% EN, 60% TL |

### Target Metrics
- **Minimum**: 20 hours total recording
- **Optimal**: 40 hours total recording
- **Distribution**: 
  - 30% primarily English
  - 30% primarily Tagalog
  - 40% balanced code-switching

### Recording Protocol

1. **Pre-Recording** (5 min)
   - Test audio levels
   - Note: Date, subject, topic, teacher ID
   - Brief teacher on natural delivery

2. **During Recording**
   - Monitor audio quality
   - Take timestamped notes of:
     - Topic transitions
     - Technical difficulties
     - Notable code-switching moments
     - Student interactions

3. **Post-Recording** (10 min)
   - Save with naming convention: `YYYYMMDD_Subject_Teacher_Topic.wav`
   - Create metadata file
   - Quick quality check
   - Backup to cloud storage

## Phase 3: Initial Annotation (Weeks 3-5)

### Annotation Team
- **Team Size**: 3-5 annotators
- **Requirements**: 
  - Fluent in English and Tagalog
  - Familiar with academic terminology
  - Basic training in transcription

### Annotation Guidelines

#### Level 1: Basic Transcription
- Transcribe exactly what is spoken
- Mark unclear segments with [unclear]
- Note code-switching with tags: <EN>, <TL>, <MIXED>

#### Level 2: Error Correction
- Fix obvious ASR errors
- Correct grammar while preserving meaning
- Add proper punctuation
- Maintain speaker's language choice

#### Level 3: Summary Creation
- Extract key concepts per 5-minute segment
- Create bullet-point summaries
- Highlight important formulas/definitions
- Note homework/exam announcements

### Quality Control
- Each transcript reviewed by second annotator
- 10% random sampling for third review
- Inter-annotator agreement target: >85%

## Phase 4: Dataset Organization

### File Structure
```
data/
├── raw_audio/
│   ├── week1/
│   │   ├── 20240115_Math_TeacherA_Algebra.wav
│   │   └── 20240115_Math_TeacherA_Algebra.json (metadata)
│   └── week2/
├── transcripts/
│   ├── raw_asr/
│   ├── corrected/
│   └── summaries/
└── metadata/
    ├── speakers.csv
    ├── recording_log.csv
    └── annotation_status.csv
```

### Metadata Schema
```json
{
  "recording_id": "20240115_Math_TeacherA_Algebra",
  "date": "2024-01-15",
  "subject": "Mathematics",
  "topic": "Linear Algebra Introduction",
  "teacher_id": "T001",
  "duration_seconds": 3600,
  "language_distribution": {
    "english": 0.65,
    "tagalog": 0.30,
    "mixed": 0.05
  },
  "audio_quality": "good",
  "transcription_status": "completed",
  "correction_status": "in_progress",
  "summary_status": "pending",
  "notes": "Some background noise at 15:30-16:00"
}
```

## Phase 5: Synthetic Data Augmentation

If natural data is limited, create synthetic data:

1. **Text-to-Speech Generation**
   - Use Google TTS for English segments
   - Use Filipino TTS for Tagalog segments
   - Mix at realistic ratios

2. **Noise Addition**
   - Classroom ambience
   - Student chatter
   - Air conditioning hum
   - Marker on whiteboard sounds

3. **Speed Perturbation**
   - 0.9x to 1.1x speed variations
   - Maintains natural prosody

## Deliverables Checklist

### Week 1
- [ ] Approved consent forms
- [ ] Recording equipment ready
- [ ] Test recordings completed

### Week 2-3
- [ ] 10+ hours of recordings
- [ ] Initial ASR transcriptions
- [ ] Annotation team trained

### Week 4-5
- [ ] 20+ hours total recordings
- [ ] 50% transcripts corrected
- [ ] Initial summaries created
- [ ] Dataset documentation complete

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Low teacher participation | Incentivize with project acknowledgment, offer transcripts for their use |
| Poor audio quality | Always use backup recording, test equipment daily |
| Slow annotation | Start with partial annotation, use active learning |
| Limited code-switching | Specifically request natural delivery, select appropriate subjects |
| Privacy concerns | Strict data handling protocol, anonymization options |

## Contact Template for UCLM

```
Subject: Research Collaboration Request - Pulox Transcription System

Dear [Administrator Name],

We are developing Pulox, an innovative system to automatically transcribe and summarize classroom lectures in mixed English-Tagalog settings. This project aims to benefit both teachers and students by providing accurate lecture notes and summaries.

We kindly request permission to record select classroom sessions for research purposes. All data will be handled with strict confidentiality, and the resulting system will be made available to UCLM High School.

Key Benefits for UCLM:
- Free access to the transcription system
- Automated lecture notes for students
- Teacher training on the technology
- Acknowledgment in all publications

We would appreciate the opportunity to present this project in detail at your convenience.

Sincerely,
[Your Name]
[Your Institution]
```