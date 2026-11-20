from copy import deepcopy
from fractions import Fraction
import pytest
from gh3studio.model import Song,Note,Phrase,ChartError
from gh3studio.difficulty_set import complete_conversion,check_complete_conversion
from gh3studio.song_export import export_song_folder
from gh3studio.chartio import read_chart
from gh3studio.midiio import read_midi,write_midi


def test_full_set_retains_timing_sustains_and_source(tmp_path):
    song=Song(metadata={'Name':'Study','Artist':'Artist'},tracks={'Expert':[Note(i*192,i%5,96) for i in range(1000)],'Hard':[Note(0,0,96)],'Easy':[Note(0,4)]},
              tempos=[(0,Fraction(500000)),(1920,Fraction(400000))],phrases={'Expert':[Phrase(0,2,768)]})
    before=deepcopy(song);out,report=complete_conversion(song,'Expert')
    check_complete_conversion(out)
    assert song==before and out.tempos==song.tempos
    assert out.tracks['Hard']==song.tracks['Hard'] and out.tracks['Expert']==song.tracks['Expert']
    assert len(out.tracks['Medium'])==len(out.tracks['Easy'])==1000
    assert all(n.lane<3 and n.length==96 for n in out.tracks['Easy'])
    assert [n.tick for n in out.tracks['Easy']]==[n.tick for n in song.tracks['Expert']]
    assert out.phrases['Easy']==out.phrases['Medium']==song.phrases['Expert']
    import soundfile as sf
    import numpy as np
    audio=tmp_path/'song.wav';sf.write(audio,np.zeros(4410),44100)
    export_song_folder(out,report,tmp_path/'out',audio)
    reopened=read_chart(tmp_path/'out'/'notes.chart');check_complete_conversion(reopened)
    assert reopened.tracks==out.tracks
    write_midi(out,tmp_path/'notes.mid');midi=read_midi(tmp_path/'notes.mid');check_complete_conversion(midi)
    assert midi.tracks==out.tracks


@pytest.mark.parametrize('source',['Expert','Hard'])
def test_missing_slots_and_forbidden_only_taps_remain_nonempty(source):
    song=Song(tracks={source:[Note(0,4),Note(192,4),Note(384,4)]})
    out,report=complete_conversion(song,source,randomize_orange_sustains=False)
    check_complete_conversion(out)
    for d in ('Easy','Medium','Hard','Expert'):assert len(out.tracks[d])==3
    assert out.tracks[source]==song.tracks[source]
    assert report['difficulty_completion']['easy']['remapped_all_events_to_avoid_empty']
    assert complete_conversion(song,source,randomize_orange_sustains=False)[0]==out


def test_empty_slot_export_guard_and_easy_blue_guard(tmp_path):
    song,report=complete_conversion(Song(tracks={'Expert':[Note(0,0)]}),'Expert')
    song.tracks['Hard']=[]
    with pytest.raises(ChartError,match='Hard'):export_song_folder(song,report,tmp_path/'out',tmp_path/'none.wav')
    song.tracks['Hard']=[Note(0,0)];song.tracks['Easy']=[Note(0,3)]
    with pytest.raises(ChartError,match='Easy'):check_complete_conversion(song)


def test_conversion_cleans_all_tracks_and_exports_without_second_pass(tmp_path):
    import numpy as np
    import soundfile as sf
    from gh3studio.editing import prepare_cleanup
    song=Song(metadata={'Name':'Clean Study','Artist':'Artist','SongIniDelay':'100'},
        tracks={'Expert':[Note(0,0,384),Note(192,4,96)],'Hard':[Note(0,2,384),Note(192,1)]},
        modifiers={'Expert':[(0,'N 6 0')],'Hard':[(0,'N 5 0')]})
    before=deepcopy(song)
    out,report=complete_conversion(song,'Expert')
    # 0.18.5: the Expert tap and Hard forced note on a first note become forced HOPO flips everywhere.
    assert song==before and out.modifiers=={d:[(0,'N 5 0')] for d in ('Easy','Medium','Hard','Expert')}
    assert set(report['hopo_intent'])=={'Easy','Medium','Hard','Expert'}
    assert out.tracks['Expert'][0].length==192 and out.tracks['Hard'][0].length==192
    assert {c['difficulty'] for c in report['all_difficulty_cleanup']['changes']} >= {'Expert','Hard'}
    assert [c for c in prepare_cleanup(out,True,True)[1]['changes'] if c['action']!='remove marker/open-note event']==[]
    audio=tmp_path/'song.wav';sf.write(audio,np.zeros(44100),44100)
    details=export_song_folder(out,report,tmp_path/'out',audio)
    reopened=read_chart(tmp_path/'out'/'notes.chart');check_complete_conversion(reopened)
    # Timing normalization moves the whole chart by whole bars; forced flips move with their notes.
    offset=reopened.tracks['Expert'][0].tick-out.tracks['Expert'][0].tick
    assert reopened.modifiers=={d:[(t+offset,m) for t,m in markers] for d,markers in out.modifiers.items()}
    assert reopened.metadata['Offset']=='0'
    assert details['synchronization']['automatic']
    assert details['audio_export']['frames']>44100
    assert 'No missing difficulties were generated' not in (tmp_path/'out'/'IMPORT_README.txt').read_text()


def test_combined_export_dialog_automatic_repairs_and_timing(tmp_path):
    import numpy as np
    import soundfile as sf
    from PySide6.QtWidgets import QApplication,QDialogButtonBox
    from gh3studio.song_export_gui import SongExportDialog
    app=QApplication.instance() or QApplication([])
    song=Song(metadata={'Name':'Study','Artist':'Artist','SongIniDelay':'100'},tracks={'Expert':[Note(0,0,384),Note(192,4,96)]},modifiers={'Expert':[(0,'N 6 0')]})
    out,report=complete_conversion(song,'Expert')
    audio=tmp_path/'song.wav';sf.write(audio,np.zeros(44100),44100)
    dialog=SongExportDialog(out,str(audio),conversion_report=report)
    assert dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    assert dialog.markers.isHidden() and dialog.sustains.isHidden()
    assert dialog.review['synchronization']['automatic']
    assert 'Expert' in dialog.details.toPlainText()
    details=export_song_folder(dialog.prepared,dict(report,synchronization=dialog.review['synchronization']),tmp_path/'out',audio)
    assert details['audio_export']['frames']==44100+dialog.review['synchronization']['audio_padding_frames']
    dialog.close();app.processEvents()
