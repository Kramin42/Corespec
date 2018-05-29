import React from 'react';

import Select from 'react-select';

import './css/Select.css'
import './css/ParameterControls.css'

export default class ParameterControls extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: null};
    this.handleParSetChange = this.handleParSetChange.bind(this);
  }

  handleParSetChange(value) {
    this.setState({value: value});
  }

  render() {
    const parSetList = ['1','2','3','4','5','6','7','8','9','10'];
    const parSetOptions = parSetList.map(name => {
      return {value: name, label: name};
    });
    return (
      <div className="parameter-controls">
        <div className="parameter-controls-title">Parameter Sets</div>
        <div className="parameter-controls-container">
          <Select.Creatable
            name="par-set-select"
            options={parSetOptions}
            value={this.state.value}
            onChange={this.handleParSetChange}
          />
          <div className="button-group">
            <div className="button">Load</div>
            <div className="button">Save</div>
          </div>
        </div>
      </div>
    );
  };
}
