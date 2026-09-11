"""Desktop dialog with a headless description for automation."""

DIALOG_TITLE = "Delete this draft?"
CONFIRM_LABEL = "Remove"
CANCEL_LABEL = "Keep draft"


def dialog_spec() -> dict[str, str]:
    """Return the text presented by the dialog without opening a display."""
    return {
        "title": DIALOG_TITLE,
        "confirm_label": CONFIRM_LABEL,
        "cancel_label": CANCEL_LABEL,
    }


def build_dialog(parent):
    """Build the real Tk dialog when a desktop parent is available."""
    from tkinter import ttk

    spec = dialog_spec()
    frame = ttk.Frame(parent, padding=16)
    ttk.Label(frame, text=spec["title"]).pack()
    ttk.Button(frame, text=spec["confirm_label"]).pack(side="right")
    ttk.Button(frame, text=spec["cancel_label"]).pack(side="right")
    return frame
