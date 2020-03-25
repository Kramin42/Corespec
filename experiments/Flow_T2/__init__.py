from experiment import BaseExperiment # required
from libraries.invlaplace import getT2Spectrum
from hardware.system import set_flow_enabled
from libraries.expfitting import multi_exp

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np
import asyncio
import os
import yaml

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        message_handler('Switching flow ON')
        set_flow_enabled(True)
        await asyncio.sleep(self.par['flow_delay'])  # wait for flow to stabilise, in seconds
        message_handler('Starting measurement')

        await self.programs['CPMG'].run(progress_handler=progress_handler,
                                        message_handler=message_handler)
        y = self.autophase(self.integrated_data())
        y /= 1000000  # μV -> V
        # if y.size >= 10:
        #     SNR = np.mean(y.real[:2]).item() / np.sqrt(np.mean(y.imag[int(y.size/2):] * y.imag[int(y.size/2):])).item()
        #     message_handler('SNR estimate: %d' % SNR)

        # calculate flow rate
        echo_count = int(self.par['echo_count'])
        echo_time = self.par['echo_time'] / 1000000.0
        t = np.linspace(0, echo_count * echo_time, echo_count, endpoint=False)

        if self.par['remove_baseline'] == 1:
            y = self.remove_baseline(t, y)

        calibration = float(self.par['flow_calibration'])
        flow_crop = int(self.par['flow_crop'])
        # only fit points between thresh_l and thresh_h (proportions relative to sigmax)
        flow_thresh_l = float(self.par['flow_thresh_l'])
        flow_thresh_h = float(self.par['flow_thresh_h'])
        skip_N = flow_crop
        fit_N = 3
        sigmax = np.max(y.real)
        while skip_N + fit_N < echo_count:
            if y.real[skip_N] < sigmax * flow_thresh_h:
                break
            skip_N += 1
        while skip_N + fit_N < echo_count:
            if y.real[skip_N + fit_N] < sigmax * flow_thresh_l:
                break
            fit_N += 1
        P = np.polyfit(t[skip_N:fit_N + skip_N], y.real[skip_N:fit_N + skip_N], 1)
        logger.debug(P)
        flow_rate = -P[0] / P[1] * calibration
        tube_ID = float(self.par['tube_ID'])
        radius = tube_ID/2000 #  mm -> m
        seconds_per_day = 3600*24
        vol_flow = flow_rate*(np.pi*radius*radius)*seconds_per_day
        message_handler('Flow Speed (m/s): %.3f, Vol. Flow (m^3/day): %.3f' % (flow_rate, vol_flow))

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
        plot_data = {'data': [{
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
        if self.par['remove_baseline'] == 1:
            baseline_corr_y_real = self.remove_baseline(data['x'], data['y_real'])
            plot_data['data'].append({
                'name': 'Baseline Corrected',
                'type': 'scatter',
                'x': data['x'],
                'y': baseline_corr_y_real})
        return plot_data

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
        return {'data': [{
            'name': '',
            'type': 'scatter',
            'x': np.log10(data['x']),
            'y': data['y']}],
        'layout': {
            'title': 'T2 Spectrum',
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

    def remove_baseline(self, x, y):
        with open(os.path.join(self._dir, '../Static_T2/multi_exp_fit_par.yaml'), 'r') as f:
            fit_par = yaml.load(f)
        baseline = multi_exp(x, *fit_par)
        baseline = np.clip(baseline / baseline.max(), self.par['baseline_clip'], None)  # normalise and clip
        return y/baseline
