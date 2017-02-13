import os
import inspect

from brg_rhino.forms.text import TextForm
from brg_rhino.forms.image import ImageForm

try:
    import System
    import Rhino
    import rhinoscriptsyntax as rs
    from Rhino.UI.Dialogs import ShowPropertyListBox
    from Rhino.UI.Dialogs import ShowMessageBox

except ImportError as e:
    import platform
    if platform.system() == 'Windows':
        raise e


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = [
    'wait', 'get_tolerance', 'toggle_toolbargroup', 'pick_point',
    'browse_for_folder', 'browse_for_file',
    'print_display_on',
    'display_message', 'display_text', 'display_image', 'display_html',
    'update_settings', 'update_attributes', 'update_named_values',
]


# ==============================================================================
# Truly miscellaneous :)
# ==============================================================================


def add_gui_helpers(helpers, overwrite=False, protected=False):
    def decorate(cls):
        # attr = {}
        for helper in helpers:
            # for name, value in helper.__dict__.items():
            for name, value in inspect.getmembers(helper):
                # magic methods
                if name.startswith('__') and name.endswith('__'):
                    continue
                # protected / private methods
                if not protected and name.startswith('_'):
                    continue
                # existing methods
                if not overwrite:
                    if hasattr(cls, name):
                        continue
                # attr[name] = value
                # try:
                #     setattr(cls, name, value.__func__)
                # except:
                #     setattr(cls, name, value)
                # inspect.ismethoddescriptor
                # inspect.isdatadescriptor
                if inspect.ismethod(value):
                    setattr(cls, name, value.__func__)
                else:
                    setattr(cls, name, value)
        # cls = type(cls.__name__, (cls, ), attr)
        return cls
    return decorate


def wait():
    return Rhino.RhinoApp.Wait()


def get_tolerance():
    return rs.UnitAbsoluteTolerance()


def toggle_toolbargroup(rui, group):
    if not os.path.exists(rui) or not os.path.isfile(rui):
        return
    collection = rs.IsToolbarCollection(rui)
    if not collection:
        collection = rs.OpenToolbarCollection(rui)
        if rs.IsToolbar(collection, group, True):
            rs.ShowToolbar(collection, group)
    else:
        if rs.IsToolbar(collection, group, True):
            if rs.IsToolbarVisible(collection, group):
                rs.HideToolbar(collection, group)
            else:
                rs.ShowToolbar(collection, group)


# pick a location
# get_location
def pick_point(message='Pick a point.'):
    point = rs.GetPoint(message)
    if point:
        return list(point)
    return None


# ==============================================================================
# File system
# ==============================================================================


def browse_for_folder(message=None, default=None):
    return rs.BrowseForFolder(folder=default, message=message, title='brg')


def browse_for_file(title=None, folder=None, filter=None):
    return rs.OpenFileName(title, filter=filter, folder=folder)


# ==============================================================================
# Display
# ==============================================================================


def print_display_on(on=True):
    if on:
        rs.Command('_PrintDisplay State On Color Display Thickness 1 _Enter')
    else:
        rs.Command('_PrintDisplay State Off _Enter')


def display_message(message):
    return ShowMessageBox(message, 'Message')


def display_text(text, title='Text', width=800, height=600):
    if isinstance(text, (list, tuple)):
        text = '{0}'.format(System.Environment.NewLine).join(text)
    form = TextForm(text, title, width, height)
    return form.show()


def display_image(image, title='Image', width=800, height=600):
    form = ImageForm(image, title, width, height)
    return form.show()


def display_html():
    raise NotImplementedError


# ==============================================================================
# Settings and attributes
# ==============================================================================


def update_settings(names, values, message='', title='Update settings'):
    return ShowPropertyListBox(message, title, names, values)


def update_attributes(names, values, message='', title='Update attributes'):
    return ShowPropertyListBox(message, title, names, values)


def update_named_values(names, values, message='', title='Update named values'):
    return ShowPropertyListBox(message, title, names, values)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    pass
