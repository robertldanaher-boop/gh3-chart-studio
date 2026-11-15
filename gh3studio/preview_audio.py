"""Find only an unambiguous recording next to the chart; never guess a stem."""
from pathlib import Path

AUDIO_SUFFIXES={'.wav','.flac','.ogg','.mp3','.opus'}

def matching_audio(chart_path,metadata):
    folder=Path(chart_path).resolve().parent
    stream=metadata.get('MusicStream','').replace('\\','/')
    if stream:
        candidate=(folder/stream).resolve()
        if candidate.is_relative_to(folder) and candidate.is_file() and candidate.suffix.lower() in AUDIO_SUFFIXES:return candidate
    candidates=[p for p in folder.iterdir() if p.is_file() and p.stem.lower()=='song' and p.suffix.lower() in AUDIO_SUFFIXES]
    return candidates[0] if len(candidates)==1 else None
