from experiment import BaseExperiment # required

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy as np

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None):
        await self.programs['Noise'].run(progress_handler=progress_handler)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Noise(self):
        y = self.raw_data()
        x = np.linspace(0, 0.5*len(y), len(y), endpoint=False)
        return {
            'x': x.tolist(),
            'y_real': y.real.tolist(),
            'y_imag': y.imag.tolist(),
            'rms': np.sqrt(np.mean(np.abs(y)**2)).item(),
            'y_unit': 'μV',
            'x_unit': 'μs'}

    def export_FFT(self):
        y = self.raw_data()
        fft = np.fft.fft(y)
        freq = np.fft.fftfreq(y.size, d=self.par['dwell_time']*0.001)
        # sort the frequency axis
        p = freq.argsort()
        freq = freq[p]
        fft = fft[p]
        return {
            'freq': freq.tolist(),
            'fft_real': fft.real.tolist(),
            'fft_imag': fft.imag.tolist(),
            'fft_unit': 'μV',
            'freq_unit': 'kHz'}
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_Noise(self):
        data = self.export_Noise()
        # return object according to plotly schema
        return {'data': [{
                    'name': 'Real',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y_real']}, {
                    'name': 'Imag',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y_imag']}],
                'layout': {
                    'title': 'Noise, RMS: {:0.2f}{}'.format(data['rms'], data['y_unit']),
                    'xaxis': {'title': data['x_unit']},
                    'yaxis': {'title': data['y_unit']}
                }}

    def plot_FFT(self):
        data = self.export_FFT()
        return {'data': [{
            'name': 'Real',
            'type': 'scatter',
            'x': data['freq'],
            'y': data['fft_real']}, {
            'name': 'Imag',
            'type': 'scatter',
            'x': data['freq'],
            'y': data['fft_imag']}],
            'layout': {
                'title': 'FFT',
                'xaxis': {'title': data['freq_unit']},
                'yaxis': {'title': data['fft_unit']}
            }}

    def raw_data(self):
        data = self.programs['Noise'].data
        return data.astype(np.float32).view(np.complex64)
