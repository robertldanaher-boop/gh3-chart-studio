"""Dependency-light checks for restricted handoff workspaces; NOT the full suite."""
import copy
from pathlib import Path
import pytest
from gh3studio.chartio import read_chart,write_chart
from gh3studio.converter import convert
from gh3studio.validation import ensure_valid
from gh3studio.model import ChartError

FIXTURE=Path(__file__).parents[1]/'examples'/'technical-study.chart'

def test_four_fret_conversion_keeps_original_and_timing():
    source=read_chart(FIXTURE);original=copy.deepcopy(source);result,report=convert(source)
    assert source==original and result.tempos==source.tempos
    assert {n.tick for n in result.tracks['Medium']}=={n.tick for n in source.tracks['Expert']}
    assert all(0<=n.lane<=3 for n in result.tracks['Medium'])
    ensure_valid(result,True)

def test_chart_roundtrip(tmp_path):
    result,_=convert(read_chart(FIXTURE));path=tmp_path/'notes.chart';write_chart(result,path)
    restored=read_chart(path);assert restored.tracks==result.tracks and restored.tempos==result.tempos

def test_forced_markers_require_review():
    source=read_chart(FIXTURE);source.modifiers['Expert']=[(0,'N 6')]
    with pytest.raises(ChartError,match='cleanup'):convert(source)
