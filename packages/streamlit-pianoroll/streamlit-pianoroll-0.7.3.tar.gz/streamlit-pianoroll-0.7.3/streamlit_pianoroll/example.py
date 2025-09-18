import numpy as np
import pandas as pd
import streamlit as st
from fortepyan import MidiPiece

from streamlit_pianoroll import from_fortepyan, pianoroll_player

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/example.py`

st.subheader("Behold, Piano Rolls!")


def make_some_notes(first_note: int, fortepyan_format: bool = False):
    if fortepyan_format:
        start_key = "start"
        end_key = "end"
    else:
        start_key = "startTime"
        end_key = "endTime"

    notes = []
    for it in range(180):
        start_time = it * 0.25 + 0.1 * np.random.random()
        end_time = start_time + 0.5
        pitch = first_note + 20 * np.sin(2 * np.pi * it / 80) + np.random.choice([-1, 0, 1])
        note = {
            "pitch": int(pitch),
            start_key: start_time,
            end_key: end_time,
            "velocity": 20 + np.random.randint(100),
        }
        notes.append(note)

    return notes


for jt in range(2):
    notes = make_some_notes(
        first_note=50 + np.random.randint(20),
    )
    midi_data = {
        "totalTime": notes[-1]["endTime"],
        "notes": notes,
    }
    pianoroll_player(midi_data=midi_data, key=jt)
    st.markdown("---")

notes_primary = make_some_notes(first_note=60, fortepyan_format=True)
notes_secondary = make_some_notes(first_note=53, fortepyan_format=True)

piece = MidiPiece(df=pd.DataFrame(notes_primary))
piece_secondary = MidiPiece(df=pd.DataFrame(notes_secondary))

display_columns = st.columns(3)
with display_columns[0]:
    st.write("Piece A")
    from_fortepyan(piece=piece)
with display_columns[1]:
    st.write("Piece B")
    from_fortepyan(piece=piece_secondary)
with display_columns[2]:
    st.write("Piece A & B")
    from_fortepyan(piece=piece, secondary_piece=piece_secondary)
