"""Main."""
import sys
from datetime import timedelta

import pandas as pd
import mne
import mne.annotations
import pathlib

from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog

DEST = r'F:\Exports_SEEG\GOV_lar\GOV_lar.xlsx'
SHEET = r'GOV_lar'

def _get_annotations(raw, fname):
    """
    Read the edf and returns a df with annotations
    Args:
        raw: str, a valied path to an edf file
        fname: str, a valied path to the csv output

    Returns:
        dataframe with the annotations.

    """

    annotations = raw.annotations

    annotations_df = annotations.to_data_frame()
    annotations_df['fname'] = fname
    return annotations_df


def _save_annotations_to_file(annotations_df: pd.DataFrame ,dest: pathlib.Path, patient_id: str):
    """
    Saves the annotations to a file name.
    Args:
        df: the annotations dataframe
        dest: the destination to the file

    Returns:

    """
    with pd.ExcelWriter(dest.__str__()) as excelf:
        annotations_df.to_excel(excelf, sheet_name=patient_id)
        annotations_df.to_excel(excelf)


def _get_times(raw):
    start_time = raw.info['meas_date']
    num_samples = raw.n_times
    sampling_rate = raw.info['sfreq']
    # Make the start time timezone unaware
    start_time = start_time.replace(tzinfo=None)

    # Calculate the duration of the samples in seconds
    duration = num_samples / sampling_rate

    # Calculate the end time by adding the duration to the start time
    end_time = start_time + timedelta(seconds=duration)

    # Make the end time timezone unaware
    end_time = end_time.replace(tzinfo=None)

    # Create a Pandas Series with the start and end times
    data = {'start_time': [start_time], 'end_time': [end_time]}
    times = pd.DataFrame(data)


        # writer.save()

    return times

def _read_all_edf_in_root_folder(root: pathlib.Path):
    return root.glob('**/*.edf')

def main(argv):
    app = QApplication(argv)
    window = QWidget()
    # window.show()
    annotations_global = []
    times = []
    dirname = pathlib.Path(str(QFileDialog.getExistingDirectory(window, "Select edf dir")))
    annotations_file_full_path = dirname / f'{dirname.name}_annotations.xlsx'
    timing_file_full_path = dirname / f'{dirname.name}_timings.xlsx'

    sheet_name, res = QInputDialog.getText(window, "sheet name", dirname.name)
    if not res:
        sheet_name = 'sheet1'

    glob_edf = _read_all_edf_in_root_folder(pathlib.Path(dirname))
    for edf_file in glob_edf:
        try:
            fname = edf_file.name
            raw = mne.io.read_raw_edf(edf_file.__str__(), encoding='latin1')
            annotations_df = _get_annotations(raw, fname)
            annotations_global.append(annotations_df)
            print(edf_file, len(annotations_global))

            annotations_df_global = pd.concat(annotations_global)
            _save_annotations_to_file(annotations_df_global, annotations_file_full_path, sheet_name)

            _save_timing_to_file(raw, times, timing_file_full_path)

        except Exception:
            # df_error = pd.DataFrame.from_records([{'error':'annotation read error', 'fname':edf_file.name}])
            # _save_annotations_to_file(df_error, pathlib.Path(DEST), SHEET)
            print (f'read error {edf_file.name}')


    print('*' * 80)


def _save_timing_to_file(raw, times, timing_file_full_path):
    times.append(_get_times(raw))
    # Get the folder name from the file path
    folder_name = timing_file_full_path.parent.name
    global_times = pd.concat(times)
    # Write the Pandas Series to an Excel file
    with pd.ExcelWriter(timing_file_full_path, engine='openpyxl') as writer:
        global_times.to_excel(writer, sheet_name=folder_name)


if __name__=='__main__':
    main(sys.argv)
