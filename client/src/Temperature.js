import React from 'react';
import classNames from 'classnames';

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
  }

  handleTabChange(tabIndex) {
    this.setState({
      activeParameterGroupIndex: tabIndex
    });
  }

  render() {
    const data = this.props.data;
    const active = this.props.active;

    const plots = [(<Plot />)];

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
              activeParameterGroupIndex={this.state.activeParameterGroupIndex}
              language={this.props.language}
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
