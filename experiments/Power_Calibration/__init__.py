from experiment import BaseExperiment # required

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    def override(self):
        del self.par_def['amp_90']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        amps = np.linspace(self.par['start_amp'], self.par['end_amp'], self.par['steps'])
        count = len(amps)
        index = 0
        self.data = None

        #def my_progress_handler(progress, limit=0):
        #    logger.debug('calling progress handler with %s/%s' % (progress+index*count, limit*count))
        #    progress_handler(progress+index*count, limit*count)

        for amp in amps:
            progress_handler(index, count)
            logger.debug('running amplitude %s' % amp)
            self.programs['FID'].set_par('amp_90', amp)
            await self.programs['FID'].run(message_handler=message_handler)
            run_data = self.programs['FID'].data.astype(np.float32).view(np.complex64)
            #self.data = np.append(self.data, np.max(np.abs(np.fft.fft(run_data))))
            if self.data is None:
                self.data = np.array([run_data])
            else:
                self.data = np.append(self.data, [run_data], axis=0)
            index+=1
        progress_handler(index, count)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Calibration(self):
        dwell_time = self.par['dwell_time']/1000000
        fft_mag = np.abs(np.fft.fft(self.raw_data(), axis=1))
        fft_mag *= dwell_time
        halfwidth = int(fft_mag.shape[1]*self.par['int_width']*dwell_time*500)+1
        y = np.sum(fft_mag[:,:halfwidth], axis=1) + np.sum(fft_mag[:,:-halfwidth:-1], axis=1)
        y /= (2*halfwidth+1)
        y *= self.par['int_width']/1000
        x = np.linspace(self.par['start_amp'], self.par['end_amp'], self.par['steps'])
        return {
            'x': x,
            'y': y,
            'x_unit': '%',
            'y_unit': 'V'}

    def export_Raw(self):
        return self.export_Calibration()
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_Calibration(self):
        data = self.export_Calibration()
        # return object according to plotly schema
        return {'data': [{
                    'name': '',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y']}],
                'layout': {
                    'title': 'Pulse Power Calibration',
                    'xaxis': {'title': data['x_unit']},
                    'yaxis': {'title': 'FT Integral (%s)' % data['y_unit']}
                }}

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
        phase = np.angle(np.sum(data)) # get average phase
        return data * np.exp(1j * -phase) # rotate
