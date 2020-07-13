from experiment import BaseExperiment # required
from libraries.invlaplace import getT2Spectrum, compress
from hardware.system import set_flow_enabled
from libraries.expfitting import fit_multi_exp, multi_exp

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy as np
from time import time
import asyncio

FLOW_DATA_SIZE_LIMIT = 100000

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    def override(self):
        del self.par_def['echo_time']
        del self.par_def['rep_time']
        del self.par_def['echo_count']
        del self.par_def['scans']
        del self.par_def['echo_shift']
        del self.par_def['samples']
        del self.par_def['dwell_time']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        t_init = time()
        t_last = t_init
        self.freq_t = []
        self.freq_values = []
        self.prop_t = []
        self.prop_water = []
        self.prop_oil = []
        self.prop_gas = []
        self.flow_t = []
        self.flow_water = []
        self.flow_oil = []
        self.flow_gas = []
        self.aborted = False
        flow_num = int(self.par['flow_num'])
        baseline_N_exp = int(self.par['N_exp'])
        baseline_N_ignore = int(self.par['N_ignore'])
        baseline_N_compress = int(self.par['N_compress'])
        self.baseline_fit_par = None
        while not self.aborted:
            progress_handler(0, flow_num + 1)
            if len(self.flow_t) > FLOW_DATA_SIZE_LIMIT:
                self.flow_t = self.flow_t[flow_num:]
                self.flow_water = self.flow_water[flow_num:]
                self.flow_oil = self.flow_oil[flow_num:]
                self.flow_gas = self.flow_gas[flow_num:]

                self.prop_t = self.prop_t[1:]
                self.prop_water = self.prop_water[1:]
                self.prop_oil = self.prop_oil[1:]
                self.prop_gas = self.prop_gas[1:]

            message_handler('Switching flow OFF')
            set_flow_enabled(False)
            await asyncio.sleep(self.par['flow_delay'])  # wait for flow to stabilise, in seconds
            message_handler('Starting static measurement')

            # run FID first to set the frequency automatically
            self.freq_t.append(time() - t_init)
            self.programs['FID'].set_par('rep_time', float(self.par['FID_rep_time']))
            self.programs['FID'].set_par('scans', float(self.par['FID_scans']))
            self.programs['FID'].set_par('samples', float(self.par['FID_samples']))
            self.programs['FID'].set_par('dwell_time', float(self.par['FID_dwell_time']))
            await self.programs['FID'].run(message_handler=message_handler)

            # determine location of peak
            y = self.programs['FID'].data.view(np.complex64)
            dwell_time = self.par['FID_dwell_time']  # μs
            fft = np.fft.fftshift(np.fft.fft(y))
            freq = np.fft.fftshift(np.fft.fftfreq(y.size, d=dwell_time))
            fft_mag = np.abs(fft)
            fft_abs_sumsq = np.cumsum(fft_mag * fft_mag)
            peak_index = np.searchsorted(fft_abs_sumsq, fft_abs_sumsq[-1] / 2.0)
            peak_index_interp = (fft_abs_sumsq[-1] / 2.0 - fft_abs_sumsq[peak_index - 1]) / (
                        fft_abs_sumsq[peak_index] - fft_abs_sumsq[peak_index - 1]) - 1
            peak_freq_offset = freq[peak_index] + peak_index_interp / dwell_time

            self.par['freq'] += peak_freq_offset
            self.freq_values.append(self.par['freq'])
            self.programs['CPMG'].set_par('freq', float(self.par['freq']))
            self.programs['FID'].set_par('freq', float(self.par['freq']))
            logger.debug('Setting frequency to %s' % self.par['freq'])

            # Run static T2 measurement
            self.prop_t.append(time() - t_init)
            self.programs['CPMG'].set_par('echo_time', float(self.par['static_echo_time']))
            self.programs['CPMG'].set_par('rep_time', float(self.par['static_rep_time']))
            self.programs['CPMG'].set_par('echo_count', float(self.par['static_echo_count']))
            self.programs['CPMG'].set_par('scans', float(self.par['static_scans']))
            self.programs['CPMG'].set_par('echo_shift', float(self.par['static_echo_shift']))
            self.programs['CPMG'].set_par('samples', float(self.par['static_samples']))
            self.programs['CPMG'].set_par('dwell_time', float(self.par['static_dwell_time']))
            await self.programs['CPMG'].run(message_handler=message_handler)
            progress_handler(1, flow_num+1)

            self.static_intdata = self.autophase(self.integrated_data(
                int(self.par['static_samples']),
                int(self.par['static_echo_count'])
            ))
            echo_count = int(self.par['static_echo_count'])
            echo_time = self.par['static_echo_time'] / 1000000.0  # μs -> s
            Y = self.static_intdata
            t = np.linspace(0, echo_count * echo_time, echo_count, endpoint=False)

            if baseline_N_exp > 0:
                try:
                    com_t, com_r, com_i, com_w = compress(t[baseline_N_ignore:], Y.real[baseline_N_ignore:],
                                                          Y.imag[baseline_N_ignore:], baseline_N_compress)
                    self.baseline_fit_par, stderr = fit_multi_exp(com_t, com_r, weights=com_w, N_exp=baseline_N_exp)
                    #self.baseline_fit_par, stderr = fit_multi_exp(t, Y.real, N_exp=baseline_N_exp)
                except:
                    #self.baseline_fit_par = None
                    message_handler('Warning: Could not fit multi-exponential to static measurement', type='warning')

            T2 = np.logspace(-5, 2, 200, endpoint=False)
            S = getT2Spectrum(t, Y.real, Y.imag, T2, fixed_alpha=10)
            oil_rel_proton_density = float(self.par['oil_HI'])
            oil_water_T2_boundary = float(self.par['oil_T2_max'])
            full_water_initial_amp = float(self.par['FWIA'])
            divider_index = 0
            while T2[divider_index] < oil_water_T2_boundary:
                divider_index+=1
            amount_oil = np.sum(S[:divider_index]) / oil_rel_proton_density
            amount_water = np.sum(S[divider_index:])
            initial_amp = np.mean(Y[0:4].real)

            percent_oil = 100 * (amount_oil) / (amount_water + amount_oil)
            percent_water = 100 * (amount_water) / (amount_water + amount_oil)
            full_initial_amp = 0.01*percent_water*full_water_initial_amp + 0.01*percent_oil*oil_rel_proton_density*full_water_initial_amp
            percent_gas = 100 * (full_initial_amp - initial_amp) / full_initial_amp
            if percent_gas < 0:  # not possible, so assume that it is all water/oil
                percent_gas = 0
            elif percent_gas > 100:  # also not possible
                percent_gas = 100
            percent_water -= 0.01 * percent_gas * percent_water
            percent_oil -= 0.01 * percent_gas * percent_oil

            message_handler('Oil: %.1f%%, Water: %.1f%%, Gas: %.1f%%' % (percent_oil, percent_water, percent_gas))
            self.prop_water.append(percent_water)
            self.prop_oil.append(percent_oil)
            self.prop_gas.append(percent_gas)

            message_handler('Switching flow ON')
            set_flow_enabled(True)
            await asyncio.sleep(self.par['flow_delay'])  # wait for flow to stabilise, in seconds
            message_handler('Starting flow measurements')

            for i in range(flow_num):
                t_delta = self.par['flow_spacing'] - (time() - t_last)
                if t_delta > 0:
                    await asyncio.sleep(t_delta)
                t_last = time()

                # TODO: abort immediately during sleep
                if self.aborted:
                    break

                # run flow T2 measurement
                self.flow_t.append(time() - t_init)
                self.programs['CPMG'].set_par('echo_time', float(self.par['flow_echo_time']))
                self.programs['CPMG'].set_par('rep_time', float(self.par['flow_rep_time']))
                self.programs['CPMG'].set_par('echo_count', float(self.par['flow_echo_count']))
                self.programs['CPMG'].set_par('scans', float(self.par['flow_scans']))
                self.programs['CPMG'].set_par('echo_shift', float(self.par['flow_echo_shift']))
                self.programs['CPMG'].set_par('samples', float(self.par['flow_samples']))
                self.programs['CPMG'].set_par('dwell_time', float(self.par['flow_dwell_time']))
                await self.programs['CPMG'].run(message_handler=message_handler)

                self.flow_intdata = self.autophase(self.integrated_data(
                    int(self.par['flow_samples']),
                    int(self.par['flow_echo_count'])
                ))
                self.flow_intdata /= 1000000  # μV -> V

                # calculate flow rate
                echo_count = int(self.par['flow_echo_count'])
                echo_time = self.par['flow_echo_time'] / 1000000.0
                t = np.linspace(0, echo_count * echo_time, echo_count, endpoint=False)

                # baseline correction
                if baseline_N_exp > 0 and self.baseline_fit_par is not None:
                    baseline = multi_exp(t, *self.baseline_fit_par)
                    baseline = np.clip(baseline / baseline.max(), self.par['baseline_clip'], None)  # normalise and clip
                    self.flow_intdata /= baseline

                calibration = float(self.par['flow_calibration'])
                flow_crop = int(self.par['flow_crop'])
                # only fit points between thresh_l and thresh_h (proportions relative to sigmax)
                flow_thresh_l = float(self.par['flow_thresh_l'])
                flow_thresh_h = float(self.par['flow_thresh_h'])
                skip_N = flow_crop
                fit_N = 3
                sigmax = np.max(self.flow_intdata.real)
                while skip_N + fit_N < echo_count:
                    if self.flow_intdata.real[skip_N] < sigmax * flow_thresh_h:
                        break
                    skip_N += 1
                while skip_N + fit_N < echo_count:
                    if self.flow_intdata.real[skip_N + fit_N] < sigmax * flow_thresh_l:
                        break
                    fit_N += 1
                P = np.polyfit(t[skip_N:fit_N + skip_N], self.flow_intdata.real[skip_N:fit_N + skip_N], 1)
                logger.debug(P)
                flow_rate = -P[0] / P[1] * calibration
                tube_ID = float(self.par['tube_ID'])
                radius = tube_ID/2000 #  mm -> m
                seconds_per_day = 3600*24
                vol_flow = flow_rate*(np.pi*radius*radius)*seconds_per_day
                message_handler('Total Flow Speed (m/s): %.3f, Vol. Flow (m^3/day): %.3f' % (flow_rate, vol_flow))
                #message_handler('Oil Flow Rate (m^3/day): %.3f' % (vol_flow * 0.01 * percent_oil))
                #message_handler('Water Flow Rate (m^3/day): %.3f' % (vol_flow * 0.01 * percent_water))
                #message_handler('Gas Flow Rate (m^3/day): %.3f' % (vol_flow * 0.01 * percent_gas))
                self.flow_water.append(vol_flow * 0.01 * percent_water)
                self.flow_oil.append(vol_flow * 0.01 * percent_oil)
                self.flow_gas.append(vol_flow * 0.01 * percent_gas)
                progress_handler(i+2, flow_num+1)

    def export_Raw(self):
        try:
            return {
                'freq_t': np.array(self.freq_t, dtype=np.float32),
                'freq_values': np.array(self.freq_values, dtype=np.float32),
                'freq_unit': 'MHz',
                'prop_t': np.array(self.prop_t, dtype=np.float32),
                'prop_water': np.array(self.prop_water, dtype=np.float32),
                'prop_oil': np.array(self.prop_oil, dtype=np.float32),
                'prop_gas': np.array(self.prop_gas, dtype=np.float32),
                'prop_unit': '%',
                'flow_t': np.array(self.flow_t, dtype=np.float32),
                'flow_water': np.array(self.flow_water, dtype=np.float32),
                'flow_oil': np.array(self.flow_oil, dtype=np.float32),
                'flow_gas': np.array(self.flow_gas, dtype=np.float32),
                'time_unit': 's',
                'flow_unit': 'm^3/day'}
        except AttributeError:
            raise Exception('No Data')

    def export_Display_Measurements(self):
        try:
            return {
                'prop_water': self.prop_water[-1],
                'prop_oil': self.prop_oil[-1],
                'prop_gas': self.prop_gas[-1],
                'prop_unit': '%',
                'flow_water': self.flow_water[-1],
                'flow_oil': self.flow_oil[-1],
                'flow_gas': self.flow_gas[-1],
                'flow_unit': 'm^3/day'}
        except AttributeError:
            raise Exception('No Data')

    def plot_Content(self):
        data = self.export_Raw()
        t = data['prop_t'][-10000:]
        t_unit = 's'
        if t[-1] > 300:
            t /= 60
            t_unit = 'min'
            if t[-1] > 120:
                t /= 60
                t_unit = 'hours'
        return {'data': [{
                    'name': 'Water',
                    'type': 'scatter',
                    'x': t,
                    'y': data['prop_water'][-10000:]}, {
                    'name': 'Oil',
                    'type': 'scatter',
                    'x': t,
                    'y': data['prop_oil'][-10000:]}, {
                    'name': 'Gas',
                    'type': 'scatter',
                    'x': t,
                    'y': data['prop_gas'][-10000:]}],
                'layout': {
                    'title': 'Static Readings',
                    'yaxis': {'title': 'Relative Content (%s)' % data['prop_unit']},
                    'xaxis': {'title': 'Time (%s)' % t_unit}
                }}

    def plot_Flow(self):
        data = self.export_Raw()
        t = data['flow_t'][-10000:]
        t_unit = 's'
        if t[-1] > 300:
            t /= 60
            t_unit = 'min'
            if t[-1] > 120:
                t /= 60
                t_unit = 'hours'
        return {'data': [{
                    'name': 'Water',
                    'type': 'scatter',
                    'x': t,
                    'y': data['flow_water'][-10000:]}, {
                    'name': 'Oil',
                    'type': 'scatter',
                    'x': t,
                    'y': data['flow_oil'][-10000:]}, {
                    'name': 'Gas',
                    'type': 'scatter',
                    'x': t,
                    'y': data['flow_gas'][-10000:]}],
                'layout': {
                    'title': 'Flow Readings',
                    'yaxis': {'title': 'Flow Mass (%s)' % data['flow_unit']},
                    'xaxis': {'title': 'Time (%s)' % t_unit}
                }}

    def plot_Freq(self):
        t = np.array(self.freq_t[-10000:], dtype=np.float32)
        t_unit = 's'
        if t[-1] > 300:
            t /= 60
            t_unit = 'min'
            if t[-1] > 120:
                t /= 60
                t_unit = 'hours'
        return {'data': [{
                    'name': 'Freq.',
                    'type': 'scatter',
                    'x': t,
                    'y': np.array(self.freq_values[-10000:], dtype=np.float32)}],
                'layout': {
                    'title': 'Frequency Log',
                    'yaxis': {'title': 'NMR Frequency (MHz)'},
                    'xaxis': {'title': 'Time (%s)' % t_unit}
                }}

    def export_default(self):
        return self.export_Raw()
    
    def raw_data(self):
        data = self.programs['CPMG'].data
        # deinterleave
        data = data.view(np.complex64)
        return data

    def integrated_data(self, samples, echo_count):
        data = self.raw_data()
        y = np.zeros(echo_count, dtype=np.complex64)
        for i in range(echo_count):
            y[i] = np.mean(data[i * samples:(i + 1) * samples])
        return y

    def autophase(self, data):
        phase = np.angle(np.sum(data)) # get average phase
        return data * np.exp(1j * -phase) # rotate
