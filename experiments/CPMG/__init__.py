import numpy as np
import logging

from experiment import BaseExperiment

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment):
    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None):
        await self.programs['CPMG'].run(progress_handler=progress_handler)
    
    # start a function name with "filter_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def filter_real_imag(self):
        data = programs['CPMG'].data
        par = programs['CPMG'].par
        # deinterleave
        data = data.astype(np.float32).view(np.complex64)
        # phase
        if 'phaseRx' in par:
            data = data*np.exp(1j*np.pi*par['phaseRx']/180)
        return {'real': data.real.tolist(), 'imag': data.imag.tolist(), 'unit': 'μV'}
    
    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_real_imag(self):
        data = self.filter_real_imag()
        # return object according to plotly schema
        return {'data': [{
                    'name': 'Real',
                    'type': 'scatter',
                    'x': list(range(len(data['real']))),
                    'y': data['real']}, {
                    'name': 'Imag',
                    'type': 'scatter',
                    'x': list(range(len(data['imag']))),
                    'y': data['imag']}],
                'layout': {
                    'title': 'Real/Imaginary data',
                    'yaxis': {'title': data['unit']}
                }}

