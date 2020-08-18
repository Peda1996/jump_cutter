# * Jump cuts a whole vegas sequence based on given parameters
# *
# * Revision Date: June 30.07.2020
# * Version:       1.0
# * Copyright:     Peter Wassermair
#

from collections import defaultdict
from tkinter import Label, Button, Entry, Tk, END

import numpy as np  # for numerical operations
from moviepy.editor import VideoFileClip, concatenate

# vegas importing shit
import clr

from utils.process_audio import get_jump_parts
from vegasWrapper.wrapper import get_selected_events, get_event_media_path, get_event_media_starting_position, \
    get_event_starting_position, get_event_media_end_used_time, \
    update_ui, copy_and_ajust_video_event_media

clr.AddReference('ScriptPortal.Vegas')
import ScriptPortal.Vegas
from ScriptPortal.Vegas import *

clr.AddReference('System.Drawing')
import System.Drawing


def add_entry_value(e, text):
    e.insert(END, text)


class GUI:
    def __init__(self, window, pyVEGAS):
        self.window = window
        self.pyVEGAS = pyVEGAS
        self.midi_file = None
        self.positions = None
        window.title("Jump Cutter")
        window.geometry('350x115')

        # set tempo
        self.label_video_precision = Label(window, text="Set precision")
        self.label_video_precision.grid(row=2, column=0)

        self.precision = Entry(window)
        add_entry_value(self.precision, "100")
        self.precision.grid(row=2, column=1)

        # video offset
        self.threshold_level = Label(window, text="Set Video Threshold in double")
        self.threshold_level.grid(row=3, column=0)

        self.threshold = Entry(window, textvariable="0.1")
        add_entry_value(self.threshold, "0.1")
        self.threshold.grid(row=3, column=1)

        # video offset
        self.fade_out_level = Label(window, text="Set Video fade_out in double seconds")
        self.fade_out_level.grid(row=4, column=0)

        self.fade_out = Entry(window)
        add_entry_value(self.fade_out, "0.2")
        self.fade_out.grid(row=4, column=1)

        # video offset
        self.fade_in_level = Label(window, text="Set Video fade_in in double seconds")
        self.fade_in_level.grid(row=5, column=0)

        self.fade_in = Entry(window)
        add_entry_value(self.fade_in, "0.2")
        self.fade_in.grid(row=5, column=1)

        # set execute button
        self.btn = Button(window, text="Execute Script", command=self.exec)
        self.btn.grid(row=7, column=1)

        window.mainloop()

    def exec(self):
        # get selected events
        events = get_selected_events(self.pyVEGAS)

        for track, event in events:
            filePath = get_event_media_path(event)
            media_start_pos = get_event_media_starting_position(event)
            media_event_end_time = get_event_media_end_used_time(event)
            start_pos_timeline = get_event_starting_position(event)
            current_offset = start_pos_timeline
            print("Starting")
            for start, end in get_jump_parts(
                    filePath,
                    float(self.threshold.get()),
                    int(self.precision.get()),
                    float(self.fade_out.get()),
                    float(self.fade_in.get())
            ):
                length = end - start
                if start < media_start_pos:
                    continue

                if end > media_event_end_time:
                    length = media_event_end_time - start

                # insert to correct position
                copy_and_ajust_video_event_media(event, current_offset, start, clip_duration=length)
                current_offset += length

            update_ui(self.pyVEGAS)


def FromVegas(pyVEGAS):
    GUI(Tk(), pyVEGAS)


if __name__ == "__main__":
    FromVegas(pyVEGAS)
