import React from 'react';
import classNames from 'classnames';

import Parameter from './Parameter';

export default class ParameterBox extends React.Component {
  render() {
    const parDefs = this.props.parameters;
    const active = this.props.active;
    const parameters = [];
    Object.keys(parDefs).forEach(parName => {
      let parDef = parDefs[parName];
      parameters.push(
        <Parameter name={parName} def={parDef}/>
      );
    });
    return (
      <div
        className={classNames('parameters-container')}
        style={active ? {} : {display: 'none'}}
      >
        {parameters}
      </div>
    );
  };
}
