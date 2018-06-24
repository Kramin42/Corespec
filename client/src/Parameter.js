import React from 'react';
import classNames from 'classnames';

import './css/Parameter.css';

import generateId from './util/generateId';

export default class Parameter extends React.Component {
  constructor(props) {
    super(props);
    this.id = generateId();

    this.handeValueChange = this.handeValueChange.bind(this);
  }

  handeValueChange(e) {
    // let value = e.target.value
    // if (this.props.def.dtype) {
    //   if (this.props.def.dtype.search('int')>-1) {
    //     value = parseInt(value);
    //   } else if (this.props.def.dtype.search('float')>-1) {
    //     value = parseFloat(value);
    //   }
    // }
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
          className={classNames('par-input', this.props.def.dtype)}
          name={name}
          value={value}
          onChange={this.handeValueChange}/>
        <span className="par-unit">{unit}</span>
      </div>
    );
  };
}
