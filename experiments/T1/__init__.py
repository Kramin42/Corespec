from experiment import BaseExperiment # required

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
            self.programs['InversionRecovery'].set_par('inversion_time', inv_time)
            await self.programs['InversionRecovery'].run(message_handler=message_handler)
            run_data = self.programs['InversionRecovery'].data.astype(np.float32).view(np.complex64)
            samples = int(self.par['samples'])
            echo_count = int(self.par['echo_count'])
            y = np.zeros(echo_count, dtype=np.complex64)
            for i in range(echo_count):
                y[i] = np.mean(run_data[i * samples:(i + 1) * samples])
            if self.data is None:
                self.data = np.array([y])
            else:
                self.data = np.append(self.data, [y], axis=0)
            index+=1
        progress_handler(index, count)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_T1(self):
        y = np.mean(self.raw_data(), axis=1)
        x = self.inv_times / 1000000
        return {
            'x': x,
            'y': y,
            'x_unit': 's',
            'y_unit': 'V'}

    def export_Raw(self):
        return self.export_T1()
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_T1(self):
        data = self.export_T1()
        result = {'data': [{
            'name': 'Data',
            'type': 'scatter',
            'x': data['x'],
            'y': data['y']
        }],
            'layout': {
                'title': 'T1',
                'xaxis': {'title': 'Inversion Time (%s)' % data['x_unit']},
                'yaxis': {'title': 'FT Integral Mag. (%s)' % data['y_unit']}
            }}
        if len(data['y']) == len(data['x']) and len(data['y']) > 3:
            def T1_fit_func(TI, A, B, T1):
                return A * np.abs((1 + B) * np.exp(-TI / T1) - 1)

            A_init = np.max(data['y'])
            B_init = 1
            T1_init = data['x'][np.argmin(data['y'])] / np.log(2)
            logger.debug('initial conditions: %s' % str([A_init, B_init, T1_init]))
            popt, pcov = curve_fit(T1_fit_func, np.array(data['x']), np.array(data['y']), p0=[A_init, B_init, T1_init])
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
        return result

    def plot_CPMG(self):
        y = self.autophase(self.raw_data()[-1,:])
        x = np.linspace(0, self.par['echo_time'] * len(y), len(y), endpoint=False)
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
                'title': 'CPMG Echo Integrals',
                'xaxis': {'title': 's'},
                'yaxis': {'title': 'V'}
            }}

    def raw_data(self):
        return self.data

    def autophase(self, data):
        phase = np.angle(np.sum(data)) # get average phase
        return data * np.exp(1j * -phase) # rotate
