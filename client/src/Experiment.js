import React from 'react';
import classNames from 'classnames';

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

    this.state = {
      activeParameterGroupIndex: 0
    };

    this.handleTabChange = this.handleTabChange.bind(this);
  }

  handleTabChange(tabIndex) {
    this.setState({
      activeParameterGroupIndex: tabIndex
    });
  }

  render() {
    const experiment = this.props.experiment;
    const active = this.props.active;

    const plots = [];
    let defaultPlotNames = [experiment.plots[0]];
    if (experiment.defaults && experiment.defaults.plots) {
      defaultPlotNames = experiment.defaults.plots;
    }
    defaultPlotNames.forEach(plotName => {
      plots.push(
        <Plot />
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
              activeParameterGroupIndex={this.state.activeParameterGroupIndex}
            />
          </div>
          <ParameterControls />
          <div className={classNames('shared-parameters')}>
            <div className="par-box-title">Shared</div>
            <ParameterBox parameters={sharedParameters} active={true}/>
          </div>
        </div>
        <div className={classNames('controls-block')}>
          <RunControls />
          <Progress />
          <ExportControls />
          <MessageBox />
        </div>
      </div>
    );
  };
}
