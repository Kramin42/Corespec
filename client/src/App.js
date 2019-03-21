import React from 'react';
import WebSocketClient from '@gamestdio/websocket';
import update from 'immutability-helper';

import shortUID from './util/shortUID';

import './css/App.css';
import './css/Buttons.css';

import Tabs from './Tabs';
import TabPanes from './TabPanes';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      language: {},
      experiments: [],
      parValues: {},
      runningExperiment: false,
      runningExperimentIndex: 0,
      activeTabIndex: 0,
      messages: [],
      temperature: {count: 0, limit: 1000, times: [], values: []}
    };

    // bind 'this' as context
    this.handleTabChange = this.handleTabChange.bind(this);
    this.handleConnOpen = this.handleConnOpen.bind(this);
    this.handleConnMessage = this.handleConnMessage.bind(this);
    this.command = this.command.bind(this);
    this.query = this.query.bind(this);
    this.setPar = this.setPar.bind(this);
    this.setRunning = this.setRunning.bind(this);

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

  setRunning(index, value) {
    this.setState(update(this.state, {
      runningExperiment: {$set: value},
      runningExperimentIndex: {$set: index}
    }));
  }

  handleConnOpen(evt) {
    this.message('Connected');
    if (this.state.experiments.length==0) {
      // fetch experiment metadata
      this.query('experiment_metadata')
      .then((data) => {
        this.setState({
          experiments: data.map(d => {
            d.progress = {value: 0, max: 1, finished: false};
            return d;
          })
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
      let index = this.state.experiments.length-1;
      for (;index>=0; index--) {
        if (this.state.experiments[index].name === data.experiment) break;
      }
      console.log(index);
      if (index>=0) {
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
          experiments: {[index]: {
            progress: {$set: new_progress}
          }}
        }));
      }
    }

    if (data.type=='tempcontrol') {
  	  if (data.data.name=='temperature') {
        let newTemp = this.state.temperature;
  	    newTemp.values.push(data.data.value);
        newTemp.times.push(data.data.time);
        if (newTemp.values.length > newTemp.limit) {newTemp.values.unshift();}
        if (newTemp.times.length > newTemp.limit) {newTemp.times.unshift();}
        newTemp.count++;
        this.setState(update(this.state, {
          temperature: {$set: newTemp}
        }));
  	  } else if (data.data.name=='error') {
        this.message(`${data.data.value}`, 'error');
      } else {
  	    if (data.data.name === 'amp-power') {
          this.message('Amplifier powered');
  	    } else {
          this.message(`temp control ${data.data.name} set to ${data.data.value}`);
  	    }
  	  }
  	}
  }

  handleTabChange(tabIndex) {
    this.setState({activeTabIndex: tabIndex});
  }

  message(text, type) {
    this.setState(update(this.state, {
      messages: {$push: [{text: text, type: type}]}
    }));
  }

  render() {
    const fixedTabs = [
      {
        'name': 'Temperature',
        'parameters': {
          setpoint: {
            unit: '\u00b0C',
            group: 'basic'
          },
          P: {group: 'advanced'},
          I: {group: 'advanced'}
        },
        'defaults': {'order': 0}
      }
    ];

    const allTabs = fixedTabs.concat(this.state.experiments).map((exp, i) => {
      exp.canrun = !this.state.runningExperiment;
      exp.running = this.state.runningExperimentIndex == i;
      if (exp.defaults!==undefined && exp.defaults.order!==undefined) {
        exp.order = exp.defaults.order;
      } else {
        exp.order = 1000;
      }
      return exp;
    }).sort((a, b) => a.order>b.order ? 1 : (a.order<b.order ? -1 : 0));

    return (
      <div className="app-container">
        <Tabs
          tabNames={allTabs.map(e => e.name)}
          activeIndex={this.state.activeTabIndex}
          onTabChange={this.handleTabChange}
        />
        <TabPanes
          data={allTabs}
          temperature={this.state.temperature}
          parValues={this.state.parValues}
          setPar={this.setPar}
          setRunning={this.setRunning}
          deviceCommand={this.command}
          deviceQuery={this.query}
          activeIndex={this.state.activeTabIndex}
          messages={this.state.messages}
          language={this.state.language}
        />
      </div>
    );
  };
}
