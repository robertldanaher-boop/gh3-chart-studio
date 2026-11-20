"""Forced HOPO/strum notes survive cleanup as TheGHOST flips (Bob: TheGHOST showed 0 forced)."""
import copy
from gh3studio.chartio import read_chart
from gh3studio.hopo import authored_states, restore_hopo_intent, effective_states, clone_hero_threshold

HEADER = '[Song]\n{\n  Resolution = 192\n  Offset = 0\n}\n[SyncTrack]\n{\n  0 = TS 4\n  0 = B 120000\n}\n[Events]\n{\n}\n'


def chart(tmp_path, body, name='notes.chart'):
    path = tmp_path / name
    path.write_text(HEADER + '[ExpertSingle]\n{\n' + body + '}\n', encoding='utf-8')
    return read_chart(path)


NOTES = ''.join(f'  {t} = N {lane} 0\n' for t, lane in [(0, 0), (48, 1), (192, 2), (240, 3), (384, 0), (576, 1), (768, 2)])


def test_authored_intent_follows_clone_hero_rules_and_markers(tmp_path):
    plain = chart(tmp_path, NOTES)
    assert clone_hero_threshold(plain) == 192 * 65 / 192
    states = authored_states(plain, 'Expert')
    # 48 and 240 are within 65 ticks of a different fret -> natural HOPO; the rest strum.
    assert [t for t, hopo in sorted(states.items()) if hopo] == [48, 240]
    marked = chart(tmp_path, NOTES + '  48 = N 5 0\n  192 = N 5 0\n  576 = N 6 0\n', 'm.chart')
    states = authored_states(marked, 'Expert')
    assert states[48] is False and states[192] is True and states[576] is True  # flips + tap


def test_ini_hopo_frequency_is_honoured(tmp_path):
    song = chart(tmp_path, NOTES)
    song.ini_metadata = {'hopo_frequency': '200'}
    assert authored_states(song, 'Expert')[192] is True  # 144-tick gap is now within range
    song.ini_metadata = {'eighthnote_hopo': '1'}
    assert clone_hero_threshold(song) == 96


def test_cleaned_chart_plays_as_authored_in_theghost(tmp_path):
    original = chart(tmp_path, NOTES + '  48 = N 5 0\n  192 = N 5 0\n  576 = N 6 0\n  768 = N 7 0\n')
    cleaned = copy.deepcopy(original)
    cleaned.modifiers = {}
    report = restore_hopo_intent(cleaned, original, {'Expert': 'Expert'})
    assert report['Expert']['authored_forced'] == 2 and report['Expert']['authored_taps'] == 1
    assert all(m == 'N 5 0' for _, m in cleaned.modifiers['Expert'])
    intended = authored_states(original, 'Expert')
    played = effective_states(cleaned, 'Expert')
    assert played == intended  # every note plays as the charter meant (taps as HOPOs)


def test_charts_without_forced_or_tap_notes_are_unchanged(tmp_path):
    original = chart(tmp_path, NOTES)
    cleaned = copy.deepcopy(original)
    assert restore_hopo_intent(cleaned, original, {'Expert': 'Expert'}) == {}
    assert not cleaned.modifiers.get('Expert')


def test_four_fret_conversion_keeps_intent_on_every_difficulty(tmp_path):
    from gh3studio.difficulty_set import complete_conversion
    body = ''.join(f'  {t} = N {lane} 0\n' for t, lane in [(0, 4), (48, 3), (192, 4), (240, 2), (384, 1), (432, 0), (768, 4)])
    original = chart(tmp_path, body + '  48 = N 5 0\n  192 = N 5 0\n  432 = N 6 0\n')
    result, report = complete_conversion(original, 'Expert', strict=False, randomize_orange_sustains=True)
    intended = authored_states(original, 'Expert')
    assert set(report['hopo_intent']) == {'Easy', 'Medium', 'Hard', 'Expert'}
    for difficulty in ('Easy', 'Medium', 'Hard', 'Expert'):
        played = effective_states(result, difficulty)
        assert {t: played[t] for t in played} == {t: intended[t] for t in played}, difficulty
        ticks = {n.tick for n in result.tracks[difficulty]}
        assert all(m == 'N 5 0' and t in ticks for t, m in result.modifiers.get(difficulty, []))
    assert any('Forced HOPO/strum notes kept' in w for w in report['warnings'])


def test_timing_shift_moves_forced_flips_with_their_notes(tmp_path):
    from gh3studio.editing import shift_timing
    song = chart(tmp_path, NOTES)
    song.tracks['Medium'] = copy.deepcopy(song.tracks['Expert'])
    song.modifiers = {'Medium': [(192, 'N 5 0')]}
    shifted = shift_timing(song, 500)  # +1 beat at 120 BPM
    assert shifted.modifiers['Medium'] == [(384, 'N 5 0')]
    assert 384 in {n.tick for n in shifted.tracks['Medium']}
