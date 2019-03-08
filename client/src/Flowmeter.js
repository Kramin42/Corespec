import React from 'react';
import WebSocketClient from '@gamestdio/websocket';
import classNames from 'classnames';
import update from 'immutability-helper';

import shortUID from './util/shortUID';

import './css/App.css';
import './css/Buttons.css';
import './css/Experiment.css';

import Tabs from './Tabs';
import Plot from './Plot';
import Parameter from './Parameter';

import './css/Flowmeter.css';

const FLOWMETER_EXPNAME = 'Flowmeter';
const FLOWMETER_PARSET_NAME = 'flowmeter';

export default class Flowmeter extends React.Component {
  constructor(props) {
    super(props);

    this.plotrefs = [];

    this.state = {
      language: {},
      experiment: null,
      outputs: {
        prop_water: '',
        prop_oil: '',
        prop_gas: '',
        flow_water: '',
        flow_oil: '',
        flow_gas: ''
      },
      parValues: {},
      messages: [],
      temperature: {count: 0, limit: 1000, times: [], values: []}
    };

    // bind 'this' as context
    this.handleConnOpen = this.handleConnOpen.bind(this);
    this.handleConnMessage = this.handleConnMessage.bind(this);
    this.command = this.command.bind(this);
    this.query = this.query.bind(this);
    this.setPar = this.setPar.bind(this);
    this.setRunning = this.setRunning.bind(this);

    this.run = this.run.bind(this);
    this.abort = this.abort.bind(this);
    this.replot = this.replot.bind(this);

    this.connPending = {}; // for storing promises to be resolved later
    this.conn = new WebSocketClient(props.server);

    this.conn.onopen = this.handleConnOpen;
    this.conn.onmessage = this.handleConnMessage;
  }

  query(name, args) {
    var ref = shortUID();
    this.conn.send(JSON.stringify({
      type: 'query',
      query: name,
      ref: ref,
      args: args || {}
    }));
    return new Promise((resolve, reject) => {
      this.connPending[ref] = {resolve, reject};
    });
  }

  command(name, args) {
    var ref = shortUID();
    this.conn.send(JSON.stringify({
      type: 'command',
      command: name,
      ref: ref,
      args: args || {}
    }));
    return new Promise((resolve, reject) => {
      this.connPending[ref] = {resolve, reject};
    });
  }

  setPar(expName, parName, value) {
    let mut = {parValues: {[expName]: {[parName]: {$set: value}}}}
    if (!this.state.parValues[expName]) {
      mut = {parValues: {[expName]: {$set: {[parName]: value}}}}
    }
    this.setState(update(this.state, mut));
  }

  setRunning(value) {
    this.setState(update(this.state, {
      experiment: {running: {$set: value}}
    }));
  }

  handleConnOpen(evt) {
    this.message('Connected');
    if (this.state.experiment == null) {
      // fetch experiment metadata
      this.query('experiment_metadata')
      .then((data) => {
        let flowmeterExp = data[data.map(d => d.name).indexOf(FLOWMETER_EXPNAME)];
        flowmeterExp.progress = {value: 0, max: 1, finished: false};
        this.setState({
          experiment: flowmeterExp
        });
      });

      this.query('load_language', {lang_name: 'english'})
      .then((data) => {
        console.log(data);
        this.setState({language: data});
      });

      this.query('default_parameters')
      .then(data => {
        this.setState(update(this.state, {parValues: {$merge: data}}));
      });

      this.query('get_tempcontrol')
      .then(data => {
        delete data.amp_on; // don't want this being passed to set_tempcontrol
        this.setState(update(this.state, {parValues: {Temperature: {$set: data}}}));
      });
    }
  }

  handleConnMessage(evt) {
    var data = JSON.parse(evt.data);
    console.log(data);
    if (data.ref && data.ref in this.connPending) {
      if (data.type === 'error') {
        this.connPending[data.ref].reject(data.message);
      } else {
        this.connPending[data.ref].resolve(data.result);
      }
      delete this.connPending[data.ref];
    }

    if (['message', 'warning', 'error'].includes(data.type)) {
      if (!data.silent) {
        this.message(data.message, data.type);
      }
    }

    if (data.type === 'progress') {
      if (this.state.experiment.name === data.experiment) {
        let new_progress = {
          value: data.progress,
          max: data.max,
          finished: data.finished
        }
        if (data.finished) {
          new_progress.value = 100;
          new_progress.max = 100;
        }
        this.setState(update(this.state, {
          experiment: {
            progress: {$set: new_progress}
          }
        }));
        this.replot();
      }
    }
  }

  message(text, type) {
    this.setState(update(this.state, {
      messages: {$push: [{text: text, type: type}]}
    }));
  }

  replot() {
    let p = this.plotrefs.map(p => {
      return p.current.replot();
    });
    p.push(this.query('export', {
      experiment_name: this.state.experiment.name,
      export_name: 'Display_Measurements'
    })
    .then(result => {
      console.log(result);
      this.setState(update(this.state, {
        outputs: {$set :{
            prop_water: result.prop_water.toFixed(2),
            prop_oil: result.prop_oil.toFixed(2),
            prop_gas: result.prop_gas.toFixed(2),
            flow_water: result.flow_water.toFixed(2),
            flow_oil: result.flow_oil.toFixed(2),
            flow_gas: result.flow_gas.toFixed(2)
        }}
      }));
    }));
    return Promise.all(p);
  }

  run() {
    return this.query('load_parameter_set', {
      experiment_name: this.state.experiment.name,
      par_set_name: FLOWMETER_PARSET_NAME
    })
    .then(data => {
      return this.command('set_parameters', {
        experiment_name: this.state.experiment.name,
        parameters: data
      });
    })
    .then(data => {
      console.log('running '+this.state.experiment.name);
      return this.command('run', {
        experiment_name: this.state.experiment.name
      });
    })
    .then(data => {
      console.log('done '+this.state.experiment.name);
      this.replot();
    })
    .catch(err => {
      console.log(err);
    });
  }

  abort() {
    return this.command('abort', {
      experiment_name: this.state.experiment.name
    })
    .catch(err => {
      console.log(err);
    });
  }

  render() {
    if (this.state.experiment == null) {
      return (
        <div className="app-container">
          Loading...
        </div>
      );
    }
    const experiment = this.state.experiment;

    const plots = [];
    let defaultPlotNames = [experiment.plots[0]];
    if (experiment.defaults && experiment.defaults.plots) {
      defaultPlotNames = experiment.defaults.plots;
    }
    defaultPlotNames.forEach((plotName, i) => {
      // if the ref doesn't exist yet then create it
      if (this.plotrefs.length<=i) {this.plotrefs.push(React.createRef());}
      plots.push(
        <Plot key={i}
          ref={this.plotrefs[i]}
          plotMethod={'query'}
          defaultPlot={plotName}
          experiment={experiment}
          deviceQuery={this.query}
          hideTabs={true}
        />
      );
    });

    const parGroupsObj = {};
    const sharedParameters = {};
    Object.keys(experiment.parameters).forEach(parName => {
      let parDef = experiment.parameters[parName];
      if (parDef.shared) {
        sharedParameters[parName] = parDef;
      } else if (parDef.group) {
        if (!parGroupsObj[parDef.group]) parGroupsObj[parDef.group] = {};
        parGroupsObj[parDef.group][parName] = parDef;
      } else {
        if (!parGroupsObj.other) parGroupsObj.other = {};
        parGroupsObj.other[parName] = parDef;
      }
    });
    const parameterGroups = Object.keys(parGroupsObj).map(k => {
      return {name: k, parameters: parGroupsObj[k]}
    });

    return (
      <div className="app-container">
        <div className={classNames('tab-content')}>
          <div className={classNames('plots-container')}>
            {plots}
          </div>
          <div className={classNames('outputs-block')}>
            <Parameter
              key={0}
              label={'Water Content'}
              name={'prop_water'}
              value={this.state.outputs.prop_water}
              def={{dtype: 'float', unit: '%'}}
              onValueChange={newValue => 0}
            />
            <Parameter
              key={1}
              label={'Water Mass'}
              name={'flow_water'}
              value={this.state.outputs.flow_water}
              def={{dtype: 'float', unit: ['m', <sup>3</sup>, '/day']}}
              onValueChange={newValue => 0}
            />
            <Parameter
              key={2}
              label={'Oil Content'}
              name={'prop_oil'}
              value={this.state.outputs.prop_oil}
              def={{dtype: 'float', unit: '%'}}
              onValueChange={newValue => 0}
            />
            <Parameter
              key={3}
              label={'Oil Mass'}
              name={'flow_oil'}
              value={this.state.outputs.flow_oil}
              def={{dtype: 'float', unit: ['m', <sup>3</sup>, '/day']}}
              onValueChange={newValue => 0}
            />
            <Parameter
              key={4}
              label={'Gas Content'}
              name={'prop_gas'}
              value={this.state.outputs.prop_gas}
              def={{dtype: 'float', unit: '%'}}
              onValueChange={newValue => 0}
            />
            <Parameter
              key={5}
              label={'Gas Mass'}
              name={'flow_gas'}
              value={this.state.outputs.flow_gas}
              def={{dtype: 'float', unit: ['m', <sup>3</sup>, '/day']}}
              onValueChange={newValue => 0}
            />
          </div>
          <div className={classNames('controls-block')}>
            <div className="run-controls">
              <div
                className={classNames(
                  'run-indicator',
                  {'running': experiment.running},
                  {'stopped': !experiment.running}
                )}
              ><span>{experiment.running ? 'Running' : 'Stopped'}</span></div>
              <div
                className={classNames(
                  'button',
                  'run',
                  {'disabled': experiment.running}
                )}
                onClick={() => {if (!experiment.running) {
                  this.setRunning(true);
                  this.run()
                  .then(data => {
                    this.setRunning(false);
                  });
                }}}
              ><span>Run</span></div>
              <div
                className="button abort"
                onClick={() => {
                  this.abort()
                  .then(data => {
                    this.setRunning(false);
                  });
                }}
              ><span>Stop</span></div>
            </div>
          </div>
        </div>
      </div>
    );
  };
}
