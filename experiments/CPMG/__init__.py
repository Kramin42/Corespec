import numpy as np
import logging

from experiment import BaseExperiment

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# All methods have access to the programs object, self.programs
# which contains the programs listed in config.yaml
# e.g. self.programs['CPMG'] to access the CPMG program

class Experiment(BaseExperiment):
    def run(self):
        logger.debug('running %s...' % self.name)
