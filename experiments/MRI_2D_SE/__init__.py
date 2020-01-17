from experiment import BaseExperiment  # required
from libraries.autophase import get_autophase
from scipy.signal import decimate

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
        del self.par_def['phase_GX']
        del self.par_def['phase_GY']
        del self.par_def['phase_GZ']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        phase_G_start = np.array([int(self.par['phase_GX_start']), int(self.par['phase_GY_start']), int(self.par['phase_GZ_start'])])
        phase_G_step = np.array([int(self.par['phase_GX_step']), int(self.par['phase_GY_step']), int(self.par['phase_GZ_step'])])
        phase_steps = int(self.par['phase_steps'])
        self.data = None
        for i in range(phase_steps):
            G = phase_G_start + i*phase_G_step
            if progress_handler is not None:
                progress_handler(i, phase_steps)
            self.programs['MRI_1D'].set_par('echo_shift', self.par['echo_shift'] + self.par['sample_shift'])
            self.programs['MRI_1D'].set_par('phase_GX', G[0])
            self.programs['MRI_1D'].set_par('phase_GY', G[1])
            self.programs['MRI_1D'].set_par('phase_GZ', G[2])
            await self.programs['MRI_1D'].run(progress_handler=None, message_handler=message_handler)
            run_data = self.programs['MRI_1D'].data.view(np.complex64)
            # self.data = np.append(self.data, np.max(np.abs(np.fft.fft(run_data))))
            if self.data is None:
                self.data = np.array([run_data])
            else:
                self.data = np.append(self.data, [run_data], axis=0)


    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        dwell_time = self.par['dwell_time']
        sample_shift = self.par['sample_shift']
        phase = get_autophase(self.data[int(self.par['phase_steps'])//2,:], t0=-0.5 * dwell_time * int(self.par['samples']) + sample_shift, dwelltime=dwell_time)
        export_data = self.data * np.exp(1j * phase)  # rotate
        export_data /= 1000000  # μV->V
        return {
            'real': export_data.real,
            'imag': export_data.imag,
            'unit': 'V'}

    def export_FT(self):
        y = self.autophase(self.raw_data()[-1,:])
        y = self.gaussian_apodize(y, self.par['gaussian_lb'])
        dwell_time = self.par['dwell_time']*0.000001  # μs->s
        sample_shift = self.par['sample_shift']*0.000001  # μs->s
        fft = np.fft.fftshift(np.fft.fft(y))
        freq = np.fft.fftshift(np.fft.fftfreq(y.size, d=dwell_time))
        fft *= np.exp(1j*2*np.pi*-(-0.5*dwell_time*len(y)+sample_shift)*freq)
        # sort the frequency axis
        #p = freq.argsort()
        #freq = freq[p]
        #fft = fft[p]
        fft /= 1000000  # μV->V
        fft *= dwell_time*1000  # V->V/kHz
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
        y = self.autophase(self.raw_data()[-1,:])
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
        y = self.autophase(self.raw_data()[-1, :])
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

    def plot_KSpace(self):
        data = self.raw_data()
        decimation = int(self.par['decimation'])
        data = decimate(data, decimation, axis=1)
        samples = int(self.par['samples'])//decimation
        dwell_time = self.par['dwell_time']
        phase_steps = int(self.par['phase_steps'])
        F_grad = np.linalg.norm([self.par['read_GX'], self.par['read_GY'], self.par['read_GZ']])
        P_grad_start = -np.linalg.norm(
            [self.par['phase_GX_start'], self.par['phase_GY_start'], self.par['phase_GZ_start']])
        P_grad_step = np.linalg.norm(
            [self.par['phase_GX_step'], self.par['phase_GY_step'], self.par['phase_GZ_step']])
        kx = F_grad*np.linspace(0, samples*dwell_time, samples, endpoint=False)
        kx-= kx[-1]/2 # start halfway
        ky = P_grad_start + np.linspace(0, phase_steps * P_grad_step, num=phase_steps, endpoint=False)
        norm_data = (data.real-np.min(data.real))/(np.max(data.real)-np.min(data.real))
        return {'data': [{
            'name': '',
            'type': 'image',
            'x': kx,
            'y': ky,
            'z': norm_data.ravel()}],
            'layout': {
                'title': 'K-Space',
                'xaxis': {'title': 'k_freq'},
                'yaxis': {'title': 'k_phase'}
            }}

    def plot_Image(self):
        data = self.raw_data()
        decimation = int(self.par['decimation'])
        data = decimate(data, decimation, axis=1)
        samples = int(self.par['samples']) // decimation
        phase_steps = int(self.par['phase_steps'])
        interp_ratio = int(self.par['interpolation'])
        if interp_ratio > 1:
            F_pad = np.zeros((((interp_ratio-1)*samples)//2, data.shape[0])).transpose()
            data = np.concatenate((F_pad, data, F_pad), axis=1)
            P_pad = np.zeros((((interp_ratio - 1) * phase_steps) // 2, data.shape[1]))
            data = np.concatenate((P_pad, data, P_pad), axis=0)
        image_data = np.abs(np.fft.fftshift(np.fft.fft2(np.fft.fftshift(data))))
        image_data = (image_data - np.min(image_data))/(np.max(image_data) - np.min(image_data))
        # TODO: calibrate x/y scale
        x = np.linspace(0, 1, samples*interp_ratio)
        y = np.linspace(0, 1, phase_steps*interp_ratio)
        return {'data': [{
            'name': '',
            'type': 'image',
            'x': x,
            'y': y,
            'z': image_data.ravel()}],
            'layout': {
                'title': 'Image',
                'xaxis': {'title': 'frequency encode dim.'},
                'yaxis': {'title': 'phase encode dim.'}
            }}

    def raw_data(self):
        return self.data.copy()

    def autophase(self, data):
        dwell_time = self.par['dwell_time']
        sample_shift = self.par['sample_shift']
        phase = get_autophase(data, t0=-0.5 * dwell_time * len(data) + sample_shift, dwelltime=dwell_time)
        return data * np.exp(1j * phase)  # rotate

    def gaussian_apodize(self, data, lb):
        t = np.abs(np.linspace(-1, 1, len(data), endpoint=True))
        return data * np.exp(-lb * lb * t * t)