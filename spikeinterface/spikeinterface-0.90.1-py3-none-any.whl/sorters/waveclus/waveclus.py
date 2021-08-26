from pathlib import Path
import os
from typing import Union
import sys
import copy
import json

from ..basesorter import BaseSorter
from ..utils import ShellScript

from spikeinterface.core import load_extractor, write_to_h5_dataset_format
from spikeinterface.extractors import WaveClusSortingExtractor
from spikeinterface.core.channelslicerecording import ChannelSliceRecording

PathType = Union[str, Path]

try:
    import h5py

    HAVE_H5PY = True
except ImportError:
    HAVE_H5PY = False


def check_if_installed(waveclus_path: Union[str, None]):
    if waveclus_path is None:
        return False
    assert isinstance(waveclus_path, str)

    if waveclus_path.startswith('"'):
        waveclus_path = waveclus_path[1:-1]
    waveclus_path = str(Path(waveclus_path).absolute())

    if (Path(waveclus_path) / 'wave_clus.m').is_file():
        return True
    else:
        return False


class WaveClusSorter(BaseSorter):
    """
    """

    sorter_name: str = 'waveclus'
    waveclus_path: Union[str, None] = os.getenv('WAVECLUS_PATH', None)
    requires_locations = False

    _default_params = {
        'detect_threshold': 5,
        'detect_sign': -1,  # -1 - 1 - 0
        'feature_type': 'wav',
        'scales': 4,
        'min_clus': 20,
        'maxtemp': 0.251,
        'template_sdnum': 3,
        'enable_detect_filter': True,
        'enable_sort_filter': True,
        'detect_filter_fmin': 300,
        'detect_filter_fmax': 3000,
        'detect_filter_order': 4,
        'sort_filter_fmin': 300,
        'sort_filter_fmax': 3000,
        'sort_filter_order': 2,
        'mintemp': 0,
        'w_pre': 20,
        'w_post': 44,
        'alignment_window': 10,
        'stdmax': 50,
        'max_spk': 40000,
        'ref_ms': 1.5,
        'interpolation': True,
        'keep_good_only': True,
        'chunk_memory': '500M'
    }

    _params_description = {
        'detect_threshold': "Threshold for spike detection",
        'detect_sign': "Use -1 (negative), 1 (positive), or 0 (both) depending "
                       "on the sign of the spikes in the recording",
        'feature_type': "wav (for wavelets) or pca, type of feature extraction applied to the spikes",
        'scales': "Levels of the wavelet decomposition used as features",
        'min_clus': "Minimum increase of cluster sizes used by the peak selection on the temperature map",
        'maxtemp': "Maximum temperature calculated by the SPC method",
        'template_sdnum': "Maximum distance (in total variance of the cluster) from the mean waveform to force a "
                          "spike into a cluster",
        'enable_detect_filter': "Enable or disable filter on detection",
        'enable_sort_filter': "Enable or disable filter on sorting",
        'detect_filter_fmin': "High-pass filter cutoff frequency for detection",
        'detect_filter_fmax': "Low-pass filter cutoff frequency for detection",
        'detect_filter_order': "Order of the detection filter",
        'sort_filter_fmin': "High-pass filter cutoff frequency for sorting",
        'sort_filter_fmax': "Low-pass filter cutoff frequency for sorting",
        'sort_filter_order': "Order of the sorting filter",
        'mintemp': "Minimum temperature calculated by the SPC algorithm",
        'w_pre': "Number of samples from the beginning of the spike waveform up to (including) the peak",
        'w_post': "Number of samples from the peak (excluding it) to the end of the waveform",
        'alignment_window': "Number of samples between peaks of different channels",
        'stdmax': "The events with a value over this number of noise standard deviations will be discarded",
        'max_spk': "Maximum number of spikes used by the SPC algorithm",
        'ref_ms': "Refractory time in milliseconds, all the threshold crossing inside this period are detected as the "
                  "same spike",
        'interpolation': "Enable or disable interpolation to improve the alignments of the spikes",
        'keep_good_only': "If True only 'good' units are returned",
        'chunk_memory': 'Chunk size in Mb to write h5 file (default 500Mb)'
    }

    sorter_description = """Wave Clus combines a wavelet-based feature extraction and paramagnetic clustering with a 
    template-matching approach. It is mainly designed for monotrodes and low-channel count probes. 
    For more information see https://doi.org/10.1152/jn.00339.2018"""

    installation_mesg = """\nTo use WaveClus run:\n
        >>> git clone https://github.com/csn-le/wave_clus
    and provide the installation path by setting the WAVECLUS_PATH
    environment variables or using WaveClusSorter.set_waveclus_path().\n\n

    More information on WaveClus at:
        https://github.com/csn-le/wave_clus/wiki
    """

    @classmethod
    def is_installed(cls):
        return check_if_installed(cls.waveclus_path)

    @classmethod
    def get_sorter_version(cls):
        p = os.getenv('WAVECLUS_PATH', None)
        if p is None:
            return 'unknown'
        else:
            with open(str(Path(p) / 'version.txt'), mode='r', encoding='utf8') as f:
                version = f.readline()
        return version

    @classmethod
    def set_waveclus_path(cls, waveclus_path: PathType):
        waveclus_path = str(Path(waveclus_path).absolute())
        WaveClusSorter.waveclus_path = waveclus_path
        try:
            print("Setting WAVECLUS_PATH environment variable for subprocess calls to:", waveclus_path)
            os.environ["WAVECLUS_PATH"] = waveclus_path
        except Exception as e:
            print("Could not set WAVECLUS_PATH environment variable:", e)

    @classmethod
    def _check_apply_filter_in_params(cls, params):
        return (params['enable_detect_filter'] or params['enable_sort_filter'])

    @classmethod
    def _setup_recording(cls, recording, output_folder, params, verbose):
        # Generate mat files in the dataset directory
        for nch, id in enumerate(recording.get_channel_ids()):
            vcFile_h5 = str(output_folder / ('raw' + str(nch + 1) + '.h5'))
            with h5py.File(vcFile_h5, mode='w') as f:
                f.create_dataset(
                    "sr", data=[recording.get_sampling_frequency()], dtype='float32')
                rec_sliced = ChannelSliceRecording(recording, channel_ids=[id])
                write_to_h5_dataset_format(rec_sliced, dataset_path='/data', segment_index=0,
                                           file_handle=f, time_axis=0, single_axis=True,
                                           chunk_memory=params['chunk_memory'])

        if verbose:
            samplerate = recording.get_sampling_frequency()
            num_timepoints = recording.get_num_frames(segment_index=0)
            num_channels = recording.get_num_channels()
            duration_minutes = num_timepoints / samplerate / 60
            print('Num. channels = {}, Num. timepoints = {}, duration = {} minutes'.format(
                num_channels, num_timepoints, duration_minutes))

    @classmethod
    def _run_from_folder(cls, output_folder, params, verbose):
        source_dir = Path(__file__).parent

        p = params.copy()
        if p['detect_sign'] < 0:
            p['detect_sign'] = 'neg'
        elif p['detect_sign'] > 0:
            p['detect_sign'] = 'pos'
        else:
            p['detect_sign'] = 'both'

        if not p['enable_detect_filter']:
            p['detect_filter_order'] = 0
        del p['enable_detect_filter']

        if not p['enable_sort_filter']:
            p['sort_filter_order'] = 0
        del p['enable_sort_filter']

        if p['interpolation']:
            p['interpolation'] = 'y'
        else:
            p['interpolation'] = 'n'

        tmpdir = output_folder

        par_str = ''
        par_renames = {'detect_sign': 'detection', 'detect_threshold': 'stdmin',
                       'feature_type': 'features', 'detect_filter_fmin': 'detect_fmin',
                       'detect_filter_fmax': 'detect_fmax', 'detect_filter_order': 'detect_order',
                       'sort_filter_fmin': 'sort_fmin', 'sort_filter_fmax': 'sort_fmax',
                       'sort_filter_order': 'sort_order'}
        for key, value in p.items():
            if type(value) == str:
                value = '\'{}\''.format(value)
            elif type(value) == bool:
                value = '{}'.format(value).lower()
            if key in par_renames:
                key = par_renames[key]
            par_str += 'par.{} = {};\n'.format(key, value)

        if verbose:
            print('Running waveclus in {tmpdir}...'.format(tmpdir=tmpdir))
        matlab_code = _matlab_code.format(waveclus_path=WaveClusSorter.waveclus_path,
                                          source_path=source_dir,
                                          tmpdir=tmpdir.absolute(),
                                          parameters=par_str)

        with (output_folder / 'run_waveclus.m').open('w') as f:
            f.write(matlab_code)

        if 'win' in sys.platform and sys.platform != 'darwin':
            shell_cmd = '''
                {disk_move}
                cd {tmpdir}
                matlab -nosplash -wait -log -r run_waveclus
            '''.format(disk_move=str(tmpdir.absolute())[:2], tmpdir=tmpdir)
        else:
            shell_cmd = '''
                #!/bin/bash
                cd "{tmpdir}"
                matlab -nosplash -nodisplay -log -r run_waveclus
            '''.format(tmpdir=tmpdir)
        shell_cmd = ShellScript(shell_cmd, script_path=output_folder / f'run_{cls.sorter_name}',
                                log_path=output_folder / f'{cls.sorter_name}.log', verbose=verbose)
        shell_cmd.start()
        retcode = shell_cmd.wait()

        if retcode != 0:
            raise Exception('waveclus returned a non-zero exit code')

        result_fname = tmpdir / 'times_results.mat'
        if not result_fname.is_file():
            raise Exception(f'Result file does not exist: {result_fname}')

    @classmethod
    def _get_result_from_folder(cls, output_folder):
        output_folder = Path(output_folder)
        result_fname = str(output_folder / 'times_results.mat')

        output_folder = Path(output_folder)
        with (output_folder / 'spikeinterface_params.json').open('r') as f:
            sorter_params = json.load(f)['sorter_params']
        keep_good_only = sorter_params.get('keep_good_only', True)
        sorting = WaveClusSortingExtractor(
            file_path=result_fname, keep_good_only=keep_good_only)
        return sorting


_matlab_code = '''
addpath(genpath('{waveclus_path}'));
addpath(genpath('{source_path}'));
{parameters}
try
    p_waveclus('{tmpdir}', par);
catch
    fprintf('----------------------------------------');
    fprintf(lasterr());
    quit(1);
end
quit(0);
'''
