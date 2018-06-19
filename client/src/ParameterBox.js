import React from 'react';
import classNames from 'classnames';

import Parameter from './Parameter';

export default class ParameterBox extends React.Component {
  render() {
    const parDefs = this.props.parameters;
    const active = this.props.active;
    const parlang = this.props.language['parameters'] || {}
    const parValues = this.props.parameterValues;
    const parameters = [];
    Object.keys(parDefs).forEach((parName, i) => {
      let parDef = parDefs[parName];
      let lang = parlang[parName] || {'label': parName};
      let value = parValues[parName] || '';
      parameters.push(
        <Parameter
          key={i}
          label={lang['label']}
          name={parName}
          value={value}
          def={parDef}
          onValueChange={newValue => this.props.onValueChange(parName, newValue)}
        />
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
