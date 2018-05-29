import React from 'react';
import { Line } from 'rc-progress';

import './css/Progress.css';

export default class ProgressBar extends React.Component {
  render() {
    return (
      <div className="progress-container">
        <Line percent="50" trailWidth="3" strokeWidth="3" strokeColor="#62ab37" />
      </div>
    );
  };
}
