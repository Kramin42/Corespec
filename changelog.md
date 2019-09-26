# Changelog

## [1.1.14] - 2019-09-26
### fixed
- Changed heating to only gate off during acquisition, not entire pulse program.

## [1.1.13] - 2019-03-12
### Added
- Flowmeter and Flow_T2 experiments now take the parameters flow\_crop,
  flow\_thresh\_l, and flow\_thresh\_h to define the region of the CPMG curve
  to be linearly fit. Use 0, 0.0, and 1.0 respectively to fit the whole curve.


## [1.1.12] - 2019-03-09
### Added
- Flowmeter experiment, and separate high-level UI at /flowmeter.
  Parameters must be saved to a parameter set named 'flowmeter' from the
  Flowmeter experiment for the high-level UI to run.

## [1.1.11] - 2019-02-18
### Added
- Mass Flow experiment now has automatic find freq feature which is
  able to fine tune the frequency to allow for temperature variation etc.

## [1.1.10] - 2019-02-15
### Added
- Mass Flow experiment, runs Static T2 and Flow T2
  and reports flow rates of oil, water, and gas components

## [1.1.9] - 2019-01-17
### Added
- Flow T2 Experiment now calculates flow rate using simple slope/intercept
  method with a calibration parameter
- Static T2 Experiment calculates proportion of water and oil volumes, with a
  calibration parameter for the different proton density of oil

## [1.1.8] - 2018-12-06
### Added
- Temperature control will disable heater and report an error when an invalid
reading is detected

## [1.1.7] - 2018-10-23
### Bug Fixes
- Fixed accumulation overflow error when running many scans.

## [1.1.6] - 2018-10-12
### Added
- T1_FID experiment using inversion recovery with FID acquisition.

## [1.1.5] - 2018-10-11
### Added
- T1 experiment using inversion recovery with a CPMG train for acquisition.
- Power Calibration experiment.

## [1.1.4] - 2018-09-28
### Added
- FID Magnitude curve on time domain and frequency domain plots.
- Estimated f_0 frequency in title of FID frequency domain plot.
- Exported data files include parameter values.
- CPMG SNR estimate message.
