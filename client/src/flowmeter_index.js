import ReactDOM from 'react-dom';
import React from 'react';

import Flowmeter from './Flowmeter';

ReactDOM.render(
  <Flowmeter server={`ws://${window.location.hostname}:8765`} />,
  document.getElementById('app')
);
