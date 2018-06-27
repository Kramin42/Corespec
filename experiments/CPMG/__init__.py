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
    async def run(self, progress_handler=None, warning_handler=None):
        await self.programs['CPMG'].run(progress_handler=progress_handler,
                                        warning_handler=warning_handler)

    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_real_imag(self):
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        data = self.autophase(self.raw_data())
        t = np.zeros(data.size)
        offset = 0
        sample_times = np.linspace(0, samples*self.par['dwell_time'],
                                 num=samples, endpoint=False)
        for i in range(echo_count):
            t[i*samples:(i+1)*samples] = sample_times + offset
            offset+=self.par['echo_time']
        return {'real': data.real, 'imag': data.imag, 'unit': 'μV', 'time': t, 'time_unit': 'μs'}
    
    def export_echo_integrals(self):
        y = self.autophase(self.integrated_data())
        echo_count = int(self.par['echo_count'])
        echo_time = self.par['echo_time']/1000000.0
        x = np.linspace(0, echo_count*echo_time, echo_count)
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'y_mag': np.absolute(y),
            'x_unit': 's',
            'y_unit': 'μV'}

    def export_echo_envelope(self):
        data = self.raw_data()
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        dwell_time = self.par['dwell_time']
        x = np.linspace(0, dwell_time*samples, samples, endpoint=False)
        y = np.zeros(samples, dtype=np.complex64)
        for i in range(len(data)):
            y[i%samples] += data[i]
        y /= echo_count
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'x_unit': 'μs',
            'y_unit': 'μV'}

    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_real_imag(self):
        data = self.export_real_imag()
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
    
    def plot_echo_integrals(self):
        data = self.export_echo_integrals()
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

    def plot_echo_envelope(self):
        data = self.export_echo_envelope()
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
    
    def raw_data(self):
        data = self.programs['CPMG'].data
        # deinterleave
        data = data.astype(np.float32).view(np.complex64)
        return data

    def integrated_data(self):
        data = self.raw_data()
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        y = np.zeros(echo_count, dtype=np.complex64)
        for i in range(echo_count):
            y[i] = np.mean(data[i * samples:(i + 1) * samples])
        return y

    def autophase(self, data):
        phase = np.angle(np.sum(data)) # get average phase
        return data * np.exp(1j * -phase) # rotate
