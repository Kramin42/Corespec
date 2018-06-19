import React from 'react';
import { Line } from 'rc-progress';

import './css/Progress.css';

export default class ProgressBar extends React.Component {
  render() {
    const progressPercent = 100*this.props.progress/this.props.progressMax;
    return (
      <div className="progress-container">
        <Line percent={progressPercent} trailWidth="3" strokeWidth="3" strokeColor="#62ab37" />
      </div>
    );
  };
}
