import React from 'react';

import './css/Parameter.css';

import generateId from './util/generateId';

export default class Parameter extends React.Component {
  constructor(props) {
    super(props);
    this.id = generateId();

    this.handeValueChange = this.handeValueChange.bind(this);
  }

  handeValueChange(e) {
    this.props.onValueChange(e.target.value);
  }

  render() {
    const name = this.props.name;
    const value = this.props.value;
    const label = this.props.label || name;
    const unit = this.props.def.unit || '';
    return (
      <div className="parameter">
        <label htmlFor={this.id}>
          <span className="par-name">{label}</span>
        </label>
        <input
          id={this.id}
          className="par-input"
          name={name}
          value={value}
          onChange={this.handeValueChange}/>
        <span className="par-unit">{unit}</span>
      </div>
    );
  };
}
