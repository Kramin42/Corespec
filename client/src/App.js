import React from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';
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
      activeTabIndex: 0,
      messages: [
        {text: 'test', type: 'default'},
        {text: 'test2', type: 'warning'},
        {text: 'test3', type: 'error'}
      ]
    };

    // bind 'this' as context
    this.handleTabChange = this.handleTabChange.bind(this);
    this.handleConnOpen = this.handleConnOpen.bind(this);
    this.handleConnMessage = this.handleConnMessage.bind(this);
    this.refreshParSetList = this.refreshParSetList.bind(this);

    this.connPending = {}; // for storing promises to be resolved later
    this.conn = new ReconnectingWebSocket(props.server);

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
      this.connPending[ref] = resolve;
    });
  }

  handleConnOpen(evt) {
    this.message('Connected');
    if (this.state.experiments.length==0) {
      // fetch experiment metadata
      this.query('experiment_metadata')
      .then((data) => {
        this.setState({experiments: data});
        data.forEach(exp => this.refreshParSetList(exp.name))
      });

      this.query('load_language', {lang_name: 'english'})
      .then((data) => {
        console.log(data);
        this.setState({language: data});
      });
    }
  }

  handleConnMessage(evt) {
    var data = JSON.parse(evt.data);
    if (data.ref in this.connPending) {
      this.connPending[data.ref](data.result);
      delete this.connPending[data.ref];
    }

    if (['message', 'warning', 'error'].includes(data.type)) {
      message(data.message, data.type);
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

  refreshParSetList(expName) {
    this.query('list_parameter_sets', {experiment_name: expName})
    .then((data) => {
      let expIndex = this.state.experiments.findIndex(exp => exp.name==expName);
      this.setState(update(this.state, {
        experiments: {[expIndex]: {$merge: {parSetNames: data}}}
      }));
    });
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
        }
      }
    ];

    const allTabs = fixedTabs.concat(this.state.experiments);

    return (
      <div className="app-container">
        <Tabs
          tabNames={allTabs.map(e => e.name)}
          activeIndex={this.state.activeTabIndex}
          onTabChange={this.handleTabChange}
        />
        <TabPanes
          data={allTabs}
          activeIndex={this.state.activeTabIndex}
          messages={this.state.messages}
          language={this.state.language}
        />
      </div>
    );
  };
}
