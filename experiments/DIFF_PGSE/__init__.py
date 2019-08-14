from experiment import BaseExperiment  # required
from libraries.autophase import get_autophase

# for debugging
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np


# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment):  # must be named 'Experiment'
    def override(self):
        del self.par_def['phase_grad']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        grads = np.linspace(0, int(self.par['max_grad']), int(self.par['grad_steps']), endpoint=True)
        self.data = np.zeros((grads, int(self.par['samples'])), dtype=np.complex64)
        self.last_index = None
        for i,G in enumerate(grads):
            if progress_handler is not None:
                progress_handler(i, len(grads))
            self.programs['DIFF_PGSE'].set_par('phase_grad', G)
            self.programs['DIFF_PGSE'].set_par('echo_shift', self.par['echo_shift'] + self.par['sample_shift'])
            await self.programs['DIFF_PGSE'].run(progress_handler=None, message_handler=message_handler)
            self.data[i] = self.programs['DIFF_PGSE'].data.view(np.complex64)
            self.last_index = i


    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        dwell_time = self.par['dwell_time']
        sample_shift = self.par['sample_shift']
        samples = self.par['samples']
        phase = get_autophase(self.raw_data()[0,:], t0=-0.5 * dwell_time * samples + sample_shift, dwelltime=dwell_time)
        y = self.raw_data() * np.exp(1j * phase)  # rotate
        times = np.linspace(-0.5 * self.par['dwell_time'] * len(y) + self.par['sample_shift'],
                        0.5 * self.par['dwell_time'] * len(y) + self.par['sample_shift'], len(y), endpoint=False)
        grads = np.linspace(0, int(self.par['max_grad']), int(self.par['grad_steps']), endpoint=True)
        y /= 1000000  # μV->V
        times /= 1000000  # μs->s
        return {
            'time_axis': times,
            'grad_axis': grads,
            'y_real': y.real,
            'y_imag': y.imag,
            'y_unit': 'V',
            'time_unit': 's'}

    def export_FT(self):
        y = self.autophase(self.last_data())
        y = self.gaussian_apodize(y, self.par['gaussian_lb'])
        dwell_time = self.par['dwell_time'] * 0.000001  # μs->s
        sample_shift = self.par['sample_shift'] * 0.000001  # μs->s
        fft = np.fft.fftshift(np.fft.fft(y))
        freq = np.fft.fftshift(np.fft.fftfreq(y.size, d=dwell_time))
        fft *= np.exp(1j * 2 * np.pi * -(-0.5 * dwell_time * len(y) + sample_shift) * freq)
        # sort the frequency axis
        # p = freq.argsort()
        # freq = freq[p]
        # fft = fft[p]
        fft /= 1000000  # μV->V
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
        y = self.autophase(self.last_data())
        y = self.gaussian_apodize(y, self.par['gaussian_lb'])
        x = np.linspace(-0.5 * self.par['dwell_time'] * len(y) + self.par['sample_shift'],
                        0.5 * self.par['dwell_time'] * len(y) + self.par['sample_shift'], len(y), endpoint=False)
        y /= 1000000  # μV->V
        x /= 1000000  # μs->s
        # return object according to plotly schema
        return {'data': [{
            'name': 'Real',
            'type': 'scatter',
            'x': x,
            'y': y.real}, {
            'name': 'Imag.',
            'type': 'scatter',
            'x': x,
            'y': y.imag}, {
            'name': 'Mag.',
            'type': 'scatter',
            'x': x,
            'y': np.abs(y)}],
            'layout': {
                'title': 'Real/Imaginary data',
                'xaxis': {'title': 's'},
                'yaxis': {'title': 'V'}
            }}

    def plot_Phase(self):
        y = self.autophase(self.last_data())
        x = np.linspace(-0.5 * self.par['dwell_time'] * len(y) + self.par['sample_shift'],
                        0.5 * self.par['dwell_time'] * len(y) + self.par['sample_shift'], len(y), endpoint=False)
        x /= 1000000  # μs->s

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
                'title': 'FFT',
                'xaxis': {'title': data['freq_unit']},
                'yaxis': {'title': data['fft_unit']}
            }}

    def raw_data(self):
        return self.data

    def last_data(self):
        return self.data[self.last_index, :]

    def autophase(self, data):
        dwell_time = self.par['dwell_time']
        sample_shift = self.par['sample_shift']
        phase = get_autophase(data, t0=-0.5 * dwell_time * len(data) + sample_shift, dwelltime=dwell_time)
        return data * np.exp(1j * phase)  # rotate

    def gaussian_apodize(self, data, lb):
        t = np.abs(np.linspace(-1, 1, len(data), endpoint=True))
        return data * np.exp(-lb * lb * t * t)
