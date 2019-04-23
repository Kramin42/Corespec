from experiment import BaseExperiment  # required
from libraries.invlaplace import getT1T2Spectrum

# for debugging
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np
import asyncio


# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment):  # must be named 'Experiment'
    def override(self):
        del self.par_def['inversion_time']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        self.inv_times = np.logspace(np.log10(self.par['start_inv_time']), np.log10(self.par['end_inv_time']),
                                     self.par['steps'])
        count = len(self.inv_times)
        index = 0
        self.data = None

        # def my_progress_handler(progress, limit=0):
        #    logger.debug('calling progress handler with %s/%s' % (progress+index*count, limit*count))
        #    progress_handler(progress+index*count, limit*count)

        for inv_time in self.inv_times:
            progress_handler(index, count)
            logger.debug('running inversion time %s' % inv_time)
            self.programs['InversionRecoveryCPMG'].set_par('inversion_time', inv_time)
            await self.programs['InversionRecoveryCPMG'].run(message_handler=message_handler)
            run_data = self.programs['InversionRecoveryCPMG'].data.view(np.complex64)
            samples = int(self.par['samples'])
            echo_count = int(self.par['echo_count'])
            y = np.zeros(echo_count, dtype=np.complex64)
            for i in range(echo_count):
                y[i] = np.mean(run_data[i * samples:(i + 1) * samples])
            if self.data is None:
                self.data = np.array([y])
            else:
                self.data = np.append(self.data, [y], axis=0)
            index += 1
        progress_handler(index, count)

    # start a function name with "export_" for it to be listed as an export format
    # it must take no arguments and return a JSON serialisable dict
    def export_T1(self):
        # dynamic apodization factor
        if len(self.raw_data()[-1]) >= 10:
            apodization_factor = np.abs(np.sum(self.raw_data()[-1].real[:4]) / np.sum(self.raw_data()[-1].real[-4:]))
            if apodization_factor < 1:
                apodization_factor = 1
            logger.debug('Apodisation factor: %s' % str(apodization_factor))
            apodization = np.exp(-np.log(apodization_factor) * np.linspace(0, 1, len(self.raw_data()[-1])))
        else:
            apodization = np.ones(len(self.raw_data()[-1]))
        apodization /= np.sum(apodization)
        y = np.sum(self.raw_data() * apodization, axis=1) / 1000000  # uV -> V
        phase = np.angle(y[-1])
        y *= np.exp(1j * -phase)
        x = self.inv_times / 1000000  # us -> s
        x = x[:len(y)]
        return {
            'x': x,
            'y_real': y.real,
            'y_imag': y.imag,
            'x_unit': 's',
            'y_unit': 'V'}

    def export_Raw(self):
        phase = np.angle(np.sum(self.raw_data()[-1, :]))
        data = self.raw_data() * np.exp(1j * -phase)
        T1_axis = self.inv_times / 1000000  # us -> s
        T2_axis = np.linspace(0, self.par['echo_time'] * data.shape[1], data.shape[1], endpoint=False) / 1000000
        return {
            'inv_time': T1_axis[:, np.newaxis],
            'cpmg_time': T2_axis,
            'real': data.real,
            'imag': data.imag
        }

    def export_2D(self):
        data = self.export_Raw()
        if data['real'].shape[0] < int(self.par['steps']):
            raise Exception('2D data not ready!')
        N = 50  # TODO: parameterise
        T1 = np.logspace(-5, 2, N+1, endpoint=True)[np.newaxis, :]
        T2 = np.logspace(-5, 2, N+1, endpoint=True)[np.newaxis, :]
        t_inv = data['inv_time'][:, 0]
        t_cpmg = data['cpmg_time']
        S = getT1T2Spectrum(t_inv, t_cpmg, data['real'], data['imag'], T1, T2, alpha=1, cpmg_pts=50)

        return {
            'T1': T1,
            'T2': T2,
            'S': S
        }

    # def export_default(self):
    #     export = self.export_Raw()
    #     export_spectrum = self.export_2D()
    #     export['spectrum_T1'] = export_spectrum['T1']
    #     export['spectrum_T2'] = export_spectrum['T2']
    #     export['spectrum'] = export_spectrum['S'].reshape((export_spectrum['T1'].size, export_spectrum['T2'].size))
    #     return export

    # start a function name with "plot_" for it to be listed as a plot type
    # it must take no arguments and return a JSON serialisable dict
    def plot_T1(self):
        data = self.export_T1()
        result = {'data': [{
            'name': 'Real',
            'type': 'scatter',
            'x': data['x'],
            'y': data['y_real']
        }, {
            'name': 'Imag',
            'type': 'scatter',
            'x': data['x'],
            'y': data['y_imag']
        }],
            'layout': {
                'title': 'T1',
                'xaxis': {'title': 'Inversion Time (%s)' % data['x_unit']},
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

    def plot_2D(self):
        data = self.export_2D()
        return {'data': [{
            'name': '',
            'type': 'contour',
            'x': data['T2'],
            'y': data['T1'],
            'z': data['S'].ravel()}],
            'layout': {
                'title': 'T1-T2 map',
                'xaxis': {'title': 'T2 (s)'},
                'yaxis': {'title': 'T1 (s)'}
            }}

    def raw_data(self):
        if self.data is None:
            raise Exception('Data not ready!')
        return self.data

    def autophase(self, data):
        phase = np.angle(np.sum(data))  # get average phase
        return data * np.exp(1j * -phase)  # rotate