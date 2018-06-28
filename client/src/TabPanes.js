import React from 'react';

import './css/TabPanes.css';

import Experiment from './Experiment';
import Temperature from './Temperature';

export default class TabPanes extends React.Component {
  render() {
    const data = this.props.data;
    const activeIndex = this.props.activeIndex;
    let panes = [];
    data.forEach((d, i) => {
      if (d.name==='Temperature') {
        panes.push(
          <Temperature
            key={i}
            data={d}
            active={activeIndex===i}
            temperature={this.props.temperature}
            parValues={this.props.parValues}
            setPar={this.props.setPar}
            deviceCommand={this.props.deviceCommand}
            deviceQuery={this.props.deviceQuery}
            messages={this.props.messages}
            language={this.props.language}
          />
        );
      } else {
        panes.push(
          <Experiment
            key={i}
            experiment={d}
            active={activeIndex===i}
            parValues={this.props.parValues}
            setPar={this.props.setPar}
            deviceCommand={this.props.deviceCommand}
            deviceQuery={this.props.deviceQuery}
            setRunning={value => this.props.setRunning(i, value)}
            messages={this.props.messages}
            language={this.props.language}
          />
        );
      }
    });
    return (
      <div className="tab-panes">{panes}</div>
    );
  };
}
