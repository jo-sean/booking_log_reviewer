from tkinter import Tk
from tkinter.filedialog import askopenfilename


# Source: https://stackoverflow.com/questions/3579568/choosing-a-file-in-python-with-simple-dialog
def get_file_name():
    Tk().withdraw()                 # Prevents root window from appearing
    filename = askopenfilename()    # shows an "Open" dialog box and returns path of file
    return filename
