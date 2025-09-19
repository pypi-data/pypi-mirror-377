import pickle
import numpy as np
import random
import sounddevice as sd
from scipy.io.wavfile import write as wav_write

from .utils import midi_to_chords, make_chord

class MarkovComposer:
    """
    A Markov chain-based trainable music composer.
    """
    def __init__(self):
        self.adj = {} # adjacency list of transition graph

    def fit(self, midi_path: str, look_back: int = 1, play: bool = False):
        """
        Train the Markov chain on a MIDI file. Can be called (with the same look_back) multiple times to train on multiple pieces.
        
        Arguments:
            `filename`: Path to input training data, a .mid file.
            `look_back`: Number of previous chords to condition on.
            `play`: Play the training piece while training?
        """
        chord_sequence = midi_to_chords(midi_path)
        iters = len(chord_sequence)-look_back

        for i in range(iters):
            if tuple(chord_sequence[i:i+look_back]) not in self.adj.keys():
                self.adj[tuple(chord_sequence[i:i+look_back])] = {}

            # update conditional frequency
            self.adj[tuple(chord_sequence[i:i+look_back])][chord_sequence[i+look_back]] = self.adj[tuple(chord_sequence[i:i+look_back])].get(chord_sequence[i+look_back], 0) + 1

            if play:
                sd.play(make_chord([int(x) for x in chord_sequence[i+look_back].split(',')], samplerate=44100, duration=0.2), samplerate=44100)
                sd.wait()
                print(f"[training {((i+1)*100)//iters}%] For chord(s) {tuple(chord_sequence[i:i+look_back])}: updated frequency of transition to {chord_sequence[i+look_back]} to {(self.adj[tuple(chord_sequence[i:i+look_back])][chord_sequence[i+look_back]])}")
        
        # Save an empty distribution for last key if the key did not appear before
        if tuple(chord_sequence[len(chord_sequence)-look_back:len(chord_sequence)]) not in self.adj.keys():
            self.adj[tuple(chord_sequence[len(chord_sequence)-look_back:len(chord_sequence)])] = {}
        # Build all the remaining edges with weight 0 to create a fully connected adjacency graph; even the "0" frequency transitions may have nonzero probability after softmaxing the conditional frequency distribution
        for i in range(iters+1):
            for chord in chord_sequence:
                if chord not in self.adj[tuple(chord_sequence[i:i+look_back])].keys():
                    self.adj[tuple(chord_sequence[i:i+look_back])][chord] = 0

        # # see transition matrix
        # for key in adj.keys():
        #     print(f"{key} --- {list(adj[key].values())}")

    def compose(self, piece_length: int = 1000, temperature: float = 1.0, play: bool = True, wav_path: str = None):
        """
        Generate a new composition using the trained Markov chain.
        
        Arguments:
            `piece_length`: Length of composition (in chords) to generate.
            `temperature`: Controls the randomness of the generated composition; lower value = more deterministic.
            `play`: Play the composition while generating?
            `wav_path`: If not None, saves the path to the .wav file at the specified path.
        """
        audio_sequence = []
        prev_state = list(self.adj.keys())[0]

        for i in range(piece_length):
            # use conditional frequencies as logits for a softmax instead of normalising frequencies, this provides smoothing while preserving the true distribution better (after softmaxing) than +1 smoothing
            with np.errstate(divide='ignore'):
                freqs = np.array(list(self.adj[prev_state].values()))
                log_freqs = np.zeros_like(freqs) if np.sum(freqs) == 0 else np.log(freqs)
                logits = log_freqs / temperature
                pmf = np.exp(logits) / np.sum(np.exp(logits))

            # simulate the "approximate" (softmaxed) conditional distribution
            current_chord = random.choices(list(self.adj[prev_state].keys()), weights=pmf)[0]

            chord = make_chord([int(x) for x in current_chord.split(',')], samplerate=44100, duration=0.2)
            audio_sequence.append(chord)

            if play:
                print(f"[generating {((i+1)*100)//piece_length}%] Transition from", prev_state, "to", current_chord)
                sd.play(chord, samplerate=44100)
                sd.wait()

            prev_state = tuple((list(prev_state)[1:]) + [current_chord])

        if wav_path is not None:
            wav_write(wav_path, 44100, (np.concatenate(audio_sequence)*32767).astype(np.int16))

    def save_chain(self, path: str):
        """
        Serialise the adjacency list of the transition graph and save to a pickle file.
        
        Arguments:
            `path`: Path to destination .pkl file.
        """
        with open(path, "wb") as f:
            pickle.dump(self.adj, f)

    def load_chain(self, path: str):
        """
        Load the serialised adjacency list of the transition graph from a pickle file.
        
        Arguments:
            `path`: Path to .pkl file.
        """
        with open(path, "rb") as f:
            self.adj = pickle.load(f)