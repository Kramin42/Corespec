from experiment import BaseExperiment  # required
from libraries.autophase import get_autophase
from libraries.optimisation import nelder_mead_async

# for debugging
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

import numpy as np


# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment):  # must be named 'Experiment'
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        self.data = None
        self.shims = np.array([int(self.par['MRI_shim_X']),
                               int(self.par['MRI_shim_Y']),
                               int(self.par['MRI_shim_Z'])])

        shim_step = int(self.par['shim_step'])
        precision = int(self.par['precision'])
        init_step = [shim_step, shim_step, shim_step]
        precision = [precision, precision, precision]
        max_iterations = int(self.par['max_iterations'])
        if progress_handler is not None:
            progress_handler(0, max_iterations)

        async def evalfunc(try_shims):
            logger.debug('Trying (X: %d, Y: %d, Z: %d)' %
                         tuple(try_shims.tolist()))
            self.programs['FID'].set_par('MRI_shim_X', try_shims[0])
            self.programs['FID'].set_par('MRI_shim_Y', try_shims[1])
            self.programs['FID'].set_par('MRI_shim_Z', try_shims[2])
            await self.programs['FID'].run(progress_handler=None,
                                           message_handler=message_handler)
            self.data = self.programs['FID'].data.view(np.complex64)
            y = self.gaussian_apodize(self.data, self.par['gaussian_lb'])
            result = np.sum(np.abs(y) ** 2)
            logger.debug('SumSq: %d' % result)
            return -result

        lower_bounds = [-32768] * 3
        upper_bounds = [32767] * 3
        self.opt_res = []
        try:
            iter = 0
            async for r in nelder_mead_async(evalfunc, self.shims, x_lb=lower_bounds, x_ub=upper_bounds,
                                             max_iter=max_iterations, step=init_step, x_precision=precision,
                                             message_handler=message_handler):
                self.opt_res.append(r)
                logger.debug(
                    'Best Shims So Far: (X: %d, Y: %d, Z: %d)' % tuple(
                        r[0].tolist()))
                iter += 1
                progress_handler(iter, max_iterations)
        except:
            raise
        finally:
            message_handler('Final Shims: (X: %d, Y: %d, Z: %d)' %
                            tuple(self.opt_res[-1][0].tolist()))

    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        y = self.autophase(self.raw_data())
        y = self.gaussian_apodize(y, self.par['gaussian_lb'])
        x = np.linspace(0, self.par['dwell_time'] * len(y), len(y), endpoint=False)
        y /= 1000000  # μV->V
        x /= 1000000  # μs->s
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'y_mag': np.abs(y),
            'y_unit': 'V',
            'x_unit': 's'}

    def export_FT(self):
        y = self.autophase(self.raw_data())
        y = self.gaussian_apodize(y, self.par['gaussian_lb'])
        dwell_time = self.par['dwell_time'] * 1e-6  # us->s
        fft = np.fft.fft(y)
        freq = np.fft.fftfreq(y.size, d=dwell_time)
        # sort the frequency axis
        p = freq.argsort()
        freq = freq[p]
        fft = fft[p]
        fft /= 1000000  # uV->V
        fft *= dwell_time * 1000  # V->V/kHz
        return {
            'freq': freq,
            'fft_real': fft.real,
            'fft_imag': fft.imag,
            'fft_mag': np.abs(fft),
            'fft_unit': 'V/kHz',
            'freq_unit': 'Hz'}

    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_Raw(self):
        data = self.export_Raw()
        # return object according to plotly schema
        return {'data': [{
            'name': 'Real',
            'type': 'scatter',
            'x': data['x'],
            'y': data['y_real']}, {
            'name': 'Imag.',
            'type': 'scatter',
            'x': data['x'],
            'y': data['y_imag']}, {
            'name': 'Mag.',
            'type': 'scatter',
            'x': data['x'],
            'y': data['y_mag']}],
            'layout': {
                'title': 'Real/Imaginary data',
                'xaxis': {'title': data['x_unit']},
                'yaxis': {'title': data['y_unit']}
            }}

    def plot_Phase(self):
        y = self.autophase(self.raw_data())
        x = np.linspace(0, self.par['dwell_time'] * len(y), len(y), endpoint=False)
        x /= 1000000  # us->s

        # return object according to plotly schema
        return {'data': [{
            'name': '',
            'type': 'scatter',
            'x': x,
            'y': np.angle(y)}],
            'layout': {
                'title': 'Phase',
                'xaxis': {'title': 's'},
                'yaxis': {'title': 'rad'}
            }}

    def plot_FT(self):
        data = self.export_FT()
        peak_index = np.argmax(data['fft_mag'])
        peak_freq_offset = data['freq'][peak_index] / 1000000  # in MHz
        avg_start = peak_index - int(len(data['freq']) / 20)
        avg_end = peak_index + int(len(data['freq']) / 20) + 1
        if avg_start > 0 and avg_end <= len(data['freq']):
            peak_freq_offset = np.average(data['freq'][avg_start:avg_end],
                                          weights=np.square(data['fft_mag'][avg_start:avg_end])) / 1000000  # in MHz
        peak_freq = self.par['freq'] + peak_freq_offset
        height = data['fft_real'].max()
        left_hw_index = -1
        right_hw_index = -1
        for i, x in enumerate(data['fft_real']):
            if x > height / 2:
                if left_hw_index == -1:
                    left_hw_index = i
                right_hw_index = i
        half_width = data['freq'][right_hw_index] - data['freq'][left_hw_index]
        return {'data': [{
            'name': 'Real',
            'type': 'scatter',
            'x': data['freq'],
            'y': data['fft_real']}, {
            'name': 'Imag.',
            'type': 'scatter',
            'x': data['freq'],
            'y': data['fft_imag']}, {
            'name': 'Mag.',
            'type': 'scatter',
            'x': data['freq'],
            'y': data['fft_mag']}],
            'layout': {
                'title': 'FFT (peak@{:0.4f}{}, height: {:0.4f} uV, 50% width: {:.0f} Hz)'.format(peak_freq, 'M' + data[
                    'freq_unit'], height * 1000000, half_width),
                'xaxis': {'title': data['freq_unit']},
                'yaxis': {'title': data['fft_unit']}
            }}

    def plot_SumSq(self):
        x = []
        y = []
        for i, res in enumerate(self.opt_res):
            x.append(i)
            y.append(-res[1])

        return {'data': [{
            'name': '',
            'type': 'scatter',
            'x': np.array(x, dtype=np.float),
            'y': np.array(y, dtype=np.float)}],
            'layout': {
                'title': 'Autoshim Progress (X: %d, Y: %d, Z: %d)' % tuple(self.opt_res[-1][0].tolist()),
                'xaxis': {'title': 'Iteration'},
                'yaxis': {'title': 'Best Sum of Squares'}
            }}

    def raw_data(self):
        if self.data is None:
            raise Exception('Data is not ready to be read!')
        return self.data.view(np.complex64)

    def autophase(self, data):
        phase = get_autophase(data)
        return data * np.exp(1j * phase)  # rotate

    def gaussian_apodize(self, data, lb):
        t = np.linspace(0, 1, len(data))
        return data * np.exp(-lb * lb * t * t)
