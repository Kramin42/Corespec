import React from 'react';
import * as d3 from 'd3';
import moment from 'moment';
import {saveSvgAsPng} from 'save-svg-as-png';
import * as d3SaveSvg from 'd3-save-svg';

import generateId from './util/generateId';
import {decode_plot_data} from './util/decode'
import d3plot from './d3plot';
import './css/d3plot.css';

import './css/Plot.css';

import Tabs from './Tabs';

export default class Plot extends React.Component {
  constructor(props) {
    super(props);

    this.svgid = generateId();
    this.plotSaveFormats = ['PNG', 'SVG'];

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
    this.handlePlotSave = this.handlePlotSave.bind(this);
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
        d3plot(d3.select('#'+this.svgid), result);
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

  handlePlotSave() {
    let format = this.plotSaveFormats[this.state.activeFormatIndex];
    let name = `${this.props.experiment.name}_${this.props.experiment.plots[this.state.activePlotIndex]}_${moment().format('YYYY-MM-DD_hh-mm-ss')}`;
    if (format==='PNG') {
      saveSvgAsPng(document.querySelector('#'+this.svgid), name+'.png', {
        scale: 2,
        backgroundColor: 'white'
      });
    } else if (format==='SVG') {
      d3SaveSvg.save(d3.select('#'+this.svgid).node(), {
        filename: name
      });
    }
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
              tabNames={this.plotSaveFormats}
              activeIndex={this.state.activeFormatIndex}
              onTabChange={this.handleFormatChange}
            />
            <div className="button" onClick={this.handlePlotSave}>Save</div>
          </div>
        </div>
        <svg id={this.svgid} className="plot"></svg>
      </div>
    );
  };
}
