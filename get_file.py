from tkinter import Tk
from tkinter.filedialog import askopenfilename, askopenfilenames
import config


# Source: https://stackoverflow.com/questions/3579568/choosing-a-file-in-python-with-simple-dialog
def get_file_name():
    Tk().withdraw()                 # Prevents root window from appearing
    filename = askopenfilename()    # shows an "Open" dialog box and returns path of file
    config.bookingsFile = filename
    return filename

def get_file_names():
    Tk().withdraw()                 # Prevents root window from appearing
    filenames = askopenfilenames()    # shows an "Open" dialog box and returns path of file
    config.secReportFiles = filenames
    return filenames