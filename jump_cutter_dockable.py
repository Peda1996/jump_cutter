# * Jump cuts a whole vegas sequence based on given parameters
# *
# * Revision Date: June 30.07.2020
# * Version:       1.0
# * Copyright:     Peter Wassermair
#
name = "JumpCutterView"

import clr

from System.Windows.Forms import *

from utils.process_audio import get_jump_parts
from vegasWrapper.wrapper import get_selected_events, copy_and_ajust_video_event_media, update_ui, get_event_media_path, \
    get_event_media_starting_position, get_event_media_end_used_time, get_event_starting_position

clr.AddReference('ScriptPortal.Vegas')
import ScriptPortal.Vegas
from ScriptPortal.Vegas import *

clr.AddReference('System.Drawing')
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import *


class MainForm(Form):
    def __init__(self, pyVEGAS):
        self.dockView = DockableControl(name)
        self.pyVEGAS = pyVEGAS
        self.InitializeComponent()
        self.Show()

    def InitializeComponent(self):
        self.TopLevel = False

        self._execute_button = System.Windows.Forms.Button()
        self._precision_label = System.Windows.Forms.Label()
        self._threshold_label = System.Windows.Forms.Label()
        self._precision = System.Windows.Forms.TextBox()
        self._threshold = System.Windows.Forms.TextBox()
        self._fade_out = System.Windows.Forms.TextBox()
        self._fade_out_label = System.Windows.Forms.Label()
        self._fade_in_label = System.Windows.Forms.Label()
        self._fade_in = System.Windows.Forms.TextBox()
        self.SuspendLayout()
        #
        # execute_button
        #
        self._execute_button.Location = System.Drawing.Point(12, 200)
        self._execute_button.Name = "execute_button"
        self._execute_button.Size = System.Drawing.Size(303, 203)
        self._execute_button.TabIndex = 0
        self._execute_button.Text = "Execute"
        self._execute_button.UseVisualStyleBackColor = True
        self._execute_button.Click += self.execute_button_click
        #
        # precision_label
        #
        self._precision_label.Location = System.Drawing.Point(13, 13)
        self._precision_label.Name = "precision_label"
        self._precision_label.Size = System.Drawing.Size(140, 23)
        self._precision_label.TabIndex = 1
        self._precision_label.Text = "Set precision"

        #
        # threshold_label
        #
        self._threshold_label.Location = System.Drawing.Point(13, 40)
        self._threshold_label.Name = "threshold_label"
        self._threshold_label.Size = System.Drawing.Size(140, 46)
        self._threshold_label.TabIndex = 2
        self._threshold_label.Text = "Set Video Threshold in double"
        #
        # precision
        #
        self._precision.Location = System.Drawing.Point(202, 14)
        self._precision.Name = "precision"
        self._precision.Size = System.Drawing.Size(65, 22)
        self._precision.TabIndex = 3
        self._precision.Text = "100"
        #
        # threshold
        #
        self._threshold.Location = System.Drawing.Point(202, 42)
        self._threshold.Name = "threshold"
        self._threshold.Size = System.Drawing.Size(65, 22)
        self._threshold.TabIndex = 4
        self._threshold.Text = "0.1"
        #
        # fade_out
        #
        self._fade_out.Location = System.Drawing.Point(200, 146)
        self._fade_out.Name = "fade_out"
        self._fade_out.Size = System.Drawing.Size(65, 22)
        self._fade_out.TabIndex = 8
        self._fade_out.Text = "0.1"
        #
        # fade_out_label
        #
        self._fade_out_label.Location = System.Drawing.Point(13, 146)
        self._fade_out_label.Name = "fade_out_label"
        self._fade_out_label.Size = System.Drawing.Size(141, 35)
        self._fade_out_label.TabIndex = 7
        self._fade_out_label.Text = "Set Video fade_out in double seconds"
        #
        # fade_in_label
        #
        self._fade_in_label.Location = System.Drawing.Point(12, 98)
        self._fade_in_label.Name = "fade_in_label"
        self._fade_in_label.Size = System.Drawing.Size(141, 35)
        self._fade_in_label.TabIndex = 9
        self._fade_in_label.Text = "Set Video fade_in in double seconds"
        #
        # fade_in
        #
        self._fade_in.Location = System.Drawing.Point(200, 98)
        self._fade_in.Name = "fade_in"
        self._fade_in.Size = System.Drawing.Size(65, 22)
        self._fade_in.TabIndex = 10
        self._fade_in.Text = "0.1"
        #
        # MainForm
        #
        self.dockView.Controls.Add(self._fade_in)
        self.dockView.Controls.Add(self._fade_in_label)
        self.dockView.Controls.Add(self._fade_out)
        self.dockView.Controls.Add(self._fade_out_label)
        self.dockView.Controls.Add(self._threshold)
        self.dockView.Controls.Add(self._precision)
        self.dockView.Controls.Add(self._threshold_label)
        self.dockView.Controls.Add(self._precision_label)
        self.dockView.Controls.Add(self._execute_button)

        self.ResumeLayout(False)
        self.PerformLayout()
        """
        self.ClientSize = System.Drawing.Size(286, 238)
        self.Controls.Add(self._fade_in)
        self.Controls.Add(self._fade_in_label)
        self.Controls.Add(self._fade_out)
        self.Controls.Add(self._fade_out_label)
        self.Controls.Add(self._threshold)
        self.Controls.Add(self._precision)
        self.Controls.Add(self._threshold_label)
        self.Controls.Add(self._precision_label)
        self.Controls.Add(self._execute_button)
        self.Name = "MainForm"
        self.Text = "Jump Cutter"
        #self.ResumeLayout(False)
        #self.PerformLayout()"""

    def log(self, msg):
        self._execute_button.Text = msg

    @staticmethod
    def str_to_float(value):
        try:
            return float(value)
        except ValueError:
            raise Exception('Cannot convert string to float')

    @staticmethod
    def str_to_int(value):
        try:
            return int(value)
        except ValueError:
            raise Exception('Cannot convert string to float')

    def execute_button_click(self, sender, e):
        threshold = self.str_to_float(self._threshold.Text)
        precision = self.str_to_int(self._precision.Text)
        fade_in = self.str_to_float(self._fade_in.Text)
        fade_out = self.str_to_float(self._fade_out.Text)

        self._execute_button.Text = f"Executing ({threshold};{precision};{fade_in};{fade_out})"

        # get selected events
        events = get_selected_events(self.pyVEGAS)

        for track, event in events:
            filePath = get_event_media_path(event)
            media_start_pos = get_event_media_starting_position(event)
            media_event_end_time = get_event_media_end_used_time(event)
            start_pos_timeline = get_event_starting_position(event)
            current_offset = start_pos_timeline
            try:
                self.log(f"Executing ({filePath},{threshold};{precision};{fade_in};{fade_out})")
                for start, end in get_jump_parts(
                        filePath,
                        threshold,
                        precision,
                        fade_out,
                        fade_in
                ):
                    length = end - start
                    if start < media_start_pos:
                        continue

                    if end > media_event_end_time:
                        length = media_event_end_time - start

                    # insert to correct position
                    copy_and_ajust_video_event_media(event, current_offset, start, clip_duration=length)
                    current_offset += length
                self.log("Update UI")
                update_ui(self.pyVEGAS)
            except Exception as e:
                self.log(str(e))


def FromVegas(pyVEGAS):
    if not pyVEGAS.ActivateDockView(name):
        pyVEGAS.LoadDockView(MainForm(pyVEGAS).dockView)


if __name__ == "__main__":
    FromVegas(pyVEGAS)
