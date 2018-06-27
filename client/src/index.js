import ReactDOM from 'react-dom';
import React from 'react';

import App from './App';

ReactDOM.render(
  <App server={`ws://${window.location.hostname}:8765`} />,
  document.getElementById('app')
);
