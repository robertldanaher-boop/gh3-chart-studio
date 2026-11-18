> Deferred by the accepted [project direction](PROJECT_DIRECTION.md). The text below is historical research, not the next implementation priority.

# Instrument and tablature refinement — researched, not implemented

Current 0.4.1 implementation: external stem input, separate original-mix playback,
manual attack inclusion/exclusion and a horizontal timing review. No separator,
model download, web scraper or tablature parser was added.

## Instrument isolation

Demucs's upstream README describes the experimental htdemucs_6s model, which adds
guitar and piano stems. It reports only preliminary guitar quality and notes bleed
and artifacts for piano. The original repository is archived. Its code license is
MIT; choosing code alone does not settle model-weight/dataset/dependency obligations.
https://github.com/facebookresearch/demucs/blob/main/README.md
https://github.com/facebookresearch/demucs/blob/main/LICENSE

Ultimate Vocal Remover GUI is another external separation host; its code is MIT.
Model choice, weights, runtime, and actual guitar-stem quality need independent
review. No code or model weights from either project were copied or installed.
https://github.com/Anjok07/ultimatevocalremovergui/blob/master/README.md

Recommended next implementation: optional isolated environment/process for a pinned
separator, progress/cancel, explicit first model download, original-file hashes,
same-length/time-origin checks, stem audition and CPU benchmark on Bob's hardware.
Do not assume CUDA on his AMD system. Benchmark noise bleed and false attacks on
real examples before labeling output guitar transcription. Separation is an input
improvement, not a note detector; guitar-focused pitch/onset analysis remains separate.
A standalone verified stem file can already be tested in the current GUI.

## Tablature reference

Guitar Pro documents MusicXML and MIDI export. These carry structured rhythm/note
information useful for later alignment; rendered/ASCII tablature often lacks enough
explicit timing. Guitar Pro MIDI is NOT automatically a GH3 PART GUITAR chart, so it
must not be routed blindly through our existing game-chart MIDI parser.
https://www.guitar-pro.com/docs/gp8/import-export/export/export-musicxml
https://www.guitar-pro.com/docs/gp8/import-export/export/export-midi

Proposed workflow: title/artist reference search via an allowed provider or explicit
browser link; user chooses a permitted local structured score; select guitar voice;
align to the correct recording, tempo and sections; preview proposed edits; apply
to a copy with provenance. Search results, alternate arrangements and user-written
tabs are references, not ground truth. Do not silently replace chart timing or
assume tab frets correspond to GH3 fret buttons. Search/import/alignment need their
own fixture tests, license/format review and GUI milestone.
