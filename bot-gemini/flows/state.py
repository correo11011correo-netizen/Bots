# Estado en memoria (para demo). En producción: Redis/DB.
_state_history = {} # Stores a list (stack) of states for each user

def get(user_id):
    history = _state_history.get(user_id)
    if history:
        return history[-1] # Return current state (top of the stack)
    return None

def set_state(user_id, data):
    if user_id not in _state_history:
        _state_history[user_id] = []
    _state_history[user_id].append(data)

def pop_state(user_id):
    history = _state_history.get(user_id)
    if history and len(history) > 1:
        return history.pop() # Pop current state
    return None # Cannot go back if no history or only one state

def get_previous_state(user_id):
    history = _state_history.get(user_id)
    if history and len(history) > 1:
        return history[-2] # Peek at previous state
    return None

def clear(user_id):
    _state_history.pop(user_id, None)
