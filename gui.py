import pathlib
import pygubu
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.pathchooserinput import PathChooserInput

from rpgmaker_mv_decoder.utils import decode_files, guess_at_key

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "gui.ui"


class GuiApp:
    def __init__(self, master=None):
        # build ui
        self.Window = tk.Tk() if master is None else tk.Toplevel(master)
        self.frameSrc = ttk.Labelframe(self.Window)
        self.pathSrc = PathChooserInput(self.frameSrc)
        self.pathSrc.configure(mustexist='true', title='Source Directory', type='directory')
        self.pathSrc.pack(expand='true', fill='x', side='top')
        self.pathSrc.bind('<<PathChooserPathChanged>>', self.callbackPathSrc, add='')
        self.frameSrc.configure(padding='5', text='Source Directory')
        self.frameSrc.pack(expand='true', fill='x', side='top')
        self.frameDst = ttk.Labelframe(self.Window)
        self.pathDst = PathChooserInput(self.frameDst)
        self.pathDst.configure(mustexist='true', title='Destination Directory', type='directory')
        self.pathDst.pack(expand='true', fill='x', side='top')
        self.pathDst.bind('<<PathChooserPathChanged>>', self.callbackPathDst, add='')
        self.frameDst.configure(padding='5', text='Destination Directory')
        self.frameDst.pack(expand='true', fill='x', side='top')
        self.frameOpt = ttk.Labelframe(self.Window)
        self.checkboxDetectExt = ttk.Checkbutton(self.frameOpt)
        self.detectFileExt = tk.StringVar(value='')
        self.checkboxDetectExt.configure(text='Detect File Extensions', underline='7', variable=self.detectFileExt)
        self.checkboxDetectExt.grid(column='0', columnspan='3', row='0', sticky='w')
        self.entryKey = ttk.Entry(self.frameOpt)
        self.gui_key = tk.StringVar(value='')
        self.entryKey.configure(state='normal', textvariable=self.gui_key, validate='all', width='32')
        self.entryKey.grid(column='0', row='1', sticky='w')
        _validatecmd = (self.entryKey.register(self.checkText), '%P')
        self.entryKey.configure(validatecommand=_validatecmd)
        self.buttonDetect = ttk.Button(self.frameOpt)
        self.buttonDetect.configure(state='disabled', text='Detect Key', underline='7')
        self.buttonDetect.grid(column='2', row='1', sticky='e')
        self.buttonDetect.configure(command=self.detect)
        self.frameOpt.configure(padding='10', text='Options')
        self.frameOpt.pack(side='top')
        self.frameOpt.columnconfigure('1', minsize='10')
        self.frameAction = ttk.Frame(self.Window)
        self.buttonDecode = ttk.Button(self.frameAction)
        self.buttonDecode.configure(state='disabled', text='Decode', underline='0')
        self.buttonDecode.pack(pady='5', side='top')
        self.buttonDecode.configure(command=self.decode)
        self.frameAction.pack(side='top')
        self.Window.configure(padx='10', pady='5')
        self.Window.title('RPGMaker MV Decoder')

        # Main widget
        self.mainwindow = self.Window
    
    def run(self):
        self.srcPath=''
        self.dstPath=''
        self.gui_key=''
        self.mainwindow.mainloop()


    def callbackPathSrc(self, event=None):
        self.srcPath=self.pathSrc.entry.get()
        self.buttonDetect['state'] = tk.NORMAL
        if(self.srcPath != '' and self.dstPath != ''):
            self.buttonDecode['state'] = tk.NORMAL

    def callbackPathDst(self, event=None):
        self.dstPath=self.pathDst.entry.get()
        if(self.srcPath != '' and self.dstPath != ''):
            self.buttonDecode['state'] = tk.NORMAL

    def checkText(self, newText: str) -> bool:
        data = newText.replace(" ","")
        if (data == ""):
            return True
        try:
            int(data, 16)
            return True
        except ValueError:
            return False

    def detect(self):
        try:
            self.gui_key = guess_at_key(self.srcPath)
            self.entryKey.delete(0,tk.END)
            self.entryKey.insert(0,self.gui_key)
        except:
            pass

    def decode(self):
        if(self.gui_key==''):
            self.detect()
        decode_files(self.srcPath, self.dstPath, self.entryKey.get(), self.detectFileExt.get() == '1')


if __name__ == '__main__':
    app = GuiApp()
    app.run()

