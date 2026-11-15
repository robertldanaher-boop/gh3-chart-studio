"""Integer-tick intermediate representation. No resampling of authored timing."""
from dataclasses import dataclass, field
from fractions import Fraction

class ChartError(ValueError):
    pass

@dataclass(frozen=True, order=True)
class Note:
    tick: int
    lane: int
    length: int = 0

@dataclass(frozen=True)
class Phrase:
    tick: int
    kind: int  # 0/1 face-off, 2 star power
    length: int

@dataclass
class Song:
    resolution: int = 192
    metadata: dict[str, str] = field(default_factory=dict)
    tempos: list[tuple[int, Fraction]] = field(default_factory=lambda: [(0, Fraction(500000))])
    signatures: list[tuple[int, int, int]] = field(default_factory=lambda: [(0, 4, 4)])
    events: list[tuple[int, str]] = field(default_factory=list)
    tracks: dict[str, list[Note]] = field(default_factory=dict)
    phrases: dict[str, list[Phrase]] = field(default_factory=dict)
    modifiers: dict[str, list[tuple[int, str]]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    ini_metadata: dict[str, str] = field(default_factory=dict)

    def seconds(self, tick: int) -> float:
        result = Fraction(0)
        for i, (start, tempo) in enumerate(self.tempos):
            if start >= tick:
                break
            end = min(tick, self.tempos[i+1][0]) if i+1 < len(self.tempos) else tick
            result += (end-start)*tempo/self.resolution/1000000
        return float(result)

BASES = {'Easy': 60, 'Medium': 72, 'Hard': 84, 'Expert': 96}
