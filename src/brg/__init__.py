"""This is the introductory text for the ``brg`` section in the documentation page
'reference.rst'.
"""


import os
import warnings


DATA = os.path.abspath(os.path.join(__file__, '../../../data'))


def get_full_datafile_path(filename):
    filename = filename.strip('/')
    return os.path.abspath(os.path.join(DATA, filename))


def get_data(filename):
    warnings.warn(
        'This function is deprecated. Use "brg.get_full_datafile_path(filename)" instead.'
    )
    return get_full_datafile_path(filename)


def get_all_datafile_paths():
    return os.listdir(DATA)


def check_dependencies():
    raise NotImplementedError


docs = [
    {'com': []},
    {'datastructures': []},
    # {'files': []},
    # {'geometry': []},
    {'numerical': []},
    # {'physics': []},
     {'utilities': []},
    # {'viewers': []},
]
