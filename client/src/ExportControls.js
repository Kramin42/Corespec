import React from 'react';
import moment from 'moment';

import Select from 'react-select';

import './css/ExportControls.css'

export default class ExportControls extends React.Component {
  constructor(props) {
    super(props);
    this.state = {format: null};
    this.handleFormatChange = this.handleFormatChange.bind(this);
    this.handleExport = this.handleExport.bind(this);
  }

  handleFormatChange(value) {
    this.setState({format: value});
  }

  handleExport() {
    if (this.state.format.value==='CSV') {
      this.props.deviceQuery('export_csv', {
        experiment_name: this.props.experimentName,
        export_name: 'Raw'
      })
      .then(data => {
        downloadString(data, 'text/csv', `${this.props.experimentName}_${moment().format('YYYY-MM-DD_hh-mm-ss')}.csv`);
      });
    }
    else if (this.state.format.value==='MATLAB') {
      this.props.deviceQuery('export_matlab', {
        experiment_name: this.props.experimentName,
        export_name: 'default'
      })
      .then(data => {
        let bytes = Uint8Array.from(atob(data), c => c.charCodeAt(0));
    		downloadBytes(bytes, `${this.props.experimentName}_${moment().format('YYYY-MM-DD_hh-mm-ss')}.mat`);
      });
    }
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
        <div className="button" onClick={this.handleExport}>Export</div>
      </div>
    );
  };
}

function downloadString(text, fileType, fileName) {
  	var blob = new Blob([text], { type: fileType });

  	var a = document.createElement('a');
  	a.download = fileName;
  	a.href = URL.createObjectURL(blob);
  	a.dataset.downloadurl = [fileType, a.download, a.href].join(':');
  	a.style.display = "none";
  	document.body.appendChild(a);
	a.click();
  	document.body.removeChild(a);
  	setTimeout(function() { URL.revokeObjectURL(a.href); }, 1500);
}

function downloadBytes(bytes, fileName) {
    var blob = new Blob([bytes]);
    var link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileName;
    link.click();
}
