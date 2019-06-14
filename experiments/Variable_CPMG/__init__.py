from experiment import BaseExperiment # required
from libraries.invlaplace import getT2Spectrum
from libraries.autophase import get_autophase

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy as np

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['LinVarCPMG'] to access the LinVarCPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        self.par['echo_time_inc'] = np.round(self.par['echo_time_inc']/2, 2)*2
        logger.debug('rounded echo_time_inc to %.4f us' % self.par['echo_time_inc'])
        await self.programs['LinVarCPMG'].run(progress_handler=progress_handler,
                                        message_handler=message_handler)
        y = self.autophase(self.integrated_data())
        if y.size >= 10:
            SNR = np.mean(y.real[:2]).item() / np.sqrt(np.mean(y.imag[int(y.size/2):] * y.imag[int(y.size/2):])).item()
            message_handler('SNR estimate: %d' % SNR)

    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        echo_time = self.par['echo_time']
        echo_time_inc = self.par['echo_time_inc']
        dwell_time = self.par['dwell_time']
        data = self.autophase(self.raw_data())
        t = np.zeros(data.size)
        offset = 0
        sample_times = np.linspace(0, samples*dwell_time,
                                 num=samples, endpoint=False)
        for i in range(echo_count):
            t[i*samples:(i+1)*samples] = sample_times + offset
            echo_time += echo_time_inc
            offset+=echo_time
        t/= 1000000  # μs -> s
        data/=1000000  # μV -> V
        return {
            'time': t,
            'real': data.real,
            'imag': data.imag,
            'unit': 'V',
            'time_unit': 's'}
    
    def export_Echo_Integrals(self):
        y = self.autophase(self.integrated_data())
        y /= 1000000  # μV -> V
        echo_count = int(self.par['echo_count'])
        echo_time = self.par['echo_time']
        echo_time_inc = self.par['echo_time_inc']
        echo_times = np.linspace(echo_time, echo_time+echo_time_inc*(echo_count-1), echo_count, endpoint=True)
        x = np.cumsum(echo_times)
        x -= x[0]  # start at 0
        x /= 1000000  # us -> s
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'y_mag': np.absolute(y),
            'x_unit': 's',
            'y_unit': 'V'}

    def export_Echo_Envelope(self):
        data = self.autophase(self.raw_data())
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        dwell_time = self.par['dwell_time']
        dwell_time/=1000000 # μs -> s
        x = np.linspace(0, dwell_time*samples, samples, endpoint=False)
        # y = np.zeros(samples, dtype=np.complex64)
        y = data.reshape((echo_count, samples)).mean(axis=0)
        # for i in range(len(data)):
        #     y[i%samples] += data[i]
        # y /= echo_count
        y /= 1000000  # μV -> V
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'x_unit': 's',
            'y_unit': 'V'}

    # def export_T2_Spectrum(self):
    #     echo_count = int(self.par['echo_count'])
    #     echo_time = self.par['echo_time'] / 1000000.0  # μs -> s
    #     Y = self.autophase(self.integrated_data())
    #     t = np.linspace(0, echo_count*echo_time, echo_count, endpoint=False)
    #     T2 = np.logspace(-5, 2, 200+1, endpoint=True)  # TODO: add parameters for T2 range/points
    #     S = getT2Spectrum(t, Y.real, Y.imag, T2, fixed_alpha=1)  # TODO: determine alpha automatically
    #     return {
    #         'x': T2,
    #         'y': S,
    #         'x_unit': 's',
    #         'y_unit': 'arb. units.',
    #         'initial_amp_uV': np.mean(Y[0:4].real)
    #     }

    # def export_default(self):
    #     export = self.export_Raw()
    #     export_spectrum = self.export_T2_Spectrum()
    #     export['spectrum_T2'] = export_spectrum['x']
    #     export['spectrum'] = export_spectrum['y']
    #     export['spectrum_T2_unit'] = export_spectrum['x_unit']
    #     export['spectrum_unit'] = export_spectrum['y_unit']
    #     return export

    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_Raw(self):
        data = self.export_Raw()
        # return object according to plotly schema
        return {'data': [{
                    'name': 'Real',
                    'type': 'scatter',
                    'x': data['time'],
                    'y': data['real']}, {
                    'name': 'Imag',
                    'type': 'scatter',
                    'x': data['time'],
                    'y': data['imag']}],
                'layout': {
                    'title': 'Raw data',
                    'yaxis': {'title': data['unit']},
                    'xaxis': {'title': data['time_unit']}
                }}
    
    def plot_Echo_Integrals(self):
        data = self.export_Echo_Integrals()
        return {'data': [{
                    'name': 'Real',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y_real']}, {
                    'name': 'Imaginary',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y_imag']}],
                #    'name': 'Mag',
                #    'type': 'scatter',
                #    'x': data['x'],
                #    'y': data['y_mag']}],
                'layout': {
                    'title': 'Echo Integrals',
                    'xaxis': {'title': data['x_unit']},
                    'yaxis': {'title': data['y_unit']}
                }}

    def plot_Echo_Envelope(self):
        data = self.export_Echo_Envelope()
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
                    'title': 'Average Echo Envelope',
                    'xaxis': {'title': data['x_unit']},
                    'yaxis': {'title': data['y_unit']}
                }}

    # def plot_T2_Spectrum(self):
    #     data = self.export_T2_Spectrum()
    #     return {'data': [{
    #         'name': '',
    #         'type': 'scatter',
    #         'x': np.log10(data['x']),
    #         'y': data['y']}],
    #     'layout': {
    #         'title': 'T2 Spectrum',
    #         'xaxis': {'title': 'log10(T2) (%s)' % data['x_unit']},
    #         'yaxis': {'title': 'Incremental Volume (%s)' % data['y_unit']}
    #     }}
    
    def raw_data(self):
        data = self.programs['LinVarCPMG'].data
        # deinterleave
        data = data.view(np.complex64)
        return data

    def integrated_data(self, decimation=1):
        data = self.raw_data()
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count']/decimation)
        y = np.zeros(echo_count, dtype=np.complex64)
        for i in range(echo_count):
            y[i] = np.mean(data[i * decimation * samples:(i*decimation + 1) * samples])
        return y

    def autophase(self, data):
        phase = -np.angle(np.sum(data))  # use simple method for CPMG
        return data * np.exp(1j * phase)  # rotate
