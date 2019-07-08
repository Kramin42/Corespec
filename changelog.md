# Changelog

## [1.1.15] - 2019-07-08
### Added
- Experimental Variable Echo Spacing CPMG.

## [1.1.14] - 2019-06-11
### Added
- T2 Spin Echo Experiment: Runs Spin Echo experiments for a range of echo times.

## [1.1.13] - 2019-06-10
### Added
- More accurate autophase for all experiments, will accurately phase off-centre frequency components.
- Added acquisition shift parameter to Spin Echo experiment, for asymmetrical sampling.

## [1.1.12] - 2019-06-05
### Added
- Spin Echo experiment.

## [1.1.11] - 2019-04-23
### Added
- Different export options for experiments, e.g. Raw and Echo Integrals for CPMG.
- Faster plotting in CPMG experiment with large echo counts, by decimating plot data.

## [1.1.10] - 2019-03-21
### Added
- T1-T2 Experiment with 2D inversion laplace.
- CPMG experiment export includes laplace inversion spectrum
### Removed
- Pulse Calibration, Power Calibration is more useful

## [1.1.9] - 2018-12-17
### Added
- Ability to change the WiFi password on the /admin page.

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
