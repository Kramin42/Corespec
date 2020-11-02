# Changelog

## [1.2.3] - 2020-11-02
### Added
- 2D Saturation Recovery CPMG experiment (SR-CPMG).
- D-T2 experiment for the diffusion gradient board. Small delta is named `grad_time` and big Delta is named `diff_time`, the echo time of the first echo will be `2*diff_time`.
- Constant gradient CPMG experiment for the diffusion board. NOTE: Gradient amplitude limited to 10% of full range.

### Changed/Fixed
- MRI 1D SE: Echo Time now correctly defines the time from the centre of the 90 pulse to the centre of the echo.
- T1-T2 renamed to IR-CPMG.
- IR-CPMG, T1 FID: Inversion Time now defines the time between the *centres* of the inversion pulse and the 90 pulse, rather than the time from the end of the inversion pulse to the start of the 90 pulse.

## [1.2.2] - 2020-06-22
### Added
- Autoshim experiment for MRI gradient board

### Changed
- Improved reconnection behaviour to prevent data loss
- Linewidth calculation added to FID experiment

### Removed
- MRI PGSE, use DIFF PGSE with diffusion board instead
- DIFF 1D, use MRI 1D with MRI board instead

## [1.2.1] - 2020-04-22
### Changed
- Added MRI shim parameters to most experiments (only applicable with 3-channel MRI board).
- Reworked UI layout.

## [1.1.18d] - 2020-04-09
### Fixed
- Fixed inversion recovery CPMG program gating heater off longer than needed.

## [1.1.18c] - 2020-03-16
### Fixed
- MRI 1D program Z gradient enable TTL issue.

## [1.1.18b] - 2020-03-05
### Fixed
- Fixed heater PWM signal.

## [1.1.18] - 2020-01-21
### Added
- 1D & 2D Spin Echo MRI experiments, using MRI gradient board.
- PGSE experiment using X channel of MRI gradient board (named "MRI PGSE").

## [1.1.17] - 2019-09-26
### Fixed
- Changed heating to only gate off during acquisition, not entire pulse program.

## [1.1.16] - 2019-08-12
### Added
- Support for diffusion gradient.
- 1D MRI experiment using diffusion gradient.
- PGSE experiment using diffusion gradient.

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
- T1 FID experiment using inversion recovery with FID acquisition.

## [1.1.5] - 2018-10-11
### Added
- T1 experiment using inversion recovery with a CPMG train for acquisition.
- Power Calibration experiment.

## [1.1.4] - 2018-09-28
### Added
- FID Magnitude curve on time domain and frequency domain plots.
- Estimated f\_0 frequency in title of FID frequency domain plot.
- Exported data files include parameter values.
- CPMG SNR estimate message.
