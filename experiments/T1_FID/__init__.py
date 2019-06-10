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
        del self.par_def['inversion_time']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        self.inv_times = np.logspace(np.log10(self.par['start_inv_time']), np.log10(self.par['end_inv_time']), self.par['steps'])
        count = len(self.inv_times)
        index = 0
        self.data = None

        #def my_progress_handler(progress, limit=0):
        #    logger.debug('calling progress handler with %s/%s' % (progress+index*count, limit*count))
        #    progress_handler(progress+index*count, limit*count)

        for inv_time in self.inv_times:
            progress_handler(index, count)
            logger.debug('running inversion time %s' % inv_time)
            self.programs['InversionRecoveryFID'].set_par('inversion_time', inv_time)
            await self.programs['InversionRecoveryFID'].run(message_handler=message_handler)
            run_data = self.programs['InversionRecoveryFID'].data.view(np.complex64)
            if self.data is None:
                self.data = np.array([run_data])
            else:
                self.data = np.append(self.data, [run_data], axis=0)
            index+=1
        progress_handler(index, count)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_T1(self):
        dwell_time = self.par['dwell_time']/1000000
        phase = np.angle(np.sum(self.raw_data()[-1])) # get average phase of last acquisition
        fft_mag = np.fft.fft(self.raw_data(), axis=1)*np.exp(1j * -phase)
        fft_mag *= dwell_time
        halfwidth = int(fft_mag.shape[1]*self.par['int_width']*dwell_time*500)+1
        y = np.sum(fft_mag[:,:halfwidth], axis=1) + np.sum(fft_mag[:,:-halfwidth:-1], axis=1)
        y /= (2*halfwidth+1)
        y *= self.par['int_width']/1000
        x = self.inv_times/1000000
        x = x[:len(y)]
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'x_unit': 's',
            'y_unit': 'V'}

    def export_Raw(self):
        return self.export_T1()

    # def export_default(self):
    #     return self.export_Raw()
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_T1(self):
        data = self.export_T1()
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
                    'title': 'T1',
                    'xaxis': {'title': 'Inversion Time (%s)' % data['x_unit']},
                    'yaxis': {'title': 'FT Integral (%s)' % data['y_unit']}
                }}
        if len(data['y_real']) == len(self.inv_times) and len(data['y_real']) > 3:
            def T1_fit_func(TI, A, B, T1):
                return A * (1 - (1 + B) * np.exp(-TI / T1))

            A_init = np.max(np.abs(data['y_real']))
            B_init = 1
            T1_init = data['x'][np.argmin(np.abs(data['y_real']))] / np.log(2)
            logger.debug('initial conditions: %s' % str([A_init, B_init, T1_init]))
            try:
                popt, pcov = curve_fit(T1_fit_func, np.array(data['x']), np.array(data['y_real']), p0=[A_init, B_init, T1_init])
                logger.debug('popt: %s' % str(popt))
                logger.debug('pcov: %s' % str(pcov))
                # return object according to plotly schema
                fit_x = np.linspace(data['x'][0], data['x'][-1], 1000)
                fit_y = T1_fit_func(fit_x, *popt)
                result['data'].append({
                    'name': 'Fit',
                    'type': 'scatter',
                    'x': fit_x,
                    'y': fit_y
                })
                result['layout']['title'] = 'T1: {:.3e} {}'.format(popt[2], data['x_unit'])
            except RuntimeError as e: # could not find acceptable fit
                logger.debug(e)
        return result

    def plot_FID(self):
        y = self.autophase(self.raw_data()[-1,:])
        x = np.linspace(0, self.par['dwell_time'] * len(y), len(y), endpoint=False)
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
                'title': 'FID',
                'xaxis': {'title': 's'},
                'yaxis': {'title': 'V'}
            }}

    def raw_data(self):
        return self.data

    def autophase(self, data):
        phase = get_autophase(data)
        return data * np.exp(1j * phase)  # rotate
