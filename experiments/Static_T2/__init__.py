from experiment import BaseExperiment # required
from libraries.invlaplace import getT2Spectrum
from hardware.system import set_flow_enabled

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np
import asyncio

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        message_handler('Switching flow OFF')
        set_flow_enabled(False)
        await asyncio.sleep(self.par['flow_delay'])  # wait for flow to stabilise, in seconds
        message_handler('Starting measurement')

        await self.programs['CPMG'].run(progress_handler=progress_handler,
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
        dwell_time = self.par['dwell_time']
        data = self.autophase(self.raw_data())
        t = np.zeros(data.size)
        offset = 0
        sample_times = np.linspace(0, samples*dwell_time,
                                 num=samples, endpoint=False)
        for i in range(echo_count):
            t[i*samples:(i+1)*samples] = sample_times + offset
            offset+=self.par['echo_time']
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
        y/=1000000 # μV -> V
        echo_count = int(self.par['echo_count'])
        echo_time = self.par['echo_time']/1000000.0
        x = np.linspace(0, echo_count*echo_time, echo_count, endpoint=False)
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
        dwell_time/=1000000  # μs -> s
        x = np.linspace(0, dwell_time*samples, samples, endpoint=False)
        y = np.zeros(samples, dtype=np.complex64)
        for i in range(len(data)):
            y[i%samples] += data[i]
        y /= echo_count
        y /= 1000000  # μV -> V
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'x_unit': 's',
            'y_unit': 'V'}

    def export_T2_Spectrum(self):
        echo_count = int(self.par['echo_count'])
        echo_time = self.par['echo_time'] / 1000000.0  # μs -> s
        Y = self.autophase(self.integrated_data())
        t = np.linspace(0, echo_count*echo_time, echo_count, endpoint=False)
        T2 = np.logspace(-5, 2, 200, endpoint=False)
        S = getT2Spectrum(t, Y.real, Y.imag, T2, fixed_alpha=10)
        return {
            'x': T2,
            'y': S,
            'x_unit': 's',
            'y_unit': 'arb. units.'
        }


    def export_default(self):
        return self.export_Raw()

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

    def plot_T2_Spectrum(self):
        data = self.export_T2_Spectrum()
        S = data['y']
        T2 = data['x']
        # TODO: change these to input parameters or determine automatically
        oil_rel_proton_density = 1.2
        oil_water_T2_boundary = 0.5
        divider_index = 0
        while data['T2'][divider_index] < oil_water_T2_boundary:
            divider_index+=1
        amount_oil = np.sum(S[:divider_index]) / oil_rel_proton_density
        amount_water = np.sum(S[divider_index:])
        percent_oil = 100 * (amount_oil) / (amount_water + amount_oil)
        percent_water = 100 * (amount_water) / (amount_water + amount_oil)
        return {'data': [{
            'name': '',
            'type': 'scatter',
            'x': np.log10(data['x']),
            'y': data['y']}],
        'layout': {
            'title': 'T2 Spectrum (Oil: %.1f%%, Water: %.1f%%)' % (percent_oil, percent_water),
            'xaxis': {'title': 'log10(T2) (%s)' % data['x_unit']},
            'yaxis': {'title': 'Incremental Volume (%s)' % data['y_unit']}
        }}
    
    def raw_data(self):
        data = self.programs['CPMG'].data
        # deinterleave
        data = data.view(np.complex64)
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
