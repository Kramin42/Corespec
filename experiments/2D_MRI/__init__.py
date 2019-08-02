from experiment import BaseExperiment # required
from libraries.autophase import get_autophase

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        self.programs['2DMRI'].set_par('echo_shift', self.par['echo_shift'] + self.par['sample_shift'])
        await self.programs['2DMRI'].run(progress_handler=progress_handler,
                                       message_handler=message_handler)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        y = self.autophase(self.raw_data())
        y = self.gaussian_apodize(y, self.par['gaussian_lb'])
        x = np.linspace(-0.5*self.par['dwell_time']*len(y)+self.par['sample_shift'], 0.5*self.par['dwell_time']*len(y)+self.par['sample_shift'], len(y), endpoint=False)
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

    # def export_default(self):
    #     return self.export_Raw()
    
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
        x = np.linspace(-0.5*self.par['dwell_time']*len(y)+self.par['sample_shift'], 0.5*self.par['dwell_time']*len(y)+self.par['sample_shift'], len(y), endpoint=False)
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
        data = self.programs['2DMRI'].data
        data = data.view(np.complex64)
        return data

    def autophase(self, data):
        dwell_time = self.par['dwell_time']
        sample_shift = self.par['sample_shift']
        phase = get_autophase(data, t0=-0.5*dwell_time*len(data)+sample_shift, dwelltime=dwell_time)
        return data * np.exp(1j * phase)  # rotate

    def gaussian_apodize(self, data, lb):
        t = np.abs(np.linspace(-1, 1, len(data), endpoint=True))
        return data * np.exp(-lb*lb*t*t)