import keyboard

def triggerKeyboardEvent(action: str) -> None:
    if action.startswith('Com:'):
        action = action.split(':', 1)[1]
        keyboard.press_and_release(action)
    elif action.startswith('Type:'):
        actions = action.split(':', 1)[1]

        for key in actions:
            keyboard.press_and_release(key)
