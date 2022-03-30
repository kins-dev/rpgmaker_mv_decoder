import pathlib
import threading
import tkinter as tk
import tkinter.ttk as ttk
from click._termui_impl import ProgressBar
from pygubu.widgets.pathchooserinput import PathChooserInput
from pygubu.widgets.dialog import Dialog

from rpgmaker_mv_decoder.utils import decode_files, guess_at_key

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "gui.ui"


class DialogUI(Dialog):
    def _create_ui(self):
        # build ui
        self.labelWorking = ttk.Label(self.toplevel)
        self.labelWorking.configure(text='Please wait...')
        self.labelWorking.grid(column='0', columnspan='3', row='0', sticky='w')
        self.pb = ttk.Progressbar(self.toplevel)
        self.pb.configure(length='300', maximum='1492',
                          mode='determinate', orient='horizontal')
        self.pb.configure(value='0')
        self.pb.grid(column='0', columnspan='3', row='2')
        self.labelPct = ttk.Label(self.toplevel)
        self.labelPct.configure(text='')
        self.labelPct.grid(column='0', row='4', sticky='w')
        self.labelCnt = ttk.Label(self.toplevel)
        self.labelCnt.configure(text='')
        self.labelCnt.grid(column='1', row='4')
        self.labelETA = ttk.Label(self.toplevel)
        self.labelETA.configure(text='')
        self.labelETA.grid(column='2', row='4', sticky='e')
        self.buttonCancel = ttk.Button(self.toplevel)
        self.buttonCancel.configure(text='Cancel')
        self.buttonCancel.grid(column='0', columnspan='3', row='6')
        self.buttonCancel.configure(command=self.cancel)
        self.toplevel.configure(height='100', padx='10', pady='10')
        self.toplevel.configure(width='300')
        self.toplevel.resizable(False, False)
        self.toplevel.title('Working')
        self.toplevel.rowconfigure('1', minsize='10')
        self.toplevel.rowconfigure('3', minsize='5')
        self.toplevel.rowconfigure('5', minsize='10')
        self.pb_valid: bool = False
        self.is_canceled: bool = False

        def disableEvent():
            pass
        self.toplevel.protocol("WM_DELETE_WINDOW", disableEvent)
        self.reset_progress()

    def cancel(self):
        self.is_canceled = True

    def close(self):
        Dialog.close(self)
        self.reset_progress()

    def set_label(self, text: str):
        self.labelWorking['text'] = text

    def show_progress(self):
        if self.pb_valid:
            self.labelCnt["text"] = f"{self.pos}/{self.max}"
            self.labelPct["text"] = f"{self.pct:0.01f}%"
            self.labelETA["text"] = self.eta
            self.pb["maximum"] = self.max
            self.pb["value"] = self.pos
        else:
            self.labelCnt["text"] = ""
            self.labelPct["text"] = ""
            self.labelETA["text"] = ""
            self.pb["maximum"] = 1000
            self.pb["value"] = 0

    def reset_progress(self):
        self.max: int = -1
        self.pos: int = -1
        self.pct: float = -1.0
        self.eta: str = ""
        self.pb_valid = False
        self.is_canceled = False
        self.show_progress()

    def format_eta(self, click_pb: ProgressBar) -> str:
        if click_pb.eta_known:
            t = int(click_pb.eta)
            seconds = t % 60
            t //= 60
            if t <= 0:
                return f"ETA: {seconds} s"
            minutes = t % 60
            t //= 60
            if t <= 0:
                return f"ETA: {minutes:02}:{seconds:02}"
            hours = t % 24
            t //= 24
            if t <= 0:
                return f"ETA: {hours:02}:{minutes:02}:{seconds:02}"
            return f"ETA: {t}d {hours:02}:{minutes:02}:{seconds:02}"
        return ""

    def set_progress(self, click_pb: ProgressBar = None) -> bool:
        if None == click_pb:
            if self.pb_valid:
                self.pos = self.max
                self.pct = 100.0
                self.eta = 0
        else:
            self.pb_valid = True
            self.pos = click_pb.pos
            self.max = click_pb.length
            self.pct = click_pb.pct * 100
            self.eta = self.format_eta(click_pb)
        self.show_progress()
        return self.is_canceled


class GuiApp:
    def __init__(self, master=None):
        # build ui
        self.Window = tk.Tk() if master is None else tk.Toplevel(master)
        self.frameSrc = ttk.Labelframe(self.Window)
        self.pathSrc = PathChooserInput(self.frameSrc)
        self.pathSrc.configure(
            mustexist='true', title='Source Directory', type='directory')
        self.pathSrc.pack(expand='true', fill='x', side='top')
        self.pathSrc.bind('<<PathChooserPathChanged>>',
                          self.callbackPathSrc, add='')
        self.frameSrc.configure(padding='5', text='Source Directory')
        self.frameSrc.pack(expand='true', fill='x', side='top')
        self.frameDst = ttk.Labelframe(self.Window)
        self.pathDst = PathChooserInput(self.frameDst)
        self.pathDst.configure(
            mustexist='true', title='Destination Directory', type='directory')
        self.pathDst.pack(expand='true', fill='x', side='top')
        self.pathDst.bind('<<PathChooserPathChanged>>',
                          self.callbackPathDst, add='')
        self.frameDst.configure(padding='5', text='Destination Directory')
        self.frameDst.pack(expand='true', fill='x', side='top')
        self.frameOpt = ttk.Labelframe(self.Window)
        self.checkboxDetectExt = ttk.Checkbutton(self.frameOpt)
        self.detectFileExt = tk.StringVar(value='')
        self.checkboxDetectExt.configure(
            text='Detect File Extensions', underline='7', variable=self.detectFileExt)
        self.checkboxDetectExt.grid(
            column='0', columnspan='3', row='0', sticky='w')
        self.entryKey = ttk.Entry(self.frameOpt)
        self.gui_key = tk.StringVar(value='')
        self.entryKey.configure(
            state='normal', textvariable=self.gui_key, validate='all', width='32')
        self.entryKey.grid(column='0', row='1', sticky='w')
        _validatecmd = (self.entryKey.register(self.checkText), '%P')
        self.entryKey.configure(validatecommand=_validatecmd)
        self.buttonDetect = ttk.Button(self.frameOpt)
        self.buttonDetect.configure(
            state='disabled', text='Detect Key', underline='7')
        self.buttonDetect.grid(column='2', row='1', sticky='e')
        self.buttonDetect.configure(command=self.detect)
        self.frameOpt.configure(padding='10', text='Options')
        self.frameOpt.pack(side='top')
        self.frameOpt.columnconfigure('1', minsize='10')
        self.frameAction = ttk.Frame(self.Window)
        self.buttonDecode = ttk.Button(self.frameAction)
        self.buttonDecode.configure(
            state='disabled', text='Decode', underline='0')
        self.buttonDecode.pack(pady='5', side='top')
        self.buttonDecode.configure(command=self.decode)
        self.frameAction.pack(side='top')
        self.Window.configure(padx='10', pady='5')
        self.Window.title('RPGMaker MV Decoder')
        self.dialog = DialogUI(self.Window, True)

        # Main widget
        self.mainwindow = self.Window
        self.dialog_shown: bool = False

    def run(self):
        self.srcPath = ''
        self.dstPath = ''
        self.gui_key = ''
        self.mainwindow.mainloop()

    def disableButtons(self):
        self.buttonDetect['state'] = tk.DISABLED
        self.buttonDecode['state'] = tk.DISABLED

    def setButtonState(self):
        if(self.srcPath != ''):
            self.buttonDetect['state'] = tk.NORMAL
        if(self.srcPath != '' and self.dstPath != ''):
            self.buttonDecode['state'] = tk.NORMAL

    def callbackPathSrc(self, event=None):
        self.srcPath = self.pathSrc.entry.get()
        self.setButtonState()

    def callbackPathDst(self, event=None):
        self.dstPath = self.pathDst.entry.get()
        self.setButtonState()

    def checkText(self, newText: str) -> bool:
        data = newText.replace(" ", "")
        if (data == ""):
            return True
        try:
            int(data, 16)
            return True
        except ValueError:
            return False

    def show_dialog(self, title: str, text: str):
        self.dialog_shown = True
        if self.dialog is None:
            self.dialog = DialogUI(self.Window, True)
            self.dialog.set_title(title)
            self.dialog.set_label(text)
            self.dialog.run()
        else:
            self.dialog.set_title(title)
            self.dialog.set_label(text)
            self.dialog.show()

    def hide_dialog(self):
        if self.dialog is not None:
            if self.dialog_shown:
                self.dialog.close()
        self.dialog_shown = False

    def detect(self, decode: bool = False):
        def detectKey():
            self.disableButtons()

            def showDialog():
                self.show_dialog("Key Detection", "Searching for key")
            threading.Thread(target=showDialog).start()
            try:
                self.gui_key = guess_at_key(
                    self.srcPath, self.dialog.set_progress)
                self.entryKey.delete(0, tk.END)
                self.entryKey.insert(0, self.gui_key)
            except:
                pass
            if not decode:
                self.setButtonState()
            self.hide_dialog()
        if not decode:
            threading.Thread(target=detectKey).start()
        else:
            detectKey()

    def decode(self):
        if(self.gui_key == ''):
            self.detect(True)

        def showDialogDecode():
            self.show_dialog("Decoding Files", "Decoding all files")
        threading.Thread(target=showDialogDecode).start()

        def decodeFiles():
            decode_files(self.srcPath,
                         self.dstPath,
                         self.entryKey.get(),
                         self.detectFileExt.get() == '1',
                         self.dialog.set_progress)
            self.hide_dialog()
            self.setButtonState()
        threading.Thread(target=decodeFiles).start()
        self.disableButtons()


if __name__ == '__main__':
    app = GuiApp()
    app.run()
