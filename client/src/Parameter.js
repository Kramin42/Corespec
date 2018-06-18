import React from 'react';

import './css/Parameter.css';

import generateId from './util/generateId';

export default class Parameter extends React.Component {
  constructor(props) {
    super(props);
    this.id = generateId();
  }

  render() {
    const name = this.props.name;
    const label = this.props.label || name;
    const unit = this.props.def.unit || '';
    return (
      <div className="parameter">
        <label htmlFor={this.id}>
          <span className="par-name">{label}</span>
        </label>
        <input id={this.id} className="par-input" name={name} />
        <span className="par-unit">{unit}</span>
      </div>
    );
  };
}
