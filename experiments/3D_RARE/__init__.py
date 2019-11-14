from experiment import BaseExperiment  # required
from libraries.invlaplace import getT2Spectrum
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
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        phase_G = np.array([int(self.par['phase_GX_start']), int(self.par['phase_GY_start']), int(self.par['phase_GZ_start'])])
        phase2_G = np.array([int(self.par['phase2_GX']), int(self.par['phase2_GY']), int(self.par['phase2_GZ'])])
        phase2_steps = int(self.par['phase2_steps'])
        G2s = np.outer(np.linspace(1, -1, phase2_steps, endpoint=False), phase2_G).astype(int)
        self.data = None
        for i,G2 in enumerate(G2s):
            if progress_handler is not None:
                progress_handler(i, phase2_steps)
            self.programs['2DMRICPMG'].set_par('phase_GX_start', phase_G[0]+G2[0])
            self.programs['2DMRICPMG'].set_par('phase_GY_start', phase_G[1]+G2[1])
            self.programs['2DMRICPMG'].set_par('phase_GZ_start', phase_G[2]+G2[2])
            await self.programs['2DMRICPMG'].run(progress_handler=None, message_handler=message_handler)
            run_data = self.programs['2DMRICPMG'].data
            # self.data = np.append(self.data, np.max(np.abs(np.fft.fft(run_data))))
            if self.data is None:
                self.data = np.array([run_data])
            else:
                self.data = np.append(self.data, [run_data], axis=0)

    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Raw(self):
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        dwell_time = self.par['dwell_time']
        data = self.raw_data()
        t = np.zeros(samples*echo_count)
        offset = 0
        sample_times = np.linspace(0, samples * dwell_time,
                                   num=samples, endpoint=False)
        for i in range(echo_count):
            t[i * samples:(i + 1) * samples] = sample_times + offset
            offset += self.par['echo_time']
        t /= 1000000  # μs -> s
        data /= 1000000  # μV -> V
        return {
            'time': t,
            'real': data.real,
            'imag': data.imag,
            'unit': 'V',
            'time_unit': 's'}

    def export_Echo_Integrals(self, decimation=1):
        y = self.autophase(self.integrated_data(decimation=decimation))
        y /= 1000000  # μV -> V
        echo_count = int(self.par['echo_count'] / decimation)
        echo_time = decimation * self.par['echo_time'] / 1000000.0
        x = np.linspace(0, echo_count * echo_time, echo_count, endpoint=False)
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'y_mag': np.absolute(y),
            'x_unit': 's',
            'y_unit': 'V'}

    def export_Echo_Envelope(self):
        data = self.autophase(self.raw_data()[-1,:])
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        dwell_time = self.par['dwell_time']
        dwell_time /= 1000000  # μs -> s
        x = np.linspace(0, dwell_time * samples, samples, endpoint=False)
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
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'])
        dwell_time = float(self.par['dwell_time'])
        data = self.autophase(self.integrated_data())
        t = np.zeros(samples*echo_count)
        offset = 0
        sample_times = np.linspace(0, samples * dwell_time,
                                   num=samples, endpoint=False)
        for i in range(echo_count):
            t[i * samples:(i + 1) * samples] = sample_times + offset
            offset += self.par['echo_time']
        t /= 1000000  # μs -> s
        data /= 1000000  # μV -> V
        # return object according to plotly schema
        return {'data': [{
            'name': 'Real',
            'type': 'scatter',
            'x': t,
            'y': data.real}, {
            'name': 'Imag',
            'type': 'scatter',
            'x': t,
            'y': data.imag}],
            'layout': {
                'title': 'Raw data',
                'yaxis': {'title': data['unit']},
                'xaxis': {'title': data['time_unit']}
            }}

    def plot_Echo_Integrals(self):
        # with very large data, decimate before sending plots
        if self.par['echo_count'] > 10000:
            data = self.export_Echo_Integrals(decimation=int(self.par['echo_count'] / 10000))
        else:
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

    def raw_data(self):
        return self.data.copy()

    def integrated_data(self, decimation=1):
        data = self.raw_data()[-1,:]
        samples = int(self.par['samples'])
        echo_count = int(self.par['echo_count'] / decimation)
        y = np.zeros(echo_count, dtype=np.complex64)
        for i in range(echo_count):
            y[i] = np.mean(data[i * decimation * samples:(i * decimation + 1) * samples])
        return y

    def autophase(self, data):
        phase = -np.angle(np.sum(data))  # use simple method for CPMG
        return data * np.exp(1j * phase)  # rotate
