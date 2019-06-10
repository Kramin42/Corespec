from experiment import BaseExperiment # required
from libraries.autophase import get_autophase

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np
from scipy.optimize import curve_fit

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    def override(self):
        del self.par_def['echo_time']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        #self.echo_times = np.logspace(np.log10(self.par['start_echo_time']), np.log10(self.par['end_echo_time']), self.par['steps'], endpoint=True)
        self.echo_times = np.linspace(self.par['start_echo_time'], self.par['end_echo_time'], self.par['steps'], endpoint=True)
        count = len(self.echo_times)
        index = 0
        self.data = None
        phase = 0

        #def my_progress_handler(progress, limit=0):
        #    logger.debug('calling progress handler with %s/%s' % (progress+index*count, limit*count))
        #    progress_handler(progress+index*count, limit*count)

        for echo_time in self.echo_times:
            progress_handler(index, count)
            logger.debug('running echo time %s' % echo_time)
            self.programs['SpinEcho'].set_par('echo_time', echo_time)
            await self.programs['SpinEcho'].run(message_handler=message_handler)
            run_data = self.programs['SpinEcho'].data.view(np.complex64)
            if index==0:
                phase = get_autophase(run_data, t0=-0.5*self.par['dwell_time']*len(run_data)+self.par['sample_shift'], dwelltime=self.par['dwell_time'])
            run_data *= np.exp(1j * phase)
            if self.data is None:
                self.data = np.array([run_data])
            else:
                self.data = np.append(self.data, [run_data], axis=0)
            index+=1
        progress_handler(index, count)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_T2(self):
        dwell_time = self.par['dwell_time']/1000000
        sample_shift = self.par['sample_shift']/1000000
        samples = int(*self.par['samples'])
        fft = np.fft.fft(self.raw_data(), axis=1)
        freq = np.fft.fftfreq(samples, d=dwell_time)[:, np.newaxis]
        fft *= np.exp(1j*2*np.pi*-(-0.5*dwell_time*len(fft)+sample_shift)*freq)
        fft *= dwell_time
        halfwidth = int(fft.shape[1]*self.par['int_width']*dwell_time*500)+1
        y = np.sum(fft[:,:halfwidth], axis=1) + np.sum(fft[:,:-halfwidth:-1], axis=1)
        y /= (2*halfwidth+1)
        y *= self.par['int_width']/1000
        x = self.echo_times/1000000
        x = x[:len(y)]
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'x_unit': 's',
            'y_unit': 'V'}

    def export_Raw(self):
        data = self.raw_data()
        T2_axis = self.echo_times / 1000000  # us -> s
        samples = int(*self.par['samples'])
        dwell_time = self.par['dwell_time'] / 1000000
        sample_shift = self.par['sample_shift'] / 1000000
        time_axis = np.linspace(-0.5*dwell_time*samples+sample_shift, 0.5*dwell_time*samples+sample_shift, samples, endpoint=False)
        return {
            'echo_time': T2_axis[:, np.newaxis],
            'sample_time': time_axis,
            'real': data.real,
            'imag': data.imag
        }

    # def export_default(self):
    #     return self.export_Raw()
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_T2(self):
        data = self.export_T2()
        result = {'data': [{
                    'name': 'Real',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y_real']
                },{
                    'name': 'Imag',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y_imag']
                }],
                'layout': {
                    'title': 'T2',
                    'xaxis': {'title': 'Echo Time (%s)' % data['x_unit']},
                    'yaxis': {'title': 'FT Integral (%s)' % data['y_unit']}
                }}
        return result

    def plot_Echo(self):
        y = self.raw_data()[-1,:]
        x = np.linspace(-0.5*self.par['dwell_time']*len(y)+self.par['sample_shift'], 0.5*self.par['dwell_time']*len(y)+self.par['sample_shift'], len(y), endpoint=False)
        y /= 1000000  # μV->V
        x /= 1000000  # μs->s
        return {'data': [{
            'name': 'Real',
            'type': 'scatter',
            'x': x,
            'y': y.real}, {
            'name': 'Imag',
            'type': 'scatter',
            'x': x,
            'y': y.imag}],
            'layout': {
                'title': 'Real/Imag data',
                'xaxis': {'title': 's'},
                'yaxis': {'title': 'V'}
            }}

    def raw_data(self):
        return self.data

