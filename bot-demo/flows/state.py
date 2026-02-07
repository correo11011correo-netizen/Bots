import os
import json
from utils import get_user_data_path

def get_state_file_path(sender):
    """
    Returns the path to the user's state file.
    """
    return os.path.join(get_user_data_path(sender), "state.json")

def get(sender):
    """
    Loads the user's state from the state.json file.
    """
    state_file = get_state_file_path(sender)
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return None

def set(sender, data):
    """
    Saves the user's state to the state.json file.
    """
    state_file = get_state_file_path(sender)
    with open(state_file, "w") as f:
        json.dump(data, f, indent=4)

def clear(sender):
    """
    Deletes the state.json file.
    """
    state_file = get_state_file_path(sender)
    if os.path.exists(state_file):
        os.remove(state_file)

def active(sender):
    """
    Checks if the state.json file exists.
    """
    return os.path.exists(get_state_file_path(sender))
