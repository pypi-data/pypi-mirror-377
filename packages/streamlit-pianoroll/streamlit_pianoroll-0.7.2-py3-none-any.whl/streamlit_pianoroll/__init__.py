import os

import pandas as pd
from fortepyan import MidiPiece
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "streamlit_pianoroll",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3210",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_pianoroll", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def pianoroll_player(
    midi_data: dict,
    show_bird_view: bool,
    key: str = None,
):
    """Create a new instance of "pianoroll".

    Parameters
    ----------
    midi_data: dict
        MIDI notes in a format that the html player will accept
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------

    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func(key=key, default=0, midi_data=midi_data, show_bird_view=show_bird_view)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


def from_notes_df(
    notes_df: pd.DataFrame,
    show_bird_view: bool = True,
    key: str = None,
):
    # This is what the html midi player expects
    column_mapping = {
        "start": "startTime",
        "end": "endTime",
    }
    df = notes_df.rename(columns=column_mapping)

    # This is the data structure expected by the html <midi-player>
    notes = df.to_dict(orient="records")
    midi_data = {
        "notes": notes,
        "totalTime": df.endTime.max(),
    }
    component_value = pianoroll_player(midi_data=midi_data, key=key, show_bird_view=show_bird_view)

    return component_value


def from_fortepyan(
    piece: MidiPiece,
    secondary_piece: MidiPiece = None,
    show_bird_view: bool = True,
    key: str = None,
):
    df = piece.df.copy()

    if secondary_piece is not None:
        df["colorId"] = 0
        secondary_df = secondary_piece.df.copy()
        secondary_df["colorId"] = 1
        df = pd.concat([df, secondary_df])
        df = df.sort_values("start", ignore_index=True)

    component_value = from_notes_df(
        notes_df=df,
        show_bird_view=show_bird_view,
        key=key,
    )

    return component_value
