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
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, warning_handler=None):
        await self.programs['Wobble'].run(progress_handler=progress_handler,
                                          warning_handler=warning_handler)
    
    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_wobble(self):
        data = self.raw_data()
        width = self.par['bandwidth']
        center = self.par['freq']
        samples = self.par['samples']

        y = data.astype(np.float32)
        y = np.mean(y.reshape(-1, samples), axis=1)
        x = np.linspace(center-width/2, center+width/2, len(y))
        return {
            'x': x,
            'y': y,
            'x_unit': 'MHz'}
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_wobble(self):
        data = self.export_wobble()
        min_i = np.argmin(data['y'])
        # return object according to plotly schema
        return {'data': [{
                    'name': 'Wobble',
                    'type': 'scatter',
                    'x': data['x'],
                    'y': data['y']}],
                'layout': {
                    'title': 'Wobble, Min: ({:.4g},{:.4g})'.format(data['x'][min_i], data['y'][min_i]),
                    'xaxis': {'title': data['x_unit']}
                }}

    def raw_data(self):
        return self.programs['Wobble'].data
