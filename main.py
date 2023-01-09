"""Main."""
import os
import logging
import sys
from datetime import timedelta
import numpy as np
import pandas as pd
import mne
import mne.annotations
import pathlib

from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog
from PyQt5 import uic

from bokeh.plotting import figure
from bokeh.io import output_file, show

def _get_annotations(raw, edf_file):
    """
    Read the edf and returns a df with annotations
    Args:
        raw: str, a valied path to an edf file
        fname: str, a valied path to the csv output

    Returns:
        dataframe with the annotations.

    """
    fname = edf_file.name
    annotations = raw.annotations

    annotations_df = annotations.to_data_frame()
    annotations_df['fname'] = fname
    annotations_df['folder_name'] = edf_file.parent.name
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
    basedir = pathlib.Path(os.path.dirname(__file__))
    window = uic.loadUi(basedir / "ui/main_window.ui")  # QWidget()
    annotations_global = []
    times = []
    dirname = pathlib.Path(str(QFileDialog.getExistingDirectory(window, "Select edf dir", '', QFileDialog.DontUseNativeDialog)))
    annotations_file_full_path = dirname / f'{dirname.name}_annotations.xlsx'
    timing_file_full_path = dirname / f'{dirname.name}_timings.xlsx'

    # sheet_name, res = QInputDialog.getText(window, "sheet name", dirname.name)
    # if not res:
    #     sheet_name = 'sheet1'

    glob_edf = _read_all_edf_in_root_folder(pathlib.Path(dirname))
    for edf_file in glob_edf:
        try:
            raw = mne.io.read_raw_edf(edf_file.__str__(), encoding='latin1')
            annotations_df = _get_annotations(raw, edf_file)
            annotations_global.append(annotations_df)
            print(edf_file, len(annotations_global))

            annotations_df_global = pd.concat(annotations_global)
            _save_annotations_to_file(annotations_df_global, annotations_file_full_path, edf_file.parent.name)

            files_times = _save_timing_to_file(raw, times, timing_file_full_path)

            expand_time = get_samples(files_times, 10)


        except Exception:
            # df_error = pd.DataFrame.from_records([{'error':'annotation read error', 'fname':edf_file.name}])
            # _save_annotations_to_file(df_error, pathlib.Path(DEST), SHEET)
            logging.error(f'read error {edf_file.name}')
            app.closeAllWindows()

    logging.info('post loop')
    split_and_save(annotations_df_global, annotations_file_full_path)
    plot_guntt(dirname, expand_time)
    annotations_df_global = pd.concat(annotations_global)

    print('*' * 80)
    window.exec_()
    app.closeAllWindows()

def plot_guntt(dirname, expand_time):
    fig = figure(output_backend="webgl", title=dirname.name, height=200, width=900)
    fig_x = expand_time
    fig_y = np.arange(len(expand_time))
    fig.circle(y=fig_x, x=fig_y, radius=10)
    output_file(dirname / f'{dirname.name}_guntt.html')
    show(fig)


def _save_timing_to_file(raw, times, timing_file_full_path):
    new_times = _get_times(raw)
    new_times['fname'] = pathlib.Path(raw.filenames[0]).name
    times.append(new_times)
    # Get the folder name from the file path
    folder_name = timing_file_full_path.parent.name
    global_times = pd.concat(times)
    # Write the Pandas Series to an Excel file
    with pd.ExcelWriter(timing_file_full_path, engine='openpyxl') as writer:
        global_times.to_excel(writer, sheet_name=folder_name)

    return global_times


def get_samples(df, sampling_rate):
    # Create an empty list to store the samples
    samples = []

    # Iterate through each row of the DataFrame
    for index, row in df.iterrows():
        # Get the start and end times
        start_time = row['start_time']
        end_time = row['end_time']

        # Calculate the number of samples
        num_samples = int((end_time - start_time).total_seconds() * sampling_rate)

        # Generate the samples
        t = np.linspace(start_time.timestamp(), end_time.timestamp(), num_samples)
        samples.extend(t)

    # Convert the samples to a NumPy array
    samples = np.array(samples)

    return samples

def split_and_save(df, file_path):
    # Group the data by the data_folder field
    groups = df.groupby('folder_name')

    # Create an Excel writer
    writer = pd.ExcelWriter(file_path, engine='openpyxl')

    # Loop through the groups and save each group to a separate spreadsheet
    for name, group in groups:
        group.to_excel(writer, sheet_name=name, index=False)

    # Save the Excel file
    writer.save()



if __name__=='__main__':
    main(sys.argv)
