"""Transactional tick-domain edits. Sources are never mutated."""
from copy import deepcopy
from itertools import groupby
from .model import Note, Phrase, ChartError
from .validation import ensure_valid
from .hopo import is_flip, natural_states


def check_editor_song(song):
    ensure_valid(song)
    if any(n.lane == 4 for n in song.tracks.get('Medium', [])):
        raise ChartError('Orange is prohibited in Medium. Create four-fret Medium first.')
    for difficulty, notes in song.tracks.items():
        previous_end = 0
        for tick, items in groupby(sorted(notes), key=lambda n: n.tick):
            chord = list(items)
            if len({n.length for n in chord}) > 1 or tick < previous_end:
                raise ChartError(f'{difficulty}, tick {tick}: unequal chord sustains or extended sustain overlap. Clean the chart first or shorten the sustain.')
            previous_end = max(n.tick+n.length for n in chord)
        markers = song.modifiers.get(difficulty, [])
        ticks = {n.tick for n in notes}
        if any(not is_flip(m) or t not in ticks for t,m in markers):
            raise ChartError('Unsupported or orphan gameplay marker; clean the chart first.')
        if len({t for t,m in markers}) != len(markers):
            raise ChartError('Duplicate HOPO markers')
    return song


class EditSession:
    def __init__(self, song):
        self.song = deepcopy(song)
        self.undo_stack = []
        self.redo_stack = []
        self.log = []

    def change(self, difficulty, action, *, note=None, tick=0, lane=0, length=0, lanes=None, step=48):
        result = deepcopy(self.song)
        notes = result.tracks.setdefault(difficulty, [])
        markers = result.modifiers.setdefault(difficulty, [])
        phrases = result.phrases.setdefault(difficulty, [])
        if action in ('move', 'resize', 'delete'):
            if note not in notes: raise ChartError('Select an existing note')
            notes.remove(note)
            if action == 'resize':
                # GH3 chord members share one sustain duration.
                notes[:] = [Note(n.tick,n.lane,length) if n.tick==note.tick else n for n in notes]
                notes.append(Note(note.tick,note.lane,length))
            elif action == 'move': notes.append(Note(tick,lane,note.length))
            if not any(n.tick==note.tick for n in notes):
                markers[:] = [(t,m) for t,m in markers if t != note.tick]
                if action == 'move':
                    markers.extend((tick,m) for t,m in self.song.modifiers.get(difficulty,[]) if t==note.tick and not any(tick==x for x,_ in markers))
        elif action == 'add':
            chord = next((n for n in notes if n.tick==tick),None)
            notes.append(Note(tick,lane,chord.length if chord else length))
        elif action == 'pattern':
            if not lanes or len(lanes)>64 or step<1: raise ChartError('Pattern must contain 1–64 notes with positive spacing')
            notes.extend(Note(tick+i*step,l,0) for i,l in enumerate(lanes))
        elif action == 'star': phrases.append(Phrase(tick,2,length))
        elif action == 'remove_star': phrases[:] = [p for p in phrases if not (p.kind==2 and p.tick<=tick<p.tick+p.length)]
        elif action in ('hopo','strum','natural'):
            group = [n for n in notes if n.tick==tick]
            if not group: raise ChartError('Choose a note head for HOPO/strum changes')
            if action=='hopo' and (len(group)!=1 or tick==min(n.tick for n in notes)):
                raise ChartError('Use HOPO on a single note after the first event')
            markers[:] = [(t,m) for t,m in markers if t != tick]
            if action!='natural' and natural_states(result,difficulty,2.95)[tick] != (action=='hopo'):
                markers.append((tick,'N 5 0'))
        else: raise ChartError('Unknown edit')
        notes.sort(); phrases.sort(key=lambda p:(p.tick,p.kind)); markers.sort()
        check_editor_song(result)
        self.undo_stack.append((self.song, list(self.log))); self.redo_stack.clear()
        self.song=result; self.log.append(dict(difficulty=difficulty,action=action,tick=tick,lane=lane,length=length,original_note=vars(note) if note else None,pattern_lanes=lanes,pattern_step=step if action=='pattern' else None))

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append((self.song,list(self.log))); self.song,self.log=self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append((self.song,list(self.log))); self.song,self.log=self.redo_stack.pop()
