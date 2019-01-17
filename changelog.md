# Changelog

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
