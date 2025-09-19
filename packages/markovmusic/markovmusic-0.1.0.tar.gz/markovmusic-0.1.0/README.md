# markovmusic

## What is it?
Using *markovmusic*, you can make a Markov chain generate music using patterns learned from your own MIDI files.

## Minimal use
- Install this package
```sh
pip install markovmusic
```
- Instantiate a composer
```python
from markovmusic import MarkovComposer

model = MarkovComposer()
```
- Specify a a MIDI file to train the composer on
```python
model.fit("allmanbros/jessica.mid")
```
- Compose and play new music
```python
model.compose()
```

## Advanced features
Usage of the following advanced features is in the docstrings for the following methods of `MarkovComposer`:
- `fit()`: you can specify:
    - how many previous chords you want the composer to learn to use to predict the next chord (`look_back`)
    - whether to play the music while training or not (`play`)
- `compose()`: you can specify:
    - how long the generated music should be (`piece_length`)
    - how creative or restrictive you want the generated music to be (`temperature`)
    - whether to play the music while generating or not (`play`)
    - a path to save the music as a WAV file (`wav_path`)
- `save_chain()`: save a trained composer to disk
- `load_chain()`: load a saved composer from disk