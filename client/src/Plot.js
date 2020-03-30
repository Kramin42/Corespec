import React from 'react';
import * as d3 from 'd3';

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
    this.plotId = 0;
    this.dirtyRender = false;

    let activePlotIndex = undefined;
    if (props.experiment && props.experiment.plots && this.props.defaultPlot) {
      activePlotIndex = props.experiment.plots.indexOf(this.props.defaultPlot);
    }

    this.state = {
      activePlotIndex: activePlotIndex,
      activeFormatIndex: 0,
      plot: {id: -1}
    }

    this.handlePlotChange = this.handlePlotChange.bind(this);
    this.handleFormatChange = this.handleFormatChange.bind(this);
    this.replot = this.replot.bind(this);
  }

  replot(plotIndex) {
    if (plotIndex===null || plotIndex===undefined) {
      plotIndex = this.state.activePlotIndex;
    }
    console.log(`refetching plot: ${plotIndex}`);
    if (this.props.plotMethod==='query') {
      return this.props.deviceQuery('plot', {
        experiment_name: this.props.experiment.name,
        plot_name: this.props.experiment.plots[plotIndex]
      })
      .then(result => {
        result.data = decode_plot_data(result.data)
        result.id = this.plotId++;
        this.setState({
          plot: result
        });
        //result.data = decode_plot_data(result.data);
        //d3plot(d3.select('#'+this.svgid), result);
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

  componentDidUpdate(prevProps, prevState) {
    //console.log('Plot componentDidUpdate', prevProps, this.props, prevState, this.state);
    if (this.props.plotMethod === 'direct') {
      if (this.props.plot.id !== prevProps.plot.id) {
        this.dirtyRender = true;
      }
    }
    if (this.props.plotMethod === 'query') {
      if (this.state.plot.id !== prevState.plot.id && this.state.plot.id !==-1) {
        this.dirtyRender = true;
      }
    }

    if (this.props.visible && this.dirtyRender) {
      if (this.props.plotMethod === 'direct') {
        //console.log('rerendering plot: temperature, plot id:', this.props.plot.id);
        var svg = document.getElementById(this.svgid);
        d3plot(d3.select(svg), this.props.plot, svg.clientWidth, svg.clientHeight);
      }
      if (this.props.plotMethod === 'query') {
        //console.log('rerendering plot:', this.props.experiment.name, this.props.experiment.plots[this.state.activePlotIndex], 'plot id:', this.state.plot.id);
        var svg = document.getElementById(this.svgid);
        d3plot(d3.select(svg), this.state.plot, svg.clientWidth, svg.clientHeight);
      }
      this.dirtyRender = false;
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
            hidden={this.props.hideTabs}
          />
          {!this.props.hideTabs &&
            <div className="plot-export-controls">
              <Tabs
                tabNames={formats}
                activeIndex={this.state.activeFormatIndex}
                onTabChange={this.handleFormatChange}
              />
              <div className="button">Save</div>
            </div>
          }
        </div>
        <svg id={this.svgid} className="plot"></svg>
      </div>
    );
  };
}
