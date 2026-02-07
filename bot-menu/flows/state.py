# Estado por usuario para la demo
_demo = {}  # { sender: {"step": str, "product": str} }

def get(sender): return _demo.get(sender)
def set(sender, data): _demo[sender] = data
def clear(sender): _demo.pop(sender, None)
def active(sender): return sender in _demo
