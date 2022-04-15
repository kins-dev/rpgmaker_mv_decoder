#!/usr/bin/env python3
"""Main entry point for GUI"""
import pathlib
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk

from click._termui_impl import ProgressBar
from pygubu.widgets.dialog import Dialog
from pygubu.widgets.pathchooserinput import PathChooserInput

import rpgmaker_mv_decoder
from icon_data import ABOUT_ICON, TITLE_BAR_ICON
from rpgmaker_mv_decoder.exceptions import NoValidFilesFound
from rpgmaker_mv_decoder.utils import decode_files, encode_files, guess_at_key

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "gui.ui"


def _format_eta(click_pb: ProgressBar) -> str:
    if click_pb.eta_known:
        time: int = int(click_pb.eta)
        seconds = time % 60
        time //= 60
        if time <= 0:
            return f"ETA: {seconds} s"
        minutes = time % 60
        time //= 60
        if time <= 0:
            return f"ETA: {minutes:02}:{seconds:02}"
        hours = time % 24
        time //= 24
        if time <= 0:
            return f"ETA: {hours:02}:{minutes:02}:{seconds:02}"
        return f"ETA: {time}d {hours:02}:{minutes:02}:{seconds:02}"
    return ""


class _DialogUI(Dialog):
    """`DialogUI` Dialog box showing progress"""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, parent):
        super().__init__(parent, modal=True)
        self.pb_valid: bool = False
        self.is_canceled: bool = False
        self.max: int = -1
        self.pos: int = -1
        self.pct: float = -1.0
        self.eta: str = ""

    def _create_ui(self):
        # build ui
        self.label_working = ttk.Label(self.toplevel)
        self.label_working.configure(text="Please wait...")
        self.label_working.grid(column="0", columnspan="3", row="0", sticky="w")
        self.progress_bar = ttk.Progressbar(self.toplevel)
        self.progress_bar.configure(
            length="300", maximum="1492", mode="determinate", orient="horizontal"
        )
        self.progress_bar.configure(value="0")
        self.progress_bar.grid(column="0", columnspan="3", row="2")
        self.label_pct = ttk.Label(self.toplevel)
        self.label_pct.configure(text="")
        self.label_pct.grid(column="0", row="4", sticky="w")
        self.label_cnt = ttk.Label(self.toplevel)
        self.label_cnt.configure(text="")
        self.label_cnt.grid(column="1", row="4")
        self.label_eta = ttk.Label(self.toplevel)
        self.label_eta.configure(text="")
        self.label_eta.grid(column="2", row="4", sticky="e")
        self.button_cancel = ttk.Button(self.toplevel)
        self.button_cancel.configure(text="Cancel")
        self.button_cancel.grid(column="0", columnspan="3", row="6")
        self.button_cancel.configure(command=self._cancel)
        self.toplevel.configure(height="100", padx="10", pady="10")
        self.toplevel.configure(width="300")
        self.toplevel.resizable(False, False)
        self.toplevel.title("Working")
        self.toplevel.rowconfigure("1", minsize="10")
        self.toplevel.rowconfigure("3", minsize="5")
        self.toplevel.rowconfigure("5", minsize="10")

        def disable_event():
            pass

        self.toplevel.protocol("WM_DELETE_WINDOW", disable_event)
        self._reset_progress()

    def _cancel(self):
        self.is_canceled = True

    def close(self):
        """`close` closes the dialog"""
        Dialog.close(self)
        self._reset_progress()

    def set_label(self, text: str):
        """`set_label` Sets the label for the progress dialog

        Args:
        - `text` (`str`): Label to show
        """
        self.label_working["text"] = text

    def _show_progress(self):
        if self.pb_valid:
            self.label_cnt["text"] = f"{self.pos}/{self.max}"
            self.label_pct["text"] = f"{self.pct:0.01f}%"
            self.label_eta["text"] = self.eta
            self.progress_bar["maximum"] = self.max
            self.progress_bar["value"] = self.pos
        else:
            self.label_cnt["text"] = ""
            self.label_pct["text"] = ""
            self.label_eta["text"] = ""
            self.progress_bar["maximum"] = 1000
            self.progress_bar["value"] = 0

    def _reset_progress(self):
        self.max: int = -1
        self.pos: int = -1
        self.pct: float = -1.0
        self.eta: str = ""
        self.pb_valid = False
        self.is_canceled = False
        self._show_progress()

    def set_progress(self, click_pb: ProgressBar = None) -> bool:
        """`set_progress` updates the progress bar and labels for the progress dialog

        Used as a callback function, takes the click `ProgressBar` and updates the
        UI as appropriate

        Args:
        - `click_pb` (`ProgressBar`, optional): Current progress data, `None` if finished.
        Defaults to `None`.

        Returns:
        - `bool`: `True` if the user has canceled the operation, `False` otherwise
        """
        if click_pb is None:
            if self.pb_valid:
                self.pos = self.max
                self.pct = 100.0
                self.eta = 0
        else:
            self.pb_valid = True
            self.pos = click_pb.pos
            self.max = click_pb.length
            self.pct = click_pb.pct * 100
            self.eta = _format_eta(click_pb)
        self._show_progress()
        return self.is_canceled


def _open_github():
    url = "https://git.kins.dev/rpgmaker_mv_decoder"
    webbrowser.open(url, new=0, autoraise=True)


class _AboutUI(Dialog):
    def __init__(self, parent):
        super().__init__(parent, modal=True)

    def _create_ui(self):
        # build ui
        self.label_title = ttk.Label(self.toplevel)
        self.label_title.configure(
            font="TkHeadingFont",
            justify="left",
            relief="flat",
            text="RPGMaker MV Decoder / Encoder",
        )
        self.label_title.grid(column="0", padx="5", pady="5", row="0")
        self.label_version = ttk.Label(self.toplevel)
        self.label_version.configure(
            text=f"""Version: {rpgmaker_mv_decoder.__version__}

Copyright 2022 by Scott@kins.dev
All rights reserved

See GitHub for license information
"""
        )
        self.label_version.grid(column="0", padx="5", row="2", sticky="w")
        self.button_github = ttk.Button(self.toplevel)
        self.button_github.configure(text="GitHub")
        self.button_github.grid(column="0", pady="5", row="5")
        self.button_github.configure(command=_open_github)
        self.toplevel.configure(height="100", width="200")
        self.toplevel.resizable(False, False)
        self.toplevel.title("About RPGMaker MV Decoder / Encoder")
        self.img_icon = tk.PhotoImage(data=TITLE_BAR_ICON["data"], format=TITLE_BAR_ICON["format"])
        self.toplevel.iconphoto(True, self.img_icon)


class _GuiApp:
    # pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self, master=None):
        # build ui
        self.window = tk.Tk() if master is None else tk.Toplevel(master)
        self._setup_path_dialogs()
        self.checkbox_detect_ext = ttk.Checkbutton(self.frame_opt)
        self.detect_file_ext = tk.StringVar(value="")
        self.checkbox_detect_ext.configure(
            text="Detect File Extensions", underline="7", variable=self.detect_file_ext
        )
        self.checkbox_detect_ext.grid(column="0", columnspan="3", row="0", sticky="w")
        self.entry_key = ttk.Entry(self.frame_opt)
        self.gui_key = ""
        self.entry_key.configure(state="normal", validate="all", width="32")
        self.entry_key.grid(column="0", row="1", sticky="w")
        _validatecmd = (self.entry_key.register(self._validate_text), "%P")
        self.entry_key.configure(validatecommand=_validatecmd)
        self.button_detect = ttk.Button(self.frame_opt)
        self.button_detect.configure(state="disabled", text="Detect Key", underline="7")
        self.button_detect.grid(column="2", row="1", sticky="e")
        self.button_detect.configure(command=self._detect)
        self.frame_opt.configure(padding="10", text="Options")
        self.frame_opt.pack(side="top")
        self.frame_opt.columnconfigure("1", minsize="10")
        self._setup_action_frame()
        self.window.configure(padx="10", pady="5")
        self.img_icon = tk.PhotoImage(data=TITLE_BAR_ICON["data"], format=TITLE_BAR_ICON["format"])
        self.window.iconphoto(True, self.img_icon)
        self.window.title("RPGMaker MV Decoder / Encoder")
        self.window.resizable(0, 0)
        self.dialog = _DialogUI(self.window)
        self.about = _AboutUI(self.window)

        # Main widget
        self.main_window = self.window
        self.dialog_shown: bool = False
        self.src_path = ""
        self.dst_path = ""

    def _setup_path_dialogs(self):
        self.frame_src = ttk.Labelframe(self.window)
        self.path_src = PathChooserInput(self.frame_src)
        self.path_src.configure(mustexist="true", title="Source Directory", type="directory")
        self.path_src.pack(expand="true", fill="x", side="top")
        self.path_src.bind("<<PathChooserPathChanged>>", self._callback_path_src, add="")
        self.frame_src.configure(padding="5", text="Source Directory")
        self.frame_src.pack(expand="true", fill="x", side="top")
        self.frame_dst = ttk.Labelframe(self.window)
        self.path_dst = PathChooserInput(self.frame_dst)
        self.path_dst.configure(mustexist="true", title="Destination Directory", type="directory")
        self.path_dst.pack(expand="true", fill="x", side="top")
        self.path_dst.bind("<<PathChooserPathChanged>>", self._callback_path_dst, add="")
        self.frame_dst.configure(padding="5", text="Destination Directory")
        self.frame_dst.pack(expand="true", fill="x", side="top")
        self.frame_opt = ttk.Labelframe(self.window)

    def _setup_action_frame(self):
        self.frame_action = ttk.Frame(self.window)
        self.button_decode = ttk.Button(self.frame_action)
        self.button_decode.configure(state="disabled", text="Decode", underline="0")
        self.button_decode.grid(column="0", row="0", sticky="w")
        self.button_decode.configure(command=self._decode)
        self.button_encode = ttk.Button(self.frame_action)
        self.button_encode.configure(state="disabled", text="Encode", underline="0")
        self.button_encode.grid(column="2", row="0")
        self.button_encode.configure(command=self._encode)
        self.button_about = ttk.Button(self.frame_action)
        self.img_about = tk.PhotoImage(data=ABOUT_ICON["data"], format=ABOUT_ICON["format"])
        self.button_about.configure(default="normal", image=self.img_about, text="About")
        self.button_about.grid(column="4", row="0", sticky="e")
        self.button_about.configure(command=self._about)
        self.frame_action.pack(fill="x", pady="5", side="top")
        self.frame_action.grid_anchor("center")
        self.frame_action.columnconfigure("0", uniform="3")
        self.frame_action.columnconfigure("1", minsize="60")
        self.frame_action.columnconfigure("2", uniform="3", weight="1")
        self.frame_action.columnconfigure("3", minsize="60")

    def run(self):
        """`run` Runs the UI"""
        self.src_path = ""
        self.dst_path = ""
        self.gui_key = ""
        self.main_window.mainloop()

    def _about(self):
        self._show_about()

    def _disable_buttons(self):
        self.button_detect["state"] = tk.DISABLED
        self.button_decode["state"] = tk.DISABLED
        self.button_encode["state"] = tk.DISABLED

    def _set_button_state(self):
        if self.src_path != "":
            if self.gui_key == "":
                self.button_detect["state"] = tk.NORMAL
        if self.src_path != "" and self.dst_path != "":
            if self.gui_key == "" or len(self.gui_key) == 32:
                self.button_decode["state"] = tk.NORMAL
        if self.src_path != "" and self.dst_path != "" and len(self.gui_key) == 32:
            self.button_encode["state"] = tk.NORMAL

    def _callback_path_src(self, _event=None):
        self.src_path = self.path_src.entry.get()
        self._set_button_state()

    def _callback_path_dst(self, _event=None):
        self.dst_path = self.path_dst.entry.get()
        self._set_button_state()

    def _show_about(self):
        if self.about is None:
            self.about = _AboutUI(self.window)
            self.about.run()
        else:
            self.about.show()

    def _show_dialog(self, title: str, text: str):
        self.dialog_shown = True
        if self.dialog is None:
            self.dialog = _DialogUI(self.window)
            self.dialog.set_title(title)
            self.dialog.set_label(text)
            self.dialog.run()
        else:
            self.dialog.set_title(title)
            self.dialog.set_label(text)
            self.dialog.show()

    def _hide_dialog(self):
        if self.dialog is not None:
            if self.dialog_shown:
                self.dialog.close()
        self.dialog_shown = False

    def _validate_text(self, new_text: str) -> bool:
        data = new_text.replace(" ", "")
        if data == "":
            self.gui_key = data
            self._disable_buttons()
            self._set_button_state()
            return True
        try:
            int(data, 16)
            self.gui_key = data
            self._disable_buttons()
            self._set_button_state()
            return True
        except ValueError:
            return False

    def _detect(self, decode: bool = False):
        def _detect_key():
            self._disable_buttons()

            def _show_dialog():
                self._show_dialog("Key Detection", "Searching for key")

            threading.Thread(target=_show_dialog).start()
            try:
                self.gui_key = guess_at_key(self.src_path, self.dialog.set_progress)
                self.entry_key.delete(0, tk.END)
                self.entry_key.insert(0, self.gui_key)
            except NoValidFilesFound:
                pass
            if not decode:
                self._set_button_state()
            self._hide_dialog()

        if not decode:
            threading.Thread(target=_detect_key).start()
        else:
            _detect_key()

    def _decode(self):
        if self.gui_key == "":
            self._detect(True)

        def _show_dialog_decode():
            self._show_dialog("Decoding Files", "Decoding all files")

        threading.Thread(target=_show_dialog_decode).start()

        def _decode_files():
            decode_files(
                self.src_path,
                self.dst_path,
                self.entry_key.get(),
                self.detect_file_ext.get() == "1",
                self.dialog.set_progress,
            )
            self._hide_dialog()
            self._set_button_state()

        threading.Thread(target=_decode_files).start()
        self._disable_buttons()

    def _encode(self):
        def _show_dialog_encode():
            self._show_dialog("Encoding Files", "Encoding all files")

        threading.Thread(target=_show_dialog_encode).start()

        def _encode_files():
            encode_files(
                self.src_path,
                self.dst_path,
                self.entry_key.get(),
                self.dialog.set_progress,
            )
            self._hide_dialog()
            self._set_button_state()

        threading.Thread(target=_encode_files).start()
        self._disable_buttons()


if __name__ == "__main__":
    APP = _GuiApp()
    APP.run()
