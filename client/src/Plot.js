import React from 'react';

import './css/Plot.css';

import Tabs from './Tabs';

export default class Plot extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      activePlotIndex: 0,
      activeFormatIndex: 0
    }

    this.handlePlotChange = this.handlePlotChange.bind(this);
    this.handleFormatChange = this.handleFormatChange.bind(this);
  }

  handlePlotChange(tabIndex) {
    this.setState({
      activePlotIndex: tabIndex
    });
  }

  handleFormatChange(tabIndex) {
    this.setState({
      activeFormatIndex: tabIndex
    });
  }

  render() {
    const plotNames = ['Raw', 'FFT'];
    const formats = ['PNG', 'SVG'];
    return (
      <div className="plot-container">
        <div className="plot-controls">
          <Tabs
            tabNames={plotNames}
            activeIndex={this.state.activePlotIndex}
            onTabChange={this.handlePlotChange}
          />
          <div className="plot-export-controls">
            <Tabs
              tabNames={formats}
              activeIndex={this.state.activeFormatIndex}
              onTabChange={this.handleFormatChange}
            />
            <div className="button">Save</div>
          </div>
        </div>
        <svg className="plot" viewbox="0 0 600 400"></svg>
      </div>
    );
  };
}
