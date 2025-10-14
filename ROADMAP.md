# Pulox Roadmap

Strategic plan for developing Pulox into a production-ready system for English-Tagalog classroom lecture transcription, correction, and summarization.

**Last Updated:** October 7, 2025
**Current Version:** 0.1.0 Alpha
**Target Version:** 1.0.0 (Production)

---

## Vision & Goals

### Primary Goal
Create a robust, accurate, and easy-to-use system that helps Philippine educators and students by automatically transcribing, correcting, and summarizing mixed English-Tagalog classroom lectures.

### Success Criteria
- ✅ **Transcription WER** < 15% for classroom audio
- ✅ **Correction Improvement** 30%+ reduction in errors
- ✅ **Summary Quality** ROUGE-L > 0.4
- ✅ **User Adoption** Deploy to at least 3 classrooms at UCLM
- ✅ **Processing Speed** < 2 minutes per 1-hour lecture
- ✅ **Usability** Non-technical teachers can use without training

---

## Release Timeline

### ✅ Phase 0: Foundation (Completed - Oct 2025)
**Status:** Complete
**Duration:** 1 week

#### Deliverables
- [x] Project structure and setup
- [x] Whisper ASR integration
- [x] FastAPI backend
- [x] Electron desktop application
- [x] Basic annotation tools
- [x] Installation scripts
- [x] Initial documentation

#### Achievements
- Functional transcription pipeline
- Desktop app with professional UI
- API with 8+ endpoints
- Comprehensive setup guides

---

### 🔄 Phase 1: Core ML Components (In Progress - Oct-Nov 2025)
**Status:** 20% Complete
**Duration:** 3 weeks
**Target:** End of November 2025

#### Week 1: Correction Module (Oct 14-20)
- [ ] Create `src/correction/error_corrector.py`
  - [ ] Rule-based corrections for common Filipino-English errors
  - [ ] MT5-small integration
  - [ ] Text normalization utilities
- [ ] Create `src/correction/rules.py`
  - [ ] Define common ASR error patterns
  - [ ] Filipino word dictionary
  - [ ] English-Tagalog cognates handling
- [ ] Add `/correct` API endpoint
- [ ] Basic unit tests for correction

#### Week 2: Summarization Module (Oct 21-27)
- [ ] Create `src/summarization/extractive.py`
  - [ ] TF-IDF sentence ranking
  - [ ] TextRank implementation
  - [ ] Key phrase extraction
- [ ] Create `src/summarization/abstractive.py`
  - [ ] MT5-small for abstractive summarization
  - [ ] Bilingual summary generation
- [ ] Create `src/summarization/hybrid.py`
  - [ ] Combine extractive + abstractive
  - [ ] Configurable summary length
- [ ] Add `/summarize` API endpoint
- [ ] Basic unit tests for summarization

#### Week 3: Evaluation & Integration (Oct 28 - Nov 3)
- [ ] Create `src/evaluation/metrics.py`
  - [ ] WER, CER, MER calculation
  - [ ] ROUGE scores (1, 2, L)
  - [ ] BERTScore implementation
- [ ] Create `src/evaluation/benchmarks.py`
  - [ ] Model comparison tools
  - [ ] Performance tracking
- [ ] Integrate correction into Electron UI
- [ ] Integrate summarization into Electron UI
- [ ] Create first Jupyter notebook for experimentation

**Deliverables:**
- Functional correction module
- Functional summarization module
- Complete evaluation framework
- Updated desktop app with new features

---

### 📊 Phase 2: Data Collection & Annotation (Nov-Dec 2025)
**Status:** Not Started
**Duration:** 4-6 weeks
**Target:** End of December 2025

#### Week 1: Administrative Preparation (Nov 4-10)
- [ ] Draft formal request letter to UCLM administration
- [ ] Prepare project presentation for faculty
- [ ] Create consent forms:
  - [ ] Teacher recording permission
  - [ ] Student voice in recordings
  - [ ] Parent/guardian consent for minors
- [ ] Establish data privacy protocols
- [ ] Get IRB approval (if required)

#### Week 2: Technical Preparation (Nov 11-17)
- [ ] Acquire recording equipment
  - [ ] Test primary recorder (Zoom H4n/H6 or similar)
  - [ ] Setup backup recording (lapel mic + smartphone)
- [ ] Test recording setup in actual classroom
- [ ] Create recording protocol document
- [ ] Train recording assistants
- [ ] Setup cloud backup for recordings

#### Weeks 3-6: Active Recording (Nov 18 - Dec 22)
- [ ] Record at least 20 hours of classroom lectures:
  - [ ] 6 hours Mathematics (English-Tagalog mix)
  - [ ] 5 hours Science (primarily English)
  - [ ] 4 hours Filipino subject (primarily Tagalog)
  - [ ] 3 hours Computer Science (heavy English technical terms)
  - [ ] 2 hours History (balanced code-switching)
- [ ] Daily quality checks and backups
- [ ] Preliminary transcriptions with Whisper
- [ ] Begin manual correction annotations

#### Parallel: Annotation (Starting Week 3)
- [ ] Recruit 3-5 annotators
- [ ] Conduct annotator training session
- [ ] Setup annotation guidelines
- [ ] Begin correcting ASR transcripts
- [ ] Begin creating summaries
- [ ] Weekly annotation review meetings
- [ ] Target: 50%+ of collected data annotated by end of phase

**Deliverables:**
- 20-40 hours of classroom audio recordings
- Manual transcriptions of all recordings
- 10+ hours of corrected transcript pairs
- 5+ hours of transcript-summary pairs
- Annotation quality report

---

### 🧠 Phase 3: Model Training & Optimization (Jan 2026)
**Status:** Not Started
**Duration:** 3 weeks
**Target:** End of January 2026

#### Week 1: Data Preparation (Jan 6-12)
- [ ] Clean and validate all collected data
- [ ] Create train/validation/test splits (70/15/15)
- [ ] Data augmentation:
  - [ ] Speed perturbation (0.9x, 1.0x, 1.1x)
  - [ ] Background noise addition
  - [ ] Synthetic data generation with TTS
- [ ] Create data loaders and preprocessing pipelines
- [ ] Setup training infrastructure (GPU server or cloud)

#### Week 2: Model Training (Jan 13-19)
- [ ] Fine-tune Whisper on Filipino-English data
  - [ ] Experiment with base and small models
  - [ ] Optimize for code-switching
  - [ ] Evaluate on validation set
- [ ] Train correction model (MT5-small)
  - [ ] Train on transcript-correction pairs
  - [ ] Hyperparameter tuning
  - [ ] Early stopping based on validation WER
- [ ] Train summarization model (MT5-small)
  - [ ] Train on transcript-summary pairs
  - [ ] Experiment with different summary lengths
  - [ ] Evaluate with ROUGE scores

#### Week 3: Evaluation & Iteration (Jan 20-26)
- [ ] Comprehensive model evaluation:
  - [ ] ASR: WER, CER on test set
  - [ ] Correction: WER improvement, BLEU score
  - [ ] Summarization: ROUGE-1, ROUGE-2, ROUGE-L, BERTScore
- [ ] Error analysis and failure case documentation
- [ ] Model optimization and compression
- [ ] Create model cards and documentation
- [ ] Benchmark against baselines

**Deliverables:**
- Fine-tuned Whisper model
- Trained correction model
- Trained summarization model
- Complete evaluation report
- Training notebooks and scripts

---

### 🧪 Phase 4: Testing & Quality Assurance (Feb 2026)
**Status:** Not Started
**Duration:** 2 weeks
**Target:** Mid-February 2026

#### Week 1: Unit & Integration Tests (Feb 3-9)
- [ ] Write unit tests:
  - [ ] `tests/test_asr.py` (target 90%+ coverage)
  - [ ] `tests/test_correction.py` (target 90%+ coverage)
  - [ ] `tests/test_summarization.py` (target 90%+ coverage)
  - [ ] `tests/test_evaluation.py` (target 90%+ coverage)
  - [ ] `tests/test_api.py` (target 85%+ coverage)
- [ ] Write integration tests:
  - [ ] Full pipeline test (audio → transcript → correction → summary)
  - [ ] API integration tests
  - [ ] Electron app E2E tests
- [ ] Create test fixtures:
  - [ ] Sample audio files (various quality levels)
  - [ ] Expected outputs for regression testing

#### Week 2: System Testing & Bug Fixes (Feb 10-16)
- [ ] Performance testing:
  - [ ] Benchmark transcription speed
  - [ ] Memory usage profiling
  - [ ] API load testing
- [ ] User acceptance testing:
  - [ ] Test with 3-5 teachers
  - [ ] Gather usability feedback
  - [ ] Identify UI/UX issues
- [ ] Security audit:
  - [ ] Check for data leaks
  - [ ] Validate file upload security
  - [ ] Test error handling
- [ ] Bug fixes and refinements
- [ ] Code review and refactoring

**Deliverables:**
- 80%+ test coverage
- Passing test suite
- Performance benchmark report
- Bug fix documentation

---

### 📦 Phase 5: Deployment & Distribution (Late Feb 2026)
**Status:** Not Started
**Duration:** 2 weeks
**Target:** End of February 2026

#### Week 1: Packaging & Documentation (Feb 17-23)
- [ ] Complete all documentation:
  - [ ] API Reference
  - [ ] Model Documentation
  - [ ] Training Guide
  - [ ] Deployment Guide
  - [ ] User Manual
  - [ ] Troubleshooting Guide
- [ ] Create Docker containers:
  - [ ] Backend Dockerfile
  - [ ] docker-compose for full stack
  - [ ] Docker Hub publishing
- [ ] Build Electron distributables:
  - [ ] Windows installer (.exe)
  - [ ] Portable version
  - [ ] Auto-updater setup
- [ ] Create demo video and screenshots

#### Week 2: Deployment & Launch (Feb 24-28)
- [ ] Setup production infrastructure:
  - [ ] Deploy backend to cloud (optional)
  - [ ] Setup CDN for models (optional)
  - [ ] Configure monitoring and logging
- [ ] Create installation packages:
  - [ ] All-in-one Windows installer
  - [ ] Offline installer with bundled models
- [ ] Pilot deployment at UCLM:
  - [ ] Install on 3-5 teacher computers
  - [ ] Conduct training session
  - [ ] Setup support channels
- [ ] Public release:
  - [ ] Publish to GitHub
  - [ ] Create release notes
  - [ ] Announce on relevant channels

**Deliverables:**
- Production-ready Windows installer
- Docker deployment option
- Complete documentation set
- Deployed to 3+ pilot users
- Public GitHub repository

---

### 🚀 Phase 6: Post-Launch & Iteration (Mar 2026+)
**Status:** Future
**Duration:** Ongoing

#### Month 1-2: Support & Refinement (Mar-Apr 2026)
- [ ] Monitor pilot deployment
- [ ] Collect user feedback
- [ ] Fix reported bugs
- [ ] Performance tuning based on real usage
- [ ] Create FAQ from common questions

#### Month 3-4: Feature Enhancement (May-Jun 2026)
- [ ] Implement requested features:
  - [ ] Real-time transcription (live lectures)
  - [ ] Multi-speaker diarization
  - [ ] Search within transcripts
  - [ ] Export to various formats (PDF, DOCX)
  - [ ] Cloud sync and backup
- [ ] Improve model accuracy with new data
- [ ] Optimize for lower-end hardware

#### Month 5-6: Scaling & Research (Jul-Aug 2026)
- [ ] Expand to other schools
- [ ] Publish research paper
- [ ] Present at conferences
- [ ] Open source release
- [ ] Build contributor community

**Ongoing:**
- Bug fixes and maintenance
- Model updates with new data
- Documentation updates
- Community support

---

## Feature Backlog

### High Priority (Next 3 Months)
1. Correction module implementation
2. Summarization module implementation
3. Data collection at UCLM
4. Model training pipeline
5. Comprehensive testing

### Medium Priority (3-6 Months)
6. Real-time transcription
7. Multi-speaker diarization
8. Advanced search functionality
9. Cloud deployment option
10. Mobile app (view-only)

### Low Priority (6+ Months)
11. Translation between English and Tagalog
12. Question generation from lectures
13. Quiz creation from transcripts
14. Integration with LMS (Moodle, Canvas)
15. Voice commands for navigation

### Research Ideas (Long Term)
16. Automatic assessment of lecture clarity
17. Student comprehension prediction
18. Code-switching pattern analysis
19. Lecture recommendation system
20. Adaptive summarization based on student level

---

## Dependencies & Risks

### Critical Dependencies
1. **UCLM Approval** - Required for data collection
2. **Annotator Availability** - Need 3-5 people for annotation
3. **GPU Access** - Required for model training
4. **User Adoption** - Need teachers willing to pilot

### Risk Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| UCLM approval delayed | High | Medium | Start with synthetic data, prepare backup school |
| Insufficient training data | High | Medium | Data augmentation, pre-trained models, synthetic TTS |
| Model accuracy below target | Medium | Medium | Ensemble methods, more training data, model tuning |
| Hardware limitations | Medium | Low | Cloud GPU, optimize for CPU, smaller models |
| Low user adoption | High | Low | Better UI/UX, training videos, responsive support |
| Data privacy concerns | High | Low | Strong encryption, local-only processing, clear policies |

---

## Success Metrics

### Technical Metrics
| Metric | Current | Target (v1.0) | Stretch Goal |
|--------|---------|---------------|--------------|
| ASR WER | ~25% (untested) | < 15% | < 10% |
| Correction Improvement | N/A | -30% WER | -40% WER |
| Summary ROUGE-L | N/A | > 0.4 | > 0.5 |
| Processing Speed | 3x realtime | < 2x realtime | 1x realtime |
| Test Coverage | 0% | 80% | 90% |
| User Satisfaction | N/A | 4/5 stars | 4.5/5 stars |

### Business Metrics
| Metric | Current | Target (v1.0) | Stretch Goal |
|--------|---------|---------------|--------------|
| Training Data | 0 hours | 20 hours | 40 hours |
| Annotations | 0 | 100% of data | + validation set |
| Pilot Users | 0 | 5 teachers | 10 teachers |
| Active Users | 0 | 20 students | 50 students |
| GitHub Stars | N/A | 50 | 200 |

---

## Milestones

- [x] **M0:** Project Setup (Oct 1, 2025)
- [x] **M1:** Working Transcription Pipeline (Oct 7, 2025)
- [ ] **M2:** Core ML Modules Complete (Nov 3, 2025)
- [ ] **M3:** Data Collection Complete (Dec 22, 2025)
- [ ] **M4:** Models Trained (Jan 26, 2026)
- [ ] **M5:** Testing Complete (Feb 16, 2026)
- [ ] **M6:** Production Release (Feb 28, 2026)
- [ ] **M7:** Pilot Deployment (Mar 15, 2026)
- [ ] **M8:** Public Launch (Apr 1, 2026)

---

## Resources Required

### Human Resources
- **Developer (You):** Full-time until v1.0
- **Annotators:** 3-5 people, part-time for 4-6 weeks
- **UCLM Coordinator:** 1 person, facilitates recording
- **Pilot Teachers:** 3-5 people for user testing

### Hardware Resources
- **Development:** Current laptop (sufficient)
- **Training:** GPU server or cloud (P3/T4 instance, ~$100-300/month for 1 month)
- **Recording:** Audio recorder (~$200) or use smartphones

### Software & Services
- **Cloud Storage:** 50-100GB for audio (~$5/month)
- **Cloud GPU:** For training only (~$150 for 1 month)
- **Optional:** Cloud deployment for demo (~$20/month)

**Total Estimated Cost:** $500-800 one-time + ~$50/month ongoing

---

## Review & Updates

This roadmap will be reviewed and updated:
- **Weekly** during active development phases
- **Monthly** during data collection and training
- **Quarterly** post-launch

**Next Review Date:** October 14, 2025

---

## Questions & Feedback

Have suggestions for the roadmap? Open an issue or contact the project lead.

**Maintainer:** [Your Name]
**Last Updated:** October 7, 2025
