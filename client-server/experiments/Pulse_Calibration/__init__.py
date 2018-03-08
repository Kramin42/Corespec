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
    def override(self):
        del self.par_def['width_90']
        self.par_def['start_width'] = {'unit': 'us'}
        self.par_def['end_width'] = {'unit': 'us'}
        self.par_def['steps'] = {}

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None):
        widths = np.linspace(self.par['start_width'], self.par['end_width'], self.par['steps'])
        count = len(widths)
        index = 0
        self.data = np.array([])

        #def my_progress_handler(progress, limit=0):
        #    logger.debug('calling progress handler with %s/%s' % (progress+index*count, limit*count))
        #    progress_handler(progress+index*count, limit*count)

        for width in widths:
            logger.debug('running width %s' % width)
            self.programs['FID'].set_par('width_90', width)
            await self.programs['FID'].run()
            run_data = self.programs['FID'].data.astype(np.float32).view(np.complex64)
            self.data = np.append(self.data, np.max(np.abs(np.fft.fft(run_data))))
            progress_handler(index+1, count)
            index+=1
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_calibration(self):
        y = self.raw_data()
        x = np.linspace(self.par['start_width'], self.par['end_width'], self.par['steps'])
        return {
            'x': x.tolist(),
            'y': y.tolist(),
            'x_unit': 'μs'}
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_calibration(self):
        data = self.export_calibration()
        # return object according to plotly schema
        return {'data': [{
                    'name': 'Real',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y']}],
                'layout': {
                    'title': 'Pulse Width Calibration',
                    'xaxis': {'title': data['x_unit']},
                    'yaxis': {'title': 'FFT Max'}
                }}

    def raw_data(self):
        return self.data