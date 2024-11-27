// frontend/src/utils/keyboardShortcuts.ts
export const handleKeyboardShortcuts = (
    event: KeyboardEvent,
    callbacks: {
        onBold?: () => void;
        onItalic?: () => void;
        onUnderline?: () => void;
        onSave?: () => void;
        onUndo?: () => void;
        onRedo?: () => void;
    }
) => {
    if (event.ctrlKey || event.metaKey) {
        switch (event.key.toLowerCase()) {
            case 'b':
                event.preventDefault();
                callbacks.onBold?.();
                break;
            case 'i':
                event.preventDefault();
                callbacks.onItalic?.();
                break;
            case 'u':
                event.preventDefault();
                callbacks.onUnderline?.();
                break;
            case 's':
                event.preventDefault();
                callbacks.onSave?.();
                break;
            case 'z':
                event.preventDefault();
                if (event.shiftKey) {
                    callbacks.onRedo?.();
                } else {
                    callbacks.onUndo?.();
                }
                break;
        }
    }
};