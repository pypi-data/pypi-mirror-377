import mido
import numpy as np

def midi_to_chords(path: str) -> list[str]:
    midi = mido.MidiFile(path)
    ticks_per_beat = midi.ticks_per_beat
    tempo = 500000

    note_events = []

    for track in midi.tracks:
        time_seconds = 0
        for message in track:
            time_seconds += mido.tick2second(message.time, ticks_per_beat, tempo)
            if message.type == 'set_tempo':
                tempo = message.tempo
            elif message.type == 'note_on' and message.velocity > 0:
                note_events.append((time_seconds, message.note))

    note_events.sort()

    chords = []
    current_chord = []
    previous_time = None
    time_window = 0.05

    for time, note in note_events:
        if previous_time is None or abs(time - previous_time) <= time_window:
            current_chord.append(note)
        else:
            chords.append(current_chord)
            current_chord = [note]
        previous_time = time

    if current_chord:
        chords.append(current_chord)

    chords_str = []

    for chord in chords:
        frequencies = [int(440 * 2 ** ((note - 69) / 12)) for note in sorted(set(chord))]
        chords_str.append(str(','.join(map(str, frequencies))))
    
    # print(chords_str)
    return chords_str

def make_chord(frequencies: list, samplerate: int = 44100, duration: float = 0.2):
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    waves = [np.sin(2 * np.pi * f * t) for f in frequencies]
    chord = np.sum(waves, axis=0)
    chord *= 1 / np.max(np.abs(chord))

    fade_len = int(0.01 * samplerate)
    fade = np.linspace(1, 0, fade_len)
    chord[-fade_len:] *= fade

    return chord