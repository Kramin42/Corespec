import React from 'react';

import Select from 'react-select';

import './css/ExportControls.css'

export default class ExportControls extends React.Component {
  constructor(props) {
    super(props);
    this.state = {format: null};
    this.handleFormatChange = this.handleFormatChange.bind(this);
  }

  handleFormatChange(value) {
    this.setState({format: value});
  }

  render() {
    const formatList = ['CSV', 'MATLAB'];
    const formatOptions = formatList.map(name => {
      return {value: name, label: name};
    });
    return (
      <div className="export-controls">
        <Select
          name="format-select"
          options={formatOptions}
          searchable={false}
          clearable={false}
          placeholder="Format..."
          value={this.state.format}
          onChange={this.handleFormatChange}
        />
        <div className="button">Export</div>
      </div>
    );
  };
}
