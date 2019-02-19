from experiment import BaseExperiment # required
from libraries.invlaplace import getT2Spectrum
from hardware.system import set_flow_enabled

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy as np
import asyncio

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
        message_handler('Switching flow OFF')
        set_flow_enabled(False)
        await asyncio.sleep(self.par['flow_delay'])  # wait for flow to stabilise, in seconds
        message_handler('Starting static measurement')

        # run FID first to set the frequency automatically
        self.par['rep_time'] = self.par['FID_rep_time']
        self.par['scans'] = self.par['FID_scans']
        self.par['samples'] = self.par['FID_samples']
        self.par['dwell_time'] = self.par['FID_dwell_time']
        self.programs['FID'].set_par('rep_time', float(self.par['FID_rep_time']))
        self.programs['FID'].set_par('scans', float(self.par['FID_scans']))
        self.programs['FID'].set_par('samples', float(self.par['FID_samples']))
        self.programs['FID'].set_par('dwell_time', float(self.par['FID_dwell_time']))
        await self.programs['FID'].run(progress_handler=progress_handler,
                                        message_handler=message_handler)

        # determine location of peak
        y = self.programs['FID'].data.view(np.complex64)
        dwell_time = self.par['dwell_time']  # μs
        fft = np.fft.fft(y)
        freq = np.fft.fftfreq(y.size, d=dwell_time)
        # sort the frequency axis
        p = freq.argsort()
        freq = freq[p]
        fft = fft[p]
        fft_mag = np.abs(fft)
        peak_index = np.argmax(fft_mag)
        peak_freq_offset = freq[peak_index]  # in MHz
        avg_start = peak_index - int(len(freq) / 20)
        avg_end = peak_index + int(len(freq) / 20) + 1
        if avg_start > 0 and avg_end <= len(freq):
            peak_freq_offset = np.average(freq[avg_start:avg_end],
                                          weights=np.square(fft_mag[avg_start:avg_end]))  # in MHz
        self.par['freq'] += peak_freq_offset
        self.programs['CPMG'].set_par('freq', float(self.par['freq']))
        logger.debug('Setting frequency to %s' % self.par['freq'])

        # Run static T2 measurement
        self.par['echo_time'] = self.par['static_echo_time']
        self.par['rep_time'] = self.par['static_rep_time']
        self.par['echo_count'] = self.par['static_echo_count']
        self.par['scans'] = self.par['static_scans']
        self.par['echo_shift'] = self.par['static_echo_shift']
        self.par['samples'] = self.par['static_samples']
        self.par['dwell_time'] = self.par['static_dwell_time']
        self.programs['CPMG'].set_par('echo_time', float(self.par['echo_time']))
        self.programs['CPMG'].set_par('rep_time', float(self.par['rep_time']))
        self.programs['CPMG'].set_par('echo_count', float(self.par['echo_count']))
        self.programs['CPMG'].set_par('scans', float(self.par['scans']))
        self.programs['CPMG'].set_par('echo_shift', float(self.par['echo_shift']))
        self.programs['CPMG'].set_par('samples', float(self.par['samples']))
        self.programs['CPMG'].set_par('dwell_time', float(self.par['dwell_time']))
        await self.programs['CPMG'].run(progress_handler=progress_handler,
                                        message_handler=message_handler)
        self.static_intdata = self.autophase(self.integrated_data())
        data = self.export_T2_Spectrum()
        S = data['y']
        T2 = data['x']
        oil_rel_proton_density = float(self.par['oil_HI'])
        oil_water_T2_boundary = float(self.par['oil_T2_max'])
        full_water_initial_amp = float(self.par['FWIA'])
        divider_index = 0
        while T2[divider_index] < oil_water_T2_boundary:
            divider_index+=1
        amount_oil = np.sum(S[:divider_index]) / oil_rel_proton_density
        amount_water = np.sum(S[divider_index:])
        percent_gas = 100*(full_water_initial_amp - data['initial_amp_uV'])/full_water_initial_amp
        percent_oil = (100 - percent_gas) * (amount_oil) / (amount_water + amount_oil)
        percent_water = (100 - percent_gas) * (amount_water) / (amount_water + amount_oil)
        message_handler('Oil: %.1f%%, Water: %.1f%%, Gas: %.1f%%' % (percent_oil, percent_water, percent_gas))

        message_handler('Switching flow ON')
        set_flow_enabled(True)
        await asyncio.sleep(self.par['flow_delay'])  # wait for flow to stabilise, in seconds
        message_handler('Starting flow measurement')

        # run flow T2 measurement
        self.par['echo_time'] = self.par['flow_echo_time']
        self.par['rep_time'] = self.par['flow_rep_time']
        self.par['echo_count'] = self.par['flow_echo_count']
        self.par['scans'] = self.par['flow_scans']
        self.par['echo_shift'] = self.par['flow_echo_shift']
        self.par['samples'] = self.par['flow_samples']
        self.par['dwell_time'] = self.par['flow_dwell_time']
        self.programs['CPMG'].set_par('echo_time', float(self.par['echo_time']))
        self.programs['CPMG'].set_par('rep_time', float(self.par['rep_time']))
        self.programs['CPMG'].set_par('echo_count', float(self.par['echo_count']))
        self.programs['CPMG'].set_par('scans', float(self.par['scans']))
        self.programs['CPMG'].set_par('echo_shift', float(self.par['echo_shift']))
        self.programs['CPMG'].set_par('samples', float(self.par['samples']))
        self.programs['CPMG'].set_par('dwell_time', float(self.par['dwell_time']))
        await self.programs['CPMG'].run(progress_handler=progress_handler,
                                        message_handler=message_handler)

        self.flow_intdata = self.autophase(self.integrated_data())
        self.flow_intdata /= 1000000  # μV -> V

        # calculate flow rate
        echo_count = int(self.par['echo_count'])
        echo_time = self.par['echo_time'] / 1000000.0
        t = np.linspace(0, echo_count * echo_time, echo_count, endpoint=False)
        calibration = float(self.par['flow_calibration'])
        fit_thresh = 0.25  # only fit points > this proportion of the max signal
        skip_N = 2
        fit_N = 3
        sigmax = np.max(self.flow_intdata.real)
        while skip_N + fit_N < echo_count:
            if self.flow_intdata.real[skip_N + fit_N] < sigmax * fit_thresh:
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
        message_handler('Oil Flow Rate (m^3/day): %.3f' % (vol_flow*0.01*percent_oil))
        message_handler('Water Flow Rate (m^3/day): %.3f' % (vol_flow * 0.01 * percent_water))
        message_handler('Gas Flow Rate (m^3/day): %.3f' % (vol_flow * 0.01 * percent_gas))


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
        echo_count = int(self.par['static_echo_count'])
        echo_time = self.par['static_echo_time'] / 1000000.0  # μs -> s
        if not hasattr(self, 'static_intdata') or self.static_intdata is None:
            raise Exception('Static T2 data not ready!')
        Y = self.static_intdata
        t = np.linspace(0, echo_count*echo_time, echo_count, endpoint=False)
        T2 = np.logspace(-5, 2, 200, endpoint=False)
        S = getT2Spectrum(t, Y.real, Y.imag, T2, fixed_alpha=10)
        return {
            'x': T2,
            'y': S,
            'x_unit': 's',
            'y_unit': 'arb. units.',
            'initial_amp_uV': np.mean(Y[0:4].real)
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
                    'title': 'Echo Integrals (IA: %.2f uV)' % (1000000*np.mean(data['y_real'][0:4])),
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
        oil_rel_proton_density = float(self.par['oil_HI'])
        oil_water_T2_boundary = float(self.par['oil_T2_max'])
        full_water_initial_amp = float(self.par['FWIA'])
        divider_index = 0
        while T2[divider_index] < oil_water_T2_boundary:
            divider_index+=1
        amount_oil = np.sum(S[:divider_index]) / oil_rel_proton_density
        amount_water = np.sum(S[divider_index:])
        percent_gas = 100*(full_water_initial_amp - data['initial_amp_uV'])/full_water_initial_amp
        percent_oil = (100 - percent_gas) * (amount_oil) / (amount_water + amount_oil)
        percent_water = (100 - percent_gas) * (amount_water) / (amount_water + amount_oil)
        return {'data': [{
            'name': '',
            'type': 'scatter',
            'x': np.log10(data['x']),
            'y': data['y']}],
        'layout': {
            'title': 'T2 Spectrum (Oil: %.1f%%, Water: %.1f%%, Gas: %.1f%%)' % (percent_oil, percent_water, percent_gas),
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
