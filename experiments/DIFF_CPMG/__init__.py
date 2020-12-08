from experiment import BaseExperiment  # required
from libraries.expfitting import fit_single_exp

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
        del self.par_def['echo_time']
        del self.par_def['echo_count']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        self.echo_times = np.round(np.logspace(
            np.log10(self.par['TE_start']),
            np.log10(self.par['TE_end']),
            int(self.par['TE_steps']),
            endpoint=True)).astype(np.int)
        self.echo_counts = np.round(np.logspace(
            np.log10(self.par['NE_start']),
            np.log10(self.par['NE_end']),
            int(self.par['TE_steps']),
            endpoint=True)).astype(np.int)

        self.data = np.zeros((self.echo_counts.shape[0], self.echo_counts.max()), dtype=np.complex64)
        self.T2s = []
        self.last_index = 0
        for i, (TE, NE) in enumerate(zip(self.echo_times, self.echo_counts)):
            if progress_handler is not None:
                progress_handler(i, len(self.echo_times))
            self.programs['DIFF_CPMG'].set_par('echo_time', TE)
            self.programs['DIFF_CPMG'].set_par('echo_count', NE)
            await self.programs['DIFF_CPMG'].run(message_handler=message_handler)
            run_data = self.programs['DIFF_CPMG'].data.view(np.complex64)
            samples = int(self.par['samples'])
            y = np.mean(np.reshape(run_data, (NE, samples)), axis=1)
            self.data[i, :NE] = y

            # exp fitting
            x = np.linspace(0, TE*1e-6 * len(y), len(y), endpoint=False)
            T2 = 0
            try:
                popt, stderr = fit_single_exp(x, self.autophase(y).real)
                logger.debug('fit_single_exp() popt: %s' % str(popt))
                T2 = 1 / popt[1]
            except (ValueError, RuntimeError):
                pass
            self.T2s.append(T2)

            self.last_index = i
        if progress_handler is not None:
            progress_handler(len(self.echo_times), len(self.echo_times))

    def export_Raw(self):
        phase = np.angle(np.sum(self.raw_data()[0, :self.echo_counts[0]]))
        data = self.raw_data() * np.exp(1j * -phase)
        data /= 1000000  # uV -> V
        TE_axis = np.array(self.echo_times)/1000000  # us -> s
        NE_axis = np.array(range(data.shape[1]))
        return {
            'echo_time_axis': TE_axis[:, np.newaxis],
            'echo_count_axis': self.echo_counts[:, np.newaxis],
            'echo_index_axis': NE_axis[np.newaxis, :],
            'y_real': data.real,
            'y_imag': data.imag,
            'y_units': 'V',
            'echo_time_units': 's'
        }
    
    def plot_CPMG(self):
        y = self.autophase(self.raw_data()[self.last_index, :self.echo_counts[self.last_index]])
        x = np.linspace(0, self.echo_times[self.last_index] * len(y), len(y), endpoint=False)
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

    def plot_T2(self):
        y = np.array(self.T2s)
        x = np.array(self.echo_times[:len(y)])/1000000  # us -> s
        result = {'data': [{
            'name': 'T2',
            'type': 'scatter',
            'x': x,
            'y': y
        }],
            'layout': {
                'title': 'T2 vs TE',
                'xaxis': {'title': 'TE (s)'},
                'yaxis': {'title': 'T2 (s)'}
            }}
        return result


    def raw_data(self):
        if self.data is None:
            raise Exception('Data not ready!')
        return self.data

    def autophase(self, data):
        phase = -np.angle(np.sum(data))  # use simple method for CPMG
        return data * np.exp(1j * phase)  # rotate
