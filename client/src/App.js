import React from 'react';

import './css/App.css';
import './css/Buttons.css';

import Tabs from './Tabs';
import ExperimentPanes from './ExperimentPanes';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      experiments: props.experiments,
      activeExperimentIndex: 0
    };

    // bind 'this' as context to handlers
    this.handleTabChange = this.handleTabChange.bind(this);
  }

  handleTabChange(tabIndex) {
    this.setState({
      activeExperimentIndex: tabIndex
    });
  }

  render() {
    return (
      <div className="app-container">
        <Tabs
          tabNames={this.state.experiments.map(e => e.name)}
          activeIndex={this.state.activeExperimentIndex}
          onTabChange={this.handleTabChange}
        />
        <ExperimentPanes
          experiments={this.state.experiments}
          activeExperimentIndex={this.state.activeExperimentIndex}
        />
      </div>
    );
  };
}
