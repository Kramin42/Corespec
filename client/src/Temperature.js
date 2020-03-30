import React from 'react';
import classNames from 'classnames';
import update from 'immutability-helper';

import './css/Experiment.css';

import Plot from './Plot';
import Tabs from './Tabs';
import ParameterPanes from './ParameterPanes';
import ParameterBox from './ParameterBox';
import MessageBox from './MessageBox';

export default class Temperature extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      activeParameterGroupIndex: 0
    };

    this.handleTabChange = this.handleTabChange.bind(this);
    this.setOwnPar = this.setOwnPar.bind(this);
    this.setTempControl = this.setTempControl.bind(this);
  }

  handleTabChange(tabIndex) {
    this.setState({
      activeParameterGroupIndex: tabIndex
    });
  }

  setOwnPar(name, value) {
    this.props.setPar(this.props.data.name, name, value);
  }

  setTempControl() {
    return this.props.deviceCommand(
      'set_tempcontrol',
      this.props.parValues[this.props.data.name]
    );
  }

  render() {
    const data = this.props.data;
    const active = this.props.active;

    const plots = [
      (<Plot
        key={0}
        ref={this.plotref}
        visible={active}
        plotMethod={'direct'}
        plot={{
          id: this.props.temperature.count + (active ? 10 : 0),
          data: [{
            name: '',
            type: 'scatter',
            x: this.props.temperature.times,
            y: this.props.temperature.values}],
          layout: {
            title: 'Temperature',
            xaxis: {title: 'time (s)'},
            yaxis: {title: 'Temperature (\u00b0C)'}
          }
        }}
      />)
    ];

    const parGroupsObj = {};
    const sharedParameters = {};
    Object.keys(data.parameters).forEach(parName => {
      let parDef = data.parameters[parName];
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
        <div className={classNames('parameters-controls-row')}>
          <div className={classNames('parameters-block')}>
            <div className={classNames('own-parameters-parcontrols-row')}>
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
                  parameterValues={this.props.parValues[data.name] || {}}
                  activeParameterGroupIndex={this.state.activeParameterGroupIndex}
                  language={this.props.language}
                  onValueChange={this.setOwnPar}
                />
              </div>
            </div>
          </div>
          <div className={classNames('controls-block')}>
            <div className="run-controls">
              <div className="button set" onClick={this.setTempControl}>Set Parameters</div>
            </div>
            <MessageBox messages={this.props.messages}/>
          </div>
        </div>
      </div>
    );
  };
}
