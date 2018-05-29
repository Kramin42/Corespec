import React from 'react';

import ParameterBox from './ParameterBox';

export default class ParameterPanes extends React.Component {
  render() {
    const groups = this.props.parameterGroups;
    const activeIndex = this.props.activeParameterGroupIndex;
    let parPanes = [];
    groups.forEach((group, i) => {
      parPanes.push(
        <ParameterBox parameters={group.parameters} active={activeIndex===i} />
      );
    });
    return (
      <div className="tab-panes">{parPanes}</div>
    );
  };
}
