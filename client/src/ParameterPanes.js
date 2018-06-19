import React from 'react';

import ParameterBox from './ParameterBox';

export default class ParameterPanes extends React.Component {
  render() {
    const groups = this.props.parameterGroups;
    const activeIndex = this.props.activeParameterGroupIndex;
    let parPanes = [];
    groups.forEach((group, i) => {
      parPanes.push(
        <ParameterBox
          key={i}
          parameters={group.parameters}
          parameterValues={this.props.parameterValues}
          active={activeIndex===i}
          language={this.props.language}
          onValueChange={this.props.onValueChange}
        />
      );
    });
    return (
      <div className="tab-panes">{parPanes}</div>
    );
  };
}
