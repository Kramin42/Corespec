import React from 'react';

import './css/RunControls.css'

export default class RunControls extends React.Component {
  render() {
    return (
      <div className="run-controls">
        <div className="button run">Run</div>
        <div className="button run-loop">Run Loop</div>
        <div className="button abort">Abort</div>
      </div>
    );
  };
}
