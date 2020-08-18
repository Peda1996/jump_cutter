# shitty imports
import tkinter as tk
from collections import defaultdict
from tkinter import filedialog
# open gui
from tkinter import *
from tkinter.ttk import Combobox
from typing import Callable

import pydub
from mido import MidiFile
import clr

clr.AddReference('ScriptPortal.Vegas')
import ScriptPortal.Vegas
from ScriptPortal.Vegas import *

clr.AddReference('System.Drawing')
import System.Drawing


def get_event_media_starting_position(event):
    """Returns the starting cut position of the media file"""
    return event.ActiveTake.Offset.ToMilliseconds()


def get_event_media_used_length(event):
    """Returns the used length of the media file"""
    return event.ActiveTake.Length.ToMilliseconds()


def get_event_media_available_length(event):
    """Returns the available max length of the media file"""
    return event.ActiveTake.AvailableLength.ToMilliseconds()


def get_event_media_end_used_time(event):
    """Returns the available max length of the media file"""
    return get_event_media_starting_position(event) + get_event_media_used_length(event)


def get_event_media_path(event):
    """Returns the file path of the media file"""
    return event.ActiveTake.Media.FilePath


def get_event_starting_position(event):
    """Returns the starting position in the vegas timeline"""
    return event.Start.ToMilliseconds()


def get_event_used_length(event):
    """Returns the length of the event in the vegas timeline"""
    return event.ActiveTake.Length.ToMilliseconds()


def get_event_end(event):
    """Returns the end position of the end TimeCode in the vegas timeline"""
    return event.End.ToMilliseconds()


def get_event_media_offset(event):
    """Returns the offset to the media file vs the vegas timeline"""
    return event.ActiveTake.Offset.ToMilliseconds()


def get_loop_region_start(pyVEGAS):
    """Retuns the starting region of the loop region"""
    start_position = pyVEGAS.Transport.LoopRegionStart.ToMilliseconds()
    return start_position.ToMilliseconds()


def get_loop_region_length(pyVEGAS):
    """Retuns the Length of the loop region"""
    return pyVEGAS.Transport.LoopRegionLength.ToMilliseconds().ToMilliseconds()


def get_looping_region(pyVEGAS):
    """Returns the looping region"""
    start_position = get_loop_region_start(pyVEGAS)
    return start_position, start_position + get_loop_region_start(pyVEGAS)


def delete_event(track, event):
    """deletes the given track event from the given track"""
    return track.Events.Remove(event)


def copy_event(event,
               start_position,
               destination_track=None):
    """
    Copy given event to destination_track
    :param event: Given Vegas Event
    :param start_position: Start Time in milliseconds on the timeline
    :param destination_track: destination_track to copy, if none is specified the track of the event will be used
    :return returns the copied event
    """
    if destination_track is None:
        destination_track = event.Track
    return event.Copy(destination_track, Timecode.FromMilliseconds(start_position))


from .debug import convert


def copy_and_ajust_video_event_media(event,
                                     target_event_timeline_insert_pos,
                                     target_event_occurs_at_media_pos,
                                     clip_duration=None):
    print(
        f"Copy / Ajust Video Event: {convert(target_event_timeline_insert_pos)} - {convert(target_event_occurs_at_media_pos)} "
        f"- {convert(clip_duration)}")

    media_timeline_offset = get_event_media_offset(event)
    dLength = get_event_used_length(event)

    # copy the whole event to another starting position, and set duration
    e = copy_event(event, target_event_timeline_insert_pos + media_timeline_offset - target_event_occurs_at_media_pos)

    if clip_duration is None:
        clip_duration = dLength + media_timeline_offset - target_event_occurs_at_media_pos

    # ajusts the track based on media (nothing is done on timeline)
    adjust_track_event(e, target_event_timeline_insert_pos,
                       clip_duration)


def copy_and_ajust_video_event(event,
                               start_position_timeline,
                               destination_track=None,
                               media_position_start=None,
                               clip_duration=None):
    print(
        f"Copy / Ajust Video Event: {convert(start_position_timeline)} - {convert(media_position_start)} "
        f"- {convert(clip_duration)}")

    # if media_position_start is not None:
    #   start_position_timeline = start_position_timeline - media_position_start
    copied_event = copy_event(event, start_position_timeline, destination_track=destination_track)
    adjust_track_event(copied_event, start_position=media_position_start, clip_duration=clip_duration)


def adjust_track_event(event, start_position=None, clip_duration=None):
    """
    Adjusts a given event, to a specified duration
    :param event: Given Vegas Event
    :param start_position: Starting position in timeline of new event
    :param clip_duration: New duration of the clip
    """
    if clip_duration is None and start_position is None:
        return

    # set the default position
    if start_position is None:
        start_position = event.Start
    else:
        start_position = Timecode.FromMilliseconds(start_position)

    # set the default clip duration
    if clip_duration is None:
        clip_duration = event.Length
    else:
        clip_duration = Timecode.FromMilliseconds(clip_duration)

    event.AdjustStartLength(start_position, clip_duration, True)


def set_event_selection(event, selected: bool):
    """
    Set the selection of an specific event
    :param selected: Set if a event is selected or not
    """
    event.Selected = selected


def get_timeline_markers(pyVEGAS):
    """
    Returns a list of markers in milliseconds
    :param pyVEGAS: Vegas API variable
    :return: a List[(Positon in Milliseconds, Label as String),..]
    """
    return [(m.Position.ToMilliseconds(), m.Label) for m in pyVEGAS.Project.Markers]


def get_selected_events(pyVEGAS):
    """
    Returns a list of all selected events
    :param pyVEGAS: Vegas API variable
    :return: a List[(Track, Event),..]
    """
    tmp = []
    for track in pyVEGAS.Project.Tracks:
        for event in track.Events:
            if event.Selected:
                tmp.append((track, event))
    return tmp


def update_ui(pyVEGAS):
    """
    Updates the sony vegas ui
    :param pyVEGAS: vegas api variable
    """
    pyVEGAS.UpdateUI()


def get_cursor_position(pyVEGAS):
    """
    Retuns the current curser position
    :param pyVEGAS: vegas api variable
    :return: returns the position of the cursor
    """
    return pyVEGAS.Transport.CursorPosition.ToMilliseconds()
