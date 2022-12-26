"""Main."""
import sys

import pandas as pd
import mne
import mne.annotations
import pathlib

SOURCE = r'D:\Documents\EEG Studies\isa.edf'
DEST = r'D:\Documents\EEG Studies\isa.xlsx'

def _get_annotations(source, dest: str = ''):
    """
    Read the edf and returns a df with annotations
    Args:
        source: str, a valied path to an edf file
        dest: str, a valied path to the csv output

    Returns:
        dataframe with the annotations.

    """

    r = mne.io.read_raw_edf(source)

    annotations = r.annotations

    annotations_df = annotations.to_data_frame()
    return annotations_df


def _save_annotations_to_file(annotations_df: pd.DataFrame ,dest: pathlib.Path, patient_id: str):
    """
    Saves the annotations to a file name.
    Args:
        df: the annotations dataframe
        dest: the destination to the file

    Returns:

    """
    with dest.open('a') as excelf:
        annotations_df.to_excel(excelf, sheet=patient_id)

def _read_all_edf_in_root_folder(root: pathlib.Path):
    return root.glob('*/**.edf')

def main(argv):
    glob_edf = _read_all_edf_in_root_folder(pathlib.Path(SOURCE))
    for edf_file in glob_edf:
        annotations_df = _get_annotations(edf_file.__str__())
        _save_annotations_to_file(annotations_df, pathlib.Path(DEST), 'patient1')

if __name__=='__main__':
    main(sys.argv)
