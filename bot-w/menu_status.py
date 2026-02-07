from botones_core import (
    incoming_messages, statuses,
    messages_lock, statuses_lock,
    display_incoming_message, display_status_update
)

def opcion_status():
    with messages_lock:
        messages_to_display = list(incoming_messages)
        incoming_messages.clear()
    with statuses_lock:
        statuses_to_display = list(statuses)
        statuses.clear()

    if not messages_to_display and not statuses_to_display:
        print("\nNo hay mensajes nuevos.")
    else:
        for msg in messages_to_display:
            display_incoming_message(msg)
        for st in statuses_to_display:
            display_status_update(st)
