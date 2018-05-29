import React from 'react';

import './css/ExperimentPanes.css'

import Experiment from './Experiment'

export default class ExperimentPanes extends React.Component {
  render() {
    const experiments = this.props.experiments;
    const experimentIndex = this.props.activeExperimentIndex;
    let expPanes = [];
    experiments.forEach((experiment, i) => {
      expPanes.push(
        <Experiment experiment={experiment} active={experimentIndex===i} />
      );
    });
    return (
      <div className="tab-panes">{expPanes}</div>
    );
  };
}
