"""Main."""
import sys

import pandas as pd
import mne
import mne.annotations
import pathlib

from datetime import timedelta


from PyQt5.QtWidgets import QFileDialog, QWidget, QApplication

SOURCE = r'E:\assuta\data\SEEG'
DEST = r'E:\assuta\data\SEEG'

def _get_annotations(source, dest: str = ''):
    """
    Read the edf and returns a df with annotations
    Args:
        source: str, a valied path to an edf file
        dest: str, a valied path to the csv output

    Returns:
        dataframe with the annotations.

    """

    r = mne.io.read_raw_edf(source, encoding='latin1')

    annotations = r.annotations

    annotations_df = annotations.to_data_frame()
    return annotations_df, r


def _save_annotations_to_file(annotations_df: pd.DataFrame ,dest: pathlib.Path, patient_id: str):
    """
    Saves the annotations to a file name.
    Args:
        df: the annotations dataframe
        dest: the destination to the file

    Returns:

    """
    with pd.ExcelWriter(dest / f'{patient_id}.xlsx', mode='a') as excelf:
        annotations_df.to_excel(excelf)


def get_times(start_time, num_samples, sampling_rate, file_path):
    # Make the start time timezone unaware
    start_time = start_time.replace(tzinfo=None)

    # Calculate the duration of the samples in seconds
    duration = num_samples / sampling_rate

    # Calculate the end time by adding the duration to the start time
    end_time = start_time + timedelta(seconds=duration)

    # Make the end time timezone unaware
    end_time = end_time.replace(tzinfo=None)

    # Create a Pandas Series with the start and end times
    times = pd.Series([start_time, end_time], index=['start_time', 'end_time'])

    # Get the folder name from the file path
    folder_name = file_path.parent.name

    # Write the Pandas Series to an Excel file
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    times.to_excel(writer, sheet_name=folder_name)
    writer.save()


def _read_all_edf_in_root_folder(root: pathlib.Path):
    return root.glob('**/*.edf')

def main(argv):
    app = QApplication(argv)
    window = QWidget()
    # window.show()
    dirname = str(QFileDialog.getExistingDirectory(window, "Select edf dir", SOURCE))
    glob_edf = _read_all_edf_in_root_folder(pathlib.Path(dirname))
    for edf_file in glob_edf:
        annotations_df, obj = _get_annotations(edf_file.__str__())
        get_times(obj.info['meas_date'], obj.n_times, obj.info['sfreq'], pathlib.Path(dirname) / 'timings.xlsx')
        _save_annotations_to_file(annotations_df, pathlib.Path(dirname), 'patient1')

if __name__=='__main__':
    main(sys.argv)
