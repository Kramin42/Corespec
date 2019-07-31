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
        self.shims = np.array([int(self.par['shim_X']),
                               int(self.par['shim_Y']),
                               int(self.par['shim_Z']),
                               int(self.par['shim_Z2']),
                               int(self.par['shim_ZX']),
                               int(self.par['shim_ZY']),
                               int(self.par['shim_XY']),
                               int(self.par['shim_X2Y2'])])

        O1_shim_range = int(self.par['O1_shim_range'])
        O2_shim_range = int(self.par['O2_shim_range'])
        iterations = int(self.par['shim_iterations'])
        convratio = int(self.par['conv_ratio'])
        if progress_handler is not None:
            progress_handler(0, iterations*8*3)
        for i in range(iterations):
            for j in range(8): # X, Y, Z, Z2, ZX, ZY, XY, X2Y2
                shim_range = O1_shim_range if j < 3 else O2_shim_range
                if shim_range == 0:
                    continue
                results = {}
                for k in [-1, 0, 1]:
                    self.try_shims = self.shims.copy()
                    self.try_shims[j] += k*shim_range
                    message_handler('trying (X: %d, Y: %d, Z: %d, Z2: %d, ZX: %d, ZY: %d, XY: %d, X2Y2: %d)' %
                                    tuple(self.try_shims.tolist()))
                    self.programs['FID'].set_par('shim_X', self.try_shims[0])
                    self.programs['FID'].set_par('shim_Y', self.try_shims[1])
                    self.programs['FID'].set_par('shim_Z', self.try_shims[2])
                    self.programs['FID'].set_par('shim_Z2', self.try_shims[3])
                    self.programs['FID'].set_par('shim_ZX', self.try_shims[4])
                    self.programs['FID'].set_par('shim_ZY', self.try_shims[5])
                    self.programs['FID'].set_par('shim_XY', self.try_shims[6])
                    self.programs['FID'].set_par('shim_X2Y2', self.try_shims[7])
                    await self.programs['FID'].run(progress_handler=None,
                                                   message_handler=message_handler)
                    y = self.gaussian_apodize(self.raw_data(), self.par['gaussian_lb'])
                    results[k] = np.sum(np.abs(y)**2)
                    if progress_handler is not None:
                        progress_handler(8*3*i+3*j+k+1, iterations * 8 * 3)
                    message_handler('SumSq: %d' % results[k])
                if i == iterations-1: # on final iteration just pick the best point
                    if results[-1] > results[1] and results[-1] > results[0]:
                        self.shims[j] -= shim_range
                    elif results[1] > results[-1] and results[1] > results[0]:
                        self.shims[j] += shim_range
                else: # on other iterations pick the midpoint of the better side
                    if results[-1] > results[1]:
                        self.shims[j] -= int(shim_range / convratio)
                    elif results[-1] < results[1]:
                        self.shims[j] += int(shim_range / convratio)
            O1_shim_range = int(O1_shim_range * (convratio - 1)/convratio)
            O2_shim_range = int(O1_shim_range * (convratio - 1) / convratio)
            message_handler('Shims X: %d, Y: %d, Z: %d, Z2: %d, ZX: %d, ZY: %d, XY: %d, X2Y2: %d' %
                            tuple(self.try_shims.tolist()))



    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        y = self.autophase(self.raw_data())
        y = self.gaussian_apodize(y, self.par['gaussian_lb'])
        x = np.linspace(0, self.par['dwell_time']*len(y), len(y), endpoint=False)
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
        fft = np.fft.fft(y)
        freq = np.fft.fftfreq(y.size, d=dwell_time)
        # sort the frequency axis
        p = freq.argsort()
        freq = freq[p]
        fft = fft[p]
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
        height = data['fft_mag'].max()
        left_hw_index = -1
        right_hw_index = -1
        for i,x in enumerate(data['fft_mag']):
            if x > height/2:
                if left_hw_index==-1:
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
                'title': 'FFT (peak@{:0.4f}{}, height: {:0.4f} uV, 50% width: {:0.4f} kHz)'.format(peak_freq, 'M'+data['freq_unit'], height*1000000, half_width/1000),
                'xaxis': {'title': data['freq_unit']},
                'yaxis': {'title': data['fft_unit']}
            }}

    def raw_data(self):
        data = self.programs['FID'].data
        data = data.view(np.complex64)
        return data

    def autophase(self, data):
        phase = get_autophase(data)
        return data * np.exp(1j * phase)  # rotate

    def gaussian_apodize(self, data, lb):
        t = np.linspace(0, 1, len(data))
        return data * np.exp(-lb*lb*t*t)