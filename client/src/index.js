import ReactDOM from 'react-dom';
import React from 'react';

import App from './App';

const EXPERIMENTS = [{
  "name": "CPMG",
  "description": "A CPMG experiment.",
  "parameters": {
    "freq": {
      "dtype": "float64",
      "unit": "MHz",
      "shared": true,
      "group": "pulse"
    },
    "phase": {
      "offset": 144,
      "dtype": "float64",
      "unit": "deg"
    },
    "amp_90": {
      "offset": 152,
      "dtype": "float32",
      "min": 0,
      "max": 100,
      "unit": "%",
      "scaling": 0.01,
      "shared": true,
      "group": "pulse"
    },
    "amp_180": {
      "offset": 160,
      "dtype": "float32",
      "min": 0,
      "max": 100,
      "unit": "%",
      "scaling": 0.01,
      "shared": true,
      "group": "pulse"
    },
    "width_90": {
      "offset": 168,
      "dtype": "uint32",
      "min": 0,
      "max": 500,
      "unit": "us",
      "scaling": 1000,
      "shared": true,
      "group": "pulse"
    },
    "width_180": {
      "offset": 172,
      "dtype": "uint32",
      "min": 0,
      "max": 500,
      "unit": "us",
      "scaling": 1000,
      "shared": true,
      "group": "pulse"
    },
    "damp_time": {
      "offset": 188,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 1000,
      "shared": true,
      "group": "pulse"
    },
    "echo_time": {
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 1000,
      "group": "pulse"
    },
    "echo_shift": {
      "dtype": "int32",
      "unit": "us",
      "scaling": 1000,
      "group": "acquisition"
    },
    "rep_time": {
      "offset": 212,
      "dtype": "uint64",
      "min": 0,
      "unit": "s",
      "scaling": 1000000000,
      "group": "pulse"
    },
    "echo_count": {
      "offset": 192,
      "dtype": "uint32",
      "min": 1,
      "group": "acquisition"
    },
    "samples": {
      "offset": 196,
      "dtype": "uint32",
      "min": 1,
      "group": "acquisition"
    },
    "dwell_time": {
      "offset": 204,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 100,
      "group": "acquisition"
    },
    "scans": {
      "offset": 208,
      "dtype": "uint32",
      "min": 1,
      "group": "acquisition"
    }
  },
  "exports": ["echo_envelope", "echo_integrals", "real_imag"],
  "plots": ["echo_envelope", "echo_integrals", "real_imag"],
  "defaults": {
    "plots": ["real_imag", "echo_integrals"]
  }
}, {
  "name": "FID",
  "description": "A FID experiment.",
  "parameters": {
    "freq": {
      "dtype": "float64",
      "unit": "MHz"
    },
    "phase": {
      "offset": 144,
      "dtype": "float64"
    },
    "amp_90": {
      "offset": 152,
      "dtype": "float32",
      "min": 0,
      "max": 100,
      "unit": "%",
      "scaling": 0.01
    },
    "width_90": {
      "offset": 168,
      "dtype": "uint32",
      "min": 0,
      "max": 500,
      "unit": "us",
      "scaling": 1000
    },
    "damp_time": {
      "offset": 188,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 1000
    },
    "acq_delay": {
      "offset": 176,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 1000
    },
    "rep_time": {
      "offset": 212,
      "dtype": "uint64",
      "min": 0,
      "unit": "s",
      "scaling": 1000000000
    },
    "samples": {
      "offset": 196,
      "dtype": "uint32",
      "min": 1
    },
    "dwell_time": {
      "offset": 204,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 100
    },
    "scans": {
      "offset": 208,
      "dtype": "uint32",
      "min": 1
    }
  },
  "exports": ["FFT", "real_imag"],
  "plots": ["FFT", "real_imag"],
  "defaults": {
    "plots": ["real_imag", "FFT"]
  }
}, {
  "name": "Noise",
  "description": "A Noise experiment.",
  "parameters": {
    "freq": {
      "dtype": "float64",
      "unit": "MHz"
    },
    "samples": {
      "offset": 196,
      "dtype": "uint32",
      "min": 1
    },
    "dwell_time": {
      "offset": 204,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 100
    }
  },
  "exports": ["FFT", "Noise"],
  "plots": ["FFT", "Noise"],
  "defaults": {
    "plots": ["Noise", "FFT"]
  }
}, {
  "name": "Pulse_Calibration",
  "description": "An experiment for calibrating pulse power/width.",
  "parameters": {
    "freq": {
      "dtype": "float64",
      "unit": "MHz"
    },
    "phase": {
      "offset": 144,
      "dtype": "float64"
    },
    "amp_90": {
      "offset": 152,
      "dtype": "float32",
      "min": 0,
      "max": 100,
      "unit": "%",
      "scaling": 0.01
    },
    "damp_time": {
      "offset": 188,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 1000
    },
    "acq_delay": {
      "offset": 176,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 1000
    },
    "rep_time": {
      "offset": 212,
      "dtype": "uint64",
      "min": 0,
      "unit": "s",
      "scaling": 1000000000
    },
    "samples": {
      "offset": 196,
      "dtype": "uint32",
      "min": 1
    },
    "dwell_time": {
      "offset": 204,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 100
    },
    "scans": {
      "offset": 208,
      "dtype": "uint32",
      "min": 1
    },
    "start_width": {
      "unit": "us"
    },
    "end_width": {
      "unit": "us"
    },
    "steps": {
      "dtype": "int32"
    },
    "int_width": {
      "min": 0,
      "unit": "kHz"
    }
  },
  "exports": ["Calibration"],
  "plots": ["Calibration", "FID"],
  "defaults": {
    "plots": ["FID", "Calibration"]
  }
}, {
  "name": "Wobble",
  "description": "A Wobble experiment.",
  "parameters": {
    "freq": {
      "dtype": "float64",
      "unit": "MHz"
    },
    "amp": {
      "offset": 152,
      "dtype": "float32",
      "min": 0,
      "max": 100,
      "unit": "%",
      "scaling": 0.01
    },
    "steps": {
      "offset": 192,
      "dtype": "uint32",
      "min": 1
    },
    "samples": {
      "offset": 196,
      "dtype": "uint32",
      "min": 1
    },
    "dwell_time": {
      "offset": 204,
      "dtype": "uint32",
      "min": 0.5,
      "unit": "us",
      "scaling": 100
    },
    "bandwidth": {
      "offset": 220,
      "dtype": "float64",
      "unit": "MHz"
    }
  },
  "exports": ["wobble"],
  "plots": ["wobble"],
  "defaults": {}
}];

ReactDOM.render(
  <App experiments={EXPERIMENTS} />,
  document.getElementById('app')
);
