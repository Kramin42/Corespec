import React from 'react';
import * as d3 from 'd3';

import generateId from './util/generateId';
import {decode_plot_data} from './util/decode'
import {d3plot, d3plot_contour} from './d3plot';
import './css/d3plot.css';

import './css/Plot.css';

import Tabs from './Tabs';

export default class Plot extends React.Component {
  constructor(props) {
    super(props);

    this.svgid = generateId();

    let activePlotIndex = undefined;
    if (props.experiment && props.experiment.plots && this.props.defaultPlot) {
      activePlotIndex = props.experiment.plots.indexOf(this.props.defaultPlot);
    }

    this.state = {
      activePlotIndex: activePlotIndex,
      activeFormatIndex: 0,
      data: {}
    }

    this.handlePlotChange = this.handlePlotChange.bind(this);
    this.handleFormatChange = this.handleFormatChange.bind(this);
    this.replot = this.replot.bind(this);
  }

  replot(plotIndex) {
    console.log(plotIndex);
    if (plotIndex===null || plotIndex===undefined) {
      plotIndex = this.state.activePlotIndex;
    }
    if (this.props.plotMethod==='query') {
      return this.props.deviceQuery('plot', {
        experiment_name: this.props.experiment.name,
        plot_name: this.props.experiment.plots[plotIndex]
      })
      .then(result => {
        result.data = decode_plot_data(result.data);
        if (result.data[0].type === 'contour') {
          d3plot_contour(d3.select('#'+this.svgid), result);
        } else {
          d3plot(d3.select('#'+this.svgid), result);
        }
      })
      .catch(err => {
        console.log(err);
      });
    } else {
      console.log('cant replot without plotMethod=query');
    }
    return Promise.resolve();
  }

  handlePlotChange(tabIndex) {
    this.setState({
      activePlotIndex: tabIndex
    });
    this.replot(tabIndex);
  }

  handleFormatChange(tabIndex) {
    this.setState({
      activeFormatIndex: tabIndex
    });
  }

  componentDidUpdate(prevProps) {
    if (this.props.plotMethod === 'direct') {
      if (this.props.plot.id !== prevProps.plot.id) {
        d3plot(d3.select('#'+this.svgid), this.props.plot);
      }
    }
  }

  render() {
    const experiment = this.props.experiment || {};
    const plotNames = experiment.plots || [];
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
        <svg id={this.svgid} className="plot"></svg>
      </div>
    );
  };
}
