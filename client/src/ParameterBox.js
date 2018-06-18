import React from 'react';
import classNames from 'classnames';

import Parameter from './Parameter';

export default class ParameterBox extends React.Component {
  render() {
    const parDefs = this.props.parameters;
    const active = this.props.active;
    const parlang = this.props.language['parameters'] || {}
    const parameters = [];
    Object.keys(parDefs).forEach(parName => {
      let parDef = parDefs[parName];
      let lang = parlang[parName] || {'label': parName};
      parameters.push(
        <Parameter
          label={lang['label']}
          name={parName}
          def={parDef}
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
