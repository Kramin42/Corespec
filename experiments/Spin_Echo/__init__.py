from experiment import BaseExperiment # required

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
        await self.programs['SpinEcho'].run(progress_handler=progress_handler,
                                       message_handler=message_handler)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        y = self.autophase(self.raw_data())
        x = np.linspace(-0.5*self.par['dwell_time']*len(y), 0.5*self.par['dwell_time']*len(y), len(y), endpoint=False)
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
        y = np.fft.ifftshift(self.autophase(self.raw_data()))
        dwell_time = self.par['dwell_time']*0.000001  # μs->s
        fft = np.fft.fftshift(np.fft.fft(y))
        freq = np.fft.fftshift(np.fft.fftfreq(y.size, d=dwell_time))
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
        x = np.linspace(0, self.par['dwell_time']*len(y), len(y), endpoint=False)
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
        peak_index = np.argmax(data['fft_mag'])
        peak_freq_offset = data['freq'][peak_index]/1000000  # in MHz
        avg_start = peak_index - int(len(data['freq'])/20)
        avg_end = peak_index + int(len(data['freq'])/20) + 1
        if avg_start>0 and avg_end<=len(data['freq']):
            peak_freq_offset = np.average(data['freq'][avg_start:avg_end], weights=np.square(data['fft_mag'][avg_start:avg_end]))/1000000  # in MHz
        peak_freq = self.par['freq'] + peak_freq_offset
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
                'title': 'FFT (peak@{:0.4f}{})'.format(peak_freq, 'M'+data['freq_unit']),
                'xaxis': {'title': data['freq_unit']},
                'yaxis': {'title': data['fft_unit']}
            }}

    def raw_data(self):
        data = self.programs['SpinEcho'].data
        data = data.view(np.complex64)
        return data

    def autophase(self, data):
        phase = np.angle(np.sum(data)) # get average phase
        return data * np.exp(1j * -phase) # rotate
