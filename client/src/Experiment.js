import React from 'react';
import classNames from 'classnames';
import update from 'immutability-helper';

import './css/Experiment.css';

import Plot from './Plot';
import Tabs from './Tabs';
import ParameterPanes from './ParameterPanes';
import ParameterBox from './ParameterBox';
import RunControls from './RunControls';
import ExportControls from './ExportControls';
import Progress from './Progress';
import ParameterControls from './ParameterControls';
import MessageBox from './MessageBox';

export default class Experiment extends React.Component {
  constructor(props) {
    super(props);

    this.plotrefs = [];

    this.state = {
      parameters: {},
      activeParameterGroupIndex: 0,
    };

    this.handleTabChange = this.handleTabChange.bind(this);
    this.setParameter = this.setParameter.bind(this);
    this.handleCommand = this.handleCommand.bind(this);
    this.run = this.run.bind(this);
    this.abort = this.abort.bind(this);
  }

  handleTabChange(tabIndex) {
    this.setState({
      activeParameterGroupIndex: tabIndex
    });
  }

  setParameter(name, value) {
    this.setState(update(this.state, {
      parameters: {[name]: {$set: value}}
    }));
  }

  run() {
    return this.props.deviceCommand('set_parameters', {
      experiment_name: this.props.experiment.name,
      parameters: Object.assign({}, this.state.parameters, this.props.sharedParValues)
    })
    .then(data => {
      console.log('running '+this.props.experiment.name);
      return this.props.deviceCommand('run', {
        experiment_name: this.props.experiment.name
      });
    })
    .then(data => {
      console.log('done '+this.props.experiment.name);
      this.plotrefs.forEach(p => {
        p.current.replot();
      });
    })
    .catch(err => {
      console.log(err);
    });
  }

  abort() {
    return this.props.deviceCommand('abort', {
      experiment_name: this.props.experiment.name
    })
    .catch(err => {
      console.log(err);
    });
  }

  handleCommand(command) {
    if (command==='run') {
      this.props.setRunning(true);
      this.run()
      .then(data => {
        this.props.setRunning(false);
      });
    } else if (command==='runinf') {

    } else if (command==='abort') {
      this.abort()
      .then(data => {
        this.props.setRunning(false);
      });
    }
  }

  render() {
    const experiment = this.props.experiment;
    const active = this.props.active;

    const plots = [];
    let defaultPlotNames = [experiment.plots[0]];
    if (experiment.defaults && experiment.defaults.plots) {
      defaultPlotNames = experiment.defaults.plots;
    }
    defaultPlotNames.forEach((plotName, i) => {
      // if the ref doesn't exist yet then create it
      if (this.plotrefs.length<=i) {this.plotrefs.push(React.createRef());}
      plots.push(
        <Plot key={i}
          ref={this.plotrefs[i]}
          defaultPlot={plotName}
          experiment={experiment}
          deviceQuery={this.props.deviceQuery}
        />
      );
    });

    const parGroupsObj = {};
    const sharedParameters = {};
    Object.keys(experiment.parameters).forEach(parName => {
      let parDef = experiment.parameters[parName];
      if (parDef.shared) {
        sharedParameters[parName] = parDef;
      } else if (parDef.group) {
        if (!parGroupsObj[parDef.group]) parGroupsObj[parDef.group] = {};
        parGroupsObj[parDef.group][parName] = parDef;
      } else {
        if (!parGroupsObj.other) parGroupsObj.other = {};
        parGroupsObj.other[parName] = parDef;
      }
    });
    const parameterGroups = Object.keys(parGroupsObj).map(k => {
      return {name: k, parameters: parGroupsObj[k]}
    });

    return (
      <div className={classNames('tab-content')} style={active ? {} : {display: 'none'}}>
        <div className={classNames('plots-container')}>
          {plots}
        </div>
        <div className={classNames('parameters-block')}>
          <div className={classNames('own-parameters')}>
            <div className="title-tab-bar">
              <div className="par-box-title">Parameters</div>
              <Tabs
                tabNames={parameterGroups.map(g => g.name)}
                activeIndex={this.state.activeParameterGroupIndex}
                onTabChange={this.handleTabChange}
              />
            </div>
            <ParameterPanes
              parameterGroups={parameterGroups}
              parameterValues={this.state.parameters}
              activeParameterGroupIndex={this.state.activeParameterGroupIndex}
              language={this.props.language}
              onValueChange={this.setParameter}
            />
          </div>
          <ParameterControls parSetNames={experiment.parSetNames} />
          <div className={classNames('shared-parameters')}>
            <div className="par-box-title">Shared</div>
            <ParameterBox
              parameters={sharedParameters}
              parameterValues={this.props.sharedParValues}
              active={true}
              language={this.props.language}
              onValueChange={this.props.setSharedPar}
            />
          </div>
        </div>
        <div className={classNames('controls-block')}>
          <RunControls
            running={experiment.running}
            canrun={experiment.canrun}
            commandHandler={this.handleCommand}
          />
          <Progress
            progress={experiment.progress.value}
            progressMax={experiment.progress.max}
          />
          <ExportControls />
          <MessageBox messages={this.props.messages} />
        </div>
      </div>
    );
  };
}
