import React from 'react';

import Select from 'react-select';

import './css/Select.css'
import './css/ParameterControls.css'

export default class ParameterControls extends React.Component {
  constructor(props) {
    super(props);
    this.state = {parSet: null};
    this.handleParSetChange = this.handleParSetChange.bind(this);
  }

  handleParSetChange(value) {
    this.setState({parSet: value});
  }

  render() {
    const parSetNames = this.props.parSetNames || [];
    const parSetOptions = parSetNames.map(name => {
      return {value: name, label: name};
    });
    return (
      <div className="parameter-controls">
        <div className="parameter-controls-title">Parameter Sets</div>
        <div className="parameter-controls-container">
          <Select.Creatable
            promptTextCreator={(label) => {return `Create "${label}"`}}
            name="par-set-select"
            options={parSetOptions}
            value={this.state.parSet}
            onChange={this.handleParSetChange}
          />
          <div className="button-group">
            <div
              className="button"
              onClick={() => this.props.parSetLoad(this.state.parSet.value)}>
              Load
            </div>
            <div
              className="button"
              onClick={() => this.props.parSetSave(this.state.parSet.value)}>
              Save
            </div>
          </div>
        </div>
      </div>
    );
  };
}
