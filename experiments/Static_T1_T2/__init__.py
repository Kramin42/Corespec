from experiment import BaseExperiment # required

# for debugging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import numpy as np
import asyncio

# All methods have access to the programs object, self.programs
# which contains the pulse programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment): # must be named 'Experiment'
    def override(self):
        del self.par_def['inversion_time']
        del self.par_def['or_mask']
        del self.par_def['and_mask']

    # must be async or otherwise return an awaitable
    async def run(self, progress_handler=None, message_handler=None):
        # turn OFF flow
        message_handler('Switching flow OFF')
        self.programs['TTLControl'].set_par('or_mask', 0x00000000)
        self.programs['TTLControl'].set_par('and_mask', ~0x00000200)  # TTL_IO_1 is at 0x00000200
        await self.programs['TTLControl'].run()
        await asyncio.sleep(self.par['flow_delay'])  # wait for flow to stabilise, in seconds
        message_handler('Starting measurement')

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
            index+=1
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
            apodization = np.exp(-np.log(apodization_factor)*np.linspace(0, 1, len(self.raw_data()[-1])))
        else:
            apodization = np.ones(len(self.raw_data()[-1]))
        apodization /= np.sum(apodization)
        y = np.sum(self.raw_data()*apodization, axis=1) / 1000000 # uV -> V
        phase = np.angle(y[-1])
        y *= np.exp(1j * -phase)
        x = self.inv_times / 1000000 # us -> s
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
            'inv_time': T1_axis[:,np.newaxis],
            'cpmg_time': T2_axis,
            'real': data.real,
            'imag': data.imag
        }

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
                    'yaxis': {'title': 'Signal Avg. (%s)' % data['y_unit']}
                }}
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
