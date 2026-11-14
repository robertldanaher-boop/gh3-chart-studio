# MASTER DEVELOPMENT PROMPT
## GH3 Chart Studio — AI-Assisted Guitar Hero Chart Generator

### YOUR ROLE

Act as a senior software architect, Python developer, machine-learning engineer, digital audio processing specialist, Windows application developer, and Guitar Hero chart-format engineer.

Your assignment is to **design, implement, test, and package a functioning Windows desktop application named GH3 Chart Studio**.

This is an implementation project, not a theoretical discussion.

Write actual source code, create the project structure, implement functional features, run available tests, document limitations, and deliver working application files.

Do not substitute mock interfaces, simulated chart-generation results, or placeholder functionality for the requested features.

Where functionality is complex, implement a smaller genuinely working version first, then extend it.

Maintain a usable application throughout development.

---

# 1. PROJECT OBJECTIVE

Create a free, user-friendly Windows 10/11 desktop application capable of generating challenging, musically coherent Guitar Hero charts from audio files or existing charts.

The application's specialty is a custom difficulty called:

**EXPERT MEDIUM — FOUR-FRET TECHNICAL**

This difficulty should deliver the intensity of Expert gameplay while restricting the player to four fret buttons:

- Green
- Red
- Yellow
- Blue

The Orange fret must never appear in Expert Medium output.

The user should experience fast note sequences, complex rhythms, frequent HOPO opportunities, challenging chords, controlled tapping-style passages, expressive sustained notes, and dynamic fret movement.

The application must distinguish between musical accuracy and gameplay difficulty.

The objective is not perfect guitar transcription. The objective is to produce charts that feel closely connected to the song and are enjoyable, technically demanding, and playable.

The primary target platform is **Guitar Hero III Wii**, with exported charts imported through TheGHOST.

Clone Hero and YARG compatibility are secondary goals.

---

# 2. PRIMARY DEVELOPMENT TECHNOLOGY

Use the following technology stack unless a demonstrably better alternative is justified.

- Python 3.11 for core development
- PySide6 / Qt for the Windows graphical interface
- PyTorch for optional machine-learning components
- librosa and NumPy/SciPy for audio analysis
- FFmpeg for audio decoding and conversion
- mido and/or pretty_midi for MIDI processing
- A validated `.chart` parser and writer
- SQLite for pattern storage, user preferences, and training metadata
- PyInstaller for Windows packaging
- pytest for automated testing
- Git for version management

Develop the application for Windows 10/11 x64.

The application must not require Windows 7.

Windows 7 will be used separately in VMware to run TheGHOST.

Keep the software modular so that audio engines, chart-generation engines, and machine-learning models can be replaced without rewriting the GUI.

Use a documented dependency lockfile and a reproducible build process.

---

# 3. USER INTERFACE REQUIREMENTS

Create a complete desktop interface with all major functions accessible from one primary window.

Avoid opening separate applications or unnecessary pop-up tools.

The GUI must be understandable to someone without programming experience.

Include these main workspaces:

1. **Song Library**
2. **Audio Analysis**
3. **Chart Generator**
4. **Pattern Learning**
5. **Chart Editor and Preview**
6. **Batch Processing**
7. **Export and Validation**
8. **Settings and Diagnostics**

Support drag-and-drop for individual songs, multiple files, complete song folders, and recursively scanned parent directories.

The application should accept:

- MP3
- OGG
- WAV
- FLAC
- `.chart`
- `.mid`
- Existing Clone Hero song folders

Display song title, artist, album, year, duration, BPM, chart difficulties, note counts, and processing status.

Allow manual metadata editing.

Never overwrite original source files without explicit user approval.

Provide visible progress, cancellation, error reporting, and a saveable diagnostic log.

Long-running analysis must not freeze the GUI.

---

# 4. EXPERT MEDIUM DIFFICULTY ENGINE

Develop a dedicated chart-generation engine that operates on four fret buttons.

Do not simply generate ordinary Medium difficulty using conventional difficulty-reduction algorithms.

Allow the user to choose among:

- Standard Medium
- Challenging Medium
- Expert Medium
- Maximum Technical Medium
- Custom preset

Expert Medium should preserve much of the rhythmic complexity and note density of Expert while eliminating Orange fret usage.

The engine must support:

- Single-note runs
- Two-note chords
- Optional three-note chords
- Ascending fret sequences
- Descending fret sequences
- Alternating patterns
- Repeating riffs
- Rapid note changes
- Syncopated rhythms
- HOPO-friendly note transitions
- Sustain notes
- Chord-to-single-note transitions
- Repeated musical motifs
- Controlled random variation

Use musical constraints to preserve playability.

Avoid impossible chord changes, unnatural fret jumps, and excessive random patterns.

Do not assume every song contains a guitar solo.

A song consisting entirely of rhythm guitar should still be capable of producing a highly technical chart.

---

# 5. ADJUSTABLE GENERATION CONTROLS

Implement the following controls using a 1–6 scale:

| Control | Function |
|---|---|
| Density | Frequency of playable note events |
| Chords | Frequency and complexity of chord patterns |
| HOPOs | Preference for hammer-on/pull-off-compatible sequences |
| Taps | Preference for tap-style technical passages |
| Move | Degree of fret-position movement |
| Sustains | Frequency and duration of long notes |
| Rhythm Complexity | Syncopation and rhythmic variety |
| Pattern Variation | Degree of variation between repeated phrases |
| Motif Consistency | How closely repeated musical phrases retain familiar patterns |

Default Expert Medium profile:

- Density: 6/6
- Chords: 4/6
- HOPOs: 5/6
- Taps: 3/6
- Move: 5/6
- Sustains: 3/6
- Rhythm Complexity: 5/6
- Pattern Variation: 4/6
- Motif Consistency: 5/6

These defaults are experimental and must remain editable.

Provide generation controls for:

- Minimum total note count
- Maximum total note count
- Target notes per minute
- Minimum and maximum section density
- Maximum simultaneous fret count
- Maximum fret jump
- Maximum sustained-note length
- Minimum note spacing
- Optional note-count safety limits for GH3

Do not increase note density by inserting arbitrary notes into silence.

When the requested minimum cannot be achieved without violating musical or gameplay constraints, display a warning and explain why.

Distinguish timed note events from individual fret gems when calculating note counts.

---

# 6. AUDIO ANALYSIS ENGINE

Create an audio-processing pipeline that analyzes the musical structure of a recording.

Detect or estimate:

- Tempo and BPM
- Beat positions
- Onset timing
- Rhythmic accents
- Musical phrase boundaries
- Repeating patterns
- Instrumental intensity
- Melodic movement
- Rhythm-guitar activity
- Dominant instrumental phrases
- Sustained tones
- Quiet passages
- Significant musical transitions

Use source separation only when it materially improves results.

Investigate reusable open-source components such as STRUM, Demucs, Basic Pitch, and other suitable audio-analysis libraries.

Verify project licenses, compatibility, availability, and model-weight restrictions before integrating code or trained models.

Do not assume that identifying a pitch directly determines which Guitar Hero fret should be used.

The audio analysis should identify musical events. The chart-generation engine should translate those events into playable patterns.

Allow optional manual BPM and audio-offset corrections.

Preserve existing tempo maps when importing authored charts.

---

# 7. MACHINE LEARNING FROM EXISTING CHARTS

This is a core feature.

Create a system capable of learning gameplay patterns from existing Guitar Hero and Clone Hero charts.

The user must be able to select a folder containing hundreds or thousands of chart files.

Recursively scan the folders and identify playable guitar tracks.

Extract structured information including:

- Difficulty
- Song BPM and tempo changes
- Note positions
- Note-event density
- Chord frequency
- Chord size
- HOPO-compatible transitions
- Sustains
- Repeated motifs
- Fret movement
- Rhythmic subdivisions
- Note sequences
- Relative note spacing
- Phrase length
- Section-level complexity

Build a local searchable pattern library.

Classify patterns into groups such as:

- Steady rhythm
- Fast rhythm
- Repeating riff
- Melodic passage
- Technical run
- Alternating chord pattern
- Breakdown
- Sustained passage
- Instrumental transition

Do not require guitar solos.

Initial machine-learning functionality should use lightweight techniques such as:

- Statistical pattern extraction
- N-gram or Markov sequence models
- Pattern clustering
- Similarity scoring
- Conditional pattern sampling
- Constraint-based candidate selection

After these techniques are functional, evaluate an optional small Transformer or other suitable learned sequence model.

Do not require training a large neural network to make the first release functional.

Keep imported charts and training data local unless the user explicitly chooses otherwise.

---

# 8. GENERATING LEARNED VARIATIONS

Develop an engine that uses learned chart patterns to create alternative interpretations of the same audio.

The program should be able to generate at least three variations:

**Variation A — Rhythm Technical**

Emphasizes demanding rhythmic patterns, chord changes, accents, and repeating riffs.

**Variation B — Melodic Technical**

Emphasizes single-note runs, fret movement, melodic contours, and HOPO opportunities.

**Variation C — Adaptive Expert Medium**

Blends rhythm and melody characteristics based on the recording's musical structure.

Variations should remain aligned to the same beat and tempo map.

Changing the fret pattern must not randomly shift note timing.

Repeated musical phrases should produce recognizable related patterns, with optional controlled differences.

Expose a generation seed so results can be reproduced.

Allow users to save, compare, and regenerate variations.

---

# 9. LEARNING USER PREFERENCES

Create a feedback system that improves future chart generation.

After generating a chart, the user should be able to rate:

- Overall difficulty
- Musical accuracy
- Note density
- HOPO quality
- Chord quality
- Fret movement
- Rhythm consistency
- Enjoyment

Allow users to identify preferred patterns and sections.

Store these preferences locally.

Initially, preference learning may work through weighted pattern ranking and selection.

Later, support optional model fine-tuning where technically justified.

Clearly distinguish learned preference adjustments from actual neural-network training.

Do not claim that a model has been trained when only heuristic weights have changed.

---

# 10. GUITAR HERO III COMPATIBILITY

Create a dedicated GH3 Wii export profile.

This profile must produce charts suitable for import through TheGHOST.

Support valid `.chart` and MIDI export.

Implement proper difficulty-track mapping.

Expert Medium must be written into the actual Medium guitar difficulty—not merely labeled Medium while retaining Expert MIDI notes.

Verify:

- Correct MIDI track names
- Correct difficulty note pitches
- No Orange fret notes in Medium
- Valid event timing
- Valid tempo map
- Valid note-on/note-off pairing
- Valid sustain durations
- Properly ordered events
- Appropriate Star Power phrase events
- Reasonable note-count limits
- Correct audio synchronization

TheGHOST recognizes certain special events differently from modern Clone Hero tools.

Investigate the original TheGHOST source code and developer documentation before implementing:

- Star Power
- Face-Off sections
- Battle Power
- HOPO modifiers
- Tap-note conversion
- Sustain handling

Modern purple tap-note mechanics must not be assumed to work directly in GH3 Wii.

For GH3, tap-style passages should be represented using supported gameplay mechanics.

Whammy-bar functionality should be supported through sustained notes and relevant Star Power interactions, without pretending that the chart directly controls physical whammy movement.

Provide a compatibility report before exporting.

---

# 11. CHART EDITOR

Implement a functional chart editor with:

- Audio waveform
- Beat grid
- BPM display
- Note timeline
- Four-fret note lanes
- Optional five-fret source view
- Note insertion and deletion
- Chord editing
- Sustain editing
- HOPO-related event editing where supported
- Zoom and scrolling
- Playback synchronization
- Loop playback
- Global audio offset
- Tempo-map adjustment
- Undo and redo

Provide a visual comparison between the source chart and generated Expert Medium chart.

Support copying and converting an Expert or Hard track into Medium without modifying the source difficulty.

Editing controls must modify actual chart data, not just the visual display.

---

# 12. AUDIO SYNCHRONIZATION

Timing accuracy is a critical requirement.

Distinguish between:

**Global offset errors:** All notes are consistently early or late.

**Tempo-map errors:** Notes drift progressively away from the recording.

**Individual transcription errors:** Specific notes do not match the musical attack.

Provide separate correction methods for each.

Implement diagnostic measurements showing how closely generated note events correspond to detected musical onsets.

Do not blindly quantize every detected note onto the nearest beat.

Preserve syncopation, tuplets, and offbeat rhythmic elements when supported by the tempo map.

Where uncertainty is high, mark the affected section for review.

---

# 13. SONG METADATA

Support:

- Song title
- Artist
- Album
- Year
- Genre
- Charter
- Album artwork
- Audio filename
- Duration

Read metadata from source audio, `song.ini`, and song-folder information.

Allow manual corrections.

Optional online metadata lookup may use MusicBrainz and other appropriate sources.

Online lookup must never replace existing correct information without review.

Distinguish recording versions, remasters, live recordings, and alternate releases when available.

Create backups before modifying metadata.

---

# 14. BATCH PROCESSING

Support single-song and batch operations.

Allow users to select any batch size, including a default preset of 56 songs.

Batch processing must support:

- Recursive folder scanning
- Duplicate detection
- Metadata validation
- Chart validation
- Automatic generation
- Custom difficulty conversion
- Folder organization
- Progress reporting
- Error recovery
- Per-song logs
- Resume after interruption

Do not mark incomplete output folders as successfully processed.

Validate exported chart and audio files before marking a song complete.

Allow processing to continue after a recoverable song-specific error.

Never destroy source chart or audio files.

---

# 15. QUALITY CONTROL

Implement automated chart-quality scoring.

Evaluate:

- Rhythm synchronization
- Note density
- Event spacing
- Chord difficulty
- HOPO opportunity rate
- Fret movement
- Pattern repetition
- Phrase consistency
- Sustain distribution
- GH3 compatibility
- Missing or malformed metadata

Display both a numerical score and an explanation of the issues detected.

Avoid presenting subjective fun or musical quality as an objectively proven score.

Support before-and-after comparisons.

Include test fixtures containing known charts and corresponding audio.

Add regression tests to ensure future application changes do not silently alter timing or break existing chart output.

---

# 16. DEVELOPMENT MILESTONES

Implement the application in the following order.

### Milestone 1 — Working Windows GUI and Chart Converter

Deliver:

- Working PySide6 desktop application
- Drag-and-drop chart import
- `.chart` and `.mid` parsing
- Expert/Hard-to-Medium conversion
- Four-fret restriction
- Note-density controls
- Chord and movement controls
- Export to valid MIDI and `.chart`
- Automated tests

### Milestone 2 — Pattern Learning

Deliver:

- Recursive chart-library scanning
- Pattern extraction
- SQLite pattern database
- Pattern similarity system
- Conditional pattern generation
- Three alternative chart versions
- Preference feedback

### Milestone 3 — Audio Analysis

Deliver:

- Audio import and decoding
- BPM and beat detection
- Onset detection
- Musical phrase analysis
- Audio-aligned pattern placement
- Offset correction
- Timing diagnostics

### Milestone 4 — Integrated Editor

Deliver:

- Waveform
- Note-lane editor
- Playback
- Note and chord editing
- Sustain handling
- Undo/redo
- Source-versus-generated comparison

### Milestone 5 — GH3 and Batch Integration

Deliver:

- Valid GH3 MIDI difficulty mapping
- Star Power validation
- TheGHOST compatibility profile
- Metadata tools
- Batch processing
- Export verification
- Windows executable packaging

### Milestone 6 — Optional Neural Training

Deliver only after earlier milestones pass:

- Suitable pretrained-model evaluation
- Local training-data preparation
- Small conditional sequence model
- Model evaluation against held-out charts
- User-preference learning
- Optional GPU inference
- Saved model profiles

---

# 17. TESTING REQUIREMENTS

Do not rely exclusively on simulated tests.

Create automated unit tests, integration tests, and realistic chart-file fixtures.

Tests must verify:

1. Chart files load correctly.
2. Tempo maps survive conversion.
3. Expert Medium never uses Orange.
4. Notes are written to the correct MIDI difficulty.
5. Chords and sustain timings remain valid.
6. Exported files can be reopened.
7. Metadata is retained.
8. Generation can be reproduced using saved settings and seeds.
9. Failed batch jobs are not reported as successful.
10. Source files remain unchanged unless modification was authorized.

Where possible, verify output in an independent chart parser.

Document any functionality that still requires testing in TheGHOST or Dolphin.

---

# 18. PROJECT DELIVERY

Create a complete, organized Git repository.

Include:

- Application source code
- Requirements and dependency lockfile
- Installation instructions
- Windows build script
- Test suite
- Sample non-copyrighted charts
- Configuration presets
- User guide
- Technical documentation
- License notices
- Development changelog

Provide a repeatable Windows build process.

Do not invent successful tests or claim a working release without verification.

If the current execution environment cannot build a Windows executable directly, provide the source, tested components, and a reproducible Windows build script.

Never replace a failing feature with a fake success message.

---

# 19. IMPORTANT DESIGN RESTRICTIONS

Avoid these mistakes:

- Do not generate arbitrary notes to reach a minimum count.
- Do not automatically insert guitar solos.
- Do not assume all music follows rock-song structure.
- Do not discard most of Expert when converting to Medium.
- Do not introduce Orange notes into Expert Medium.
- Do not confuse contemporary tap notes with GH3 mechanics.
- Do not assume chart density proves musical accuracy.
- Do not regenerate audio unnecessarily when a compatible original exists.
- Do not overwrite existing charts without backups.
- Do not assume a successfully completed ML inference means the final export is valid.
- Do not download or redistribute datasets or model weights without checking licensing.
- Do not couple the GUI tightly to a single ML framework.
- Do not make GPU acceleration mandatory.
- Do not require the user to write Python commands for normal application operation.

---

# 20. EXECUTION INSTRUCTIONS

Begin by inspecting the existing environment and any attached project files.

Research and verify the necessary format specifications and open-source dependencies.

Then:

1. Create the repository structure.
2. Implement the first functional chart parser.
3. Implement and test four-fret Expert Medium conversion.
4. Create a working GUI for importing, adjusting, previewing, and exporting the converted chart.
5. Build the validation system.
6. Deliver the first testable milestone.
7. Continue expanding the project through the remaining milestones.

Prioritize **working code over speculative features**.

Make reasonable engineering decisions without repeatedly asking for confirmation.

When requirements conflict, prioritize:

1. GH3 Wii compatibility
2. Accurate musical timing
3. Four-fret gameplay
4. Playability
5. Adjustable technical difficulty
6. Pattern learning
7. Automatic generation convenience

Maintain an implementation log distinguishing completed, tested, partially implemented, and planned functionality.

**START IMPLEMENTATION NOW. Build the first usable version of GH3 Chart Studio, including an actual four-fret Expert Medium conversion engine and Windows GUI. Do not stop after writing a project proposal.**