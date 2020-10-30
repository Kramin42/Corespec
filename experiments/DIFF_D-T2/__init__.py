from experiment import BaseExperiment # required
from libraries.invlaplace import getT2Spectrum
from libraries.autophase import get_autophase

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
        del self.par_def['grad_amp']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        self.grads = np.linspace(0, int(self.par['max_grad']), int(self.par['grad_steps']), endpoint=True)
        self.data = None
        for i, G in enumerate(self.grads):
            if progress_handler is not None:
                progress_handler(i, len(self.grads))
            self.programs['DIFF_PGSE_CPMG'].set_par('grad_amp', G)
            await self.programs['DIFF_PGSE_CPMG'].run(message_handler=message_handler)
            run_data = self.programs['DIFF_PGSE_CPMG'].data.view(np.complex64)
            samples = int(self.par['samples'])
            echo_count = int(self.par['echo_count'])
            y = np.mean(np.reshape(run_data, (echo_count, samples)), axis=1)
            if self.data is None:
                self.data = np.array([y])
            else:
                self.data = np.append(self.data, [y], axis=0)
        if progress_handler is not None:
            progress_handler(len(self.grads), len(self.grads))

    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_Diffusion(self):
        # dynamic apodization factor
        if len(self.raw_data()[-1]) >= 10:
            apodization_factor = np.abs(np.sum(self.raw_data()[-1][:4])) / np.abs(np.sum(self.raw_data()[-1][-4:]))
            if apodization_factor < 1:
                apodization_factor = 1
            logger.debug('Apodisation factor: %s' % str(apodization_factor))
            apodization = np.exp(-np.log(apodization_factor) * np.linspace(0, 1, len(self.raw_data()[-1])))
        else:
            apodization = np.ones(len(self.raw_data()[0]))
        apodization /= np.sum(apodization)
        y = np.abs(np.sum(self.raw_data() * apodization, axis=1))
        y /= 1000000 # uV -> V
        x = self.grads
        x = x[:len(y)]
        return {
            'x': x,
            'y': y,
            'x_unit': 'arb. G',
            'y_unit': 'V'}

    def export_Raw(self):
        phase = np.angle(np.sum(self.raw_data()[0, :]))
        data = self.raw_data() * np.exp(1j * -phase)
        G_axis = self.grads
        T2_axis = np.linspace(0, self.par['echo_time'] * data.shape[1], data.shape[1], endpoint=False) / 1000000
        return {
            'grad_axis': G_axis[:, np.newaxis],
            'time_axis': T2_axis[np.newaxis, :],
            'y_real': data.real,
            'y_imag': data.imag,
            'y_units': 'V',
            'time_units': 's'
        }

    def plot_Diffusion(self):
        data = self.export_Diffusion()
        result = {'data': [{
            'name': 'Mag',
            'type': 'scatter',
            'x': data['x'],
            'y': data['y']
        }],
            'layout': {
                'title': 'Diffusion',
                'xaxis': {'title': 'Gradient (%s)' % data['x_unit']},
                'yaxis': {'title': 'Signal Avg. (%s)' % data['y_unit']}
            }}
        return result

    def plot_CPMG(self):
        y = self.autophase(self.raw_data()[-1, :])
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
        if self.data is None:
            raise Exception('Data not ready!')
        return self.data

    def autophase(self, data):
        phase = -np.angle(np.sum(data))  # use simple method for CPMG
        return data * np.exp(1j * phase)  # rotate
