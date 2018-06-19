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
      parameters: {},
      activeParameterGroupIndex: 0
    };

    this.handleTabChange = this.handleTabChange.bind(this);
    this.setParameter = this.setParameter.bind(this);
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

  render() {
    const data = this.props.data;
    const active = this.props.active;

    const plots = [(<Plot key={0} />)];

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
        </div>
        <div className={classNames('controls-block')}>
          <div className="run-controls">
            <div className="button set">Set Parameters</div>
          </div>
          <MessageBox messages={this.props.messages}/>
        </div>
      </div>
    );
  };
}
