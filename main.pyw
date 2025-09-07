import collections
import io
import os
import threading

import PySimpleGUI as sg
from PIL import Image, ImageTk
import random

folders = [
    'C:/Users/Duke/Desktop/projects/art/ref'
]


timer = None

class RepeatTimer(threading.Timer):
    win = None

    def set_win(self, win: sg.Window):
        self.win = win

    def run(self):
        while not self.finished.wait(self.interval):
            self.win.write_event_value('Next', True)

def get_img_data(f, maxsize=(500, 800), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

def start_new_timer():
    if timer:
        timer.cancel()
    t = RepeatTimer(timer_wait_time, lambda: {})
    t.set_win(window)
    t.start()
    return t
#timer_wait_time = int(sg.popup_get_text('Set timer delay', default_text=str(default_timer)))

default_timer = 120

default_times = [5, 10, 30, 60, 120, 300, 600, 1200]
buttons1 = []
buttons2 = []
for time in default_times:
    ls = buttons1 if time <= 120 else buttons2
    ls.append(sg.Button(str(time)))
buttons2.append(sg.Button('No Timer'))

# chatgpt
folder = folders[0]
second_dirs = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

# Split into two roughly even lists
mid = len(second_dirs) // 2
checkboxes1 = [sg.Checkbox(name, key=name, default=True) for name in second_dirs[:mid]]
checkboxes2 = [sg.Checkbox(name, key=name, default=True) for name in second_dirs[mid:]]

layout = [
    checkboxes1, checkboxes2,
    [sg.Button('Check/Uncheck All', key='-TOGGLE-')],
    [sg.Text('Set timer delay')],
    [sg.InputText(default_text=str(default_timer), key='-INPUT-')],
    buttons1, buttons2,
    [sg.Button('OK'), sg.Button('Close')]
]

window = sg.Window('Timer Input', layout)
timer_wait_time = default_timer

checked = True

while True:
    event, values = window.read()
    if event in ('Close', sg.WIN_CLOSED):
        sys.exit()
        break
    elif event == 'OK':
        try:
            timer_wait_time = int(values['-INPUT-'])
            break
        except:
            sg.popup_error("Please enter a valid number.")
    elif event == 'No Timer':
        timer_wait_time = 1e10
        break
    elif event == '-TOGGLE-':
        checked = not checked
        for name in second_dirs:
            window[name].update(value=checked)
    else:
        try:
            timer_wait_time = int(event)
            break
        except:
            sg.popup_error("Please enter a valid number.")

window.close()

selected_folders = [os.path.join(folder, name) for name in second_dirs if values.get(name)]

print(selected_folders)
#block over

img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")

dirs = collections.deque(selected_folders)
fnames = []
while dirs:
    folder = dirs.pop()
    flist0 = os.listdir(folder)
    for f in flist0:
        fpath = os.path.join(folder, f)
        if os.path.isdir(fpath):
            dirs.append(fpath)
            continue
        if os.path.isfile(fpath) and f.lower().endswith(img_types):
            fnames.append(fpath)
        # rename file
        # arr = f.split('_')
        # os.rename(os.path.join(folder, f), os.path.join(folder, arr[-1]))

num_files = len(fnames)  # number of images found
if num_files == 0:
    sg.popup('No files in folder')
    raise SystemExit()

random.shuffle(fnames)
# limit to 100 files
fnames = fnames[:100]

# make these 2 elements outside the layout as we want to "update" them later
# initialize to the first file in the list
filename = os.path.join(folder, fnames[0])  # name of first file in list
image_elem = sg.Image(data=get_img_data(filename, first=True))
filename_display_elem = sg.Text('{} {}/{}'.format(1, os.path.basename(os.path.dirname(fnames[0])), os.path.basename(fnames[0])),
                                size=(80, 2), auto_size_text=True, justification='center')

# define layout, show and read the form
pause_button = sg.Button('Pause', size=(8, 2))
col = [[filename_display_elem],
       [image_elem],
       [sg.Button('Prev', size=(8, 2)), pause_button, sg.Button('Next', size=(8, 2))]]

layout = [[sg.Column(col)]]

window = sg.Window('Image Browser', layout, return_keyboard_events=True,
                   location=(0, 0), use_default_focus=False, resizable=True, size=(550, 900))

timer = start_new_timer()

# loop reading the user input and displaying image, filename
i = 0
paused = False
while True:
    # read the form
    event, values = window.read()
    # perform button and keyboard operations
    if event == sg.WIN_CLOSED:
        break
    elif event in ('Next', 'd', 'Down:40', 'Next:34'):
        i += 1
        if i >= num_files:
            i -= num_files
        filename = fnames[i]
        if event == 'd':
            timer.cancel()
            pause_button.update(text='Resume (Paused)')
            paused = True
        else:
            timer = start_new_timer()
    elif event in ('Prev', 'a', 'Up:38', 'Prior:33'):
        i -= 1
        if i < 0:
            i = num_files + i
        filename = fnames[i]
        if event == 'a':
            timer.cancel()
            pause_button.update(text='Resume (Paused)')
            paused = True
        else:
            timer = start_new_timer()
    elif event in ('Pause', 'p', 'r', ' '):
        if paused:
            timer = start_new_timer()
            pause_button.update(text='Pause')
            paused = False
        else:
            timer.cancel()
            pause_button.update(text='Resume (Paused)')
            paused = True
    else:
        filename = fnames[i]

    # update window with new image
    this_img = get_img_data(filename)
    image_elem.update(data=this_img)
    window.size = (550, min(this_img.height(), 800) + 200)
    # update window with filename
    filename_display_elem.update('{} {}/{}'.format(i + 1, os.path.basename(os.path.dirname(fnames[i])), os.path.basename(fnames[i])))


timer.cancel()
window.close()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
