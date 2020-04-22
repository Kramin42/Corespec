import React from 'react';
import classNames from 'classnames';
import update from 'immutability-helper';

import './css/Experiment.css';

import Plot from './Plot';
import Tabs from './Tabs';
import ParameterPanes from './ParameterPanes';
import ParameterBox from './ParameterBox';
import RunControls from './RunControls';
import ExportControls from './ExportControls';
import Progress from './Progress';
import ParameterControls from './ParameterControls';
import MessageBox from './MessageBox';

export default class Experiment extends React.Component {
  constructor(props) {
    super(props);

    this.plotrefs = [];
    this.replotting = false;
    this.plots_initialised = false;

    this.state = {
      activeParameterGroupIndex: 0,
      parSetNames: []
    };

    this.handleTabChange = this.handleTabChange.bind(this);
    this.setOwnPar = this.setOwnPar.bind(this);
    this.setSharedPar = this.setSharedPar.bind(this);
    this.handleCommand = this.handleCommand.bind(this);
    this.run = this.run.bind(this);
    this.abort = this.abort.bind(this);
    this.replot = this.replot.bind(this);
    this.parSetLoad = this.parSetLoad.bind(this);
    this.parSetSave = this.parSetSave.bind(this);
    this.refreshParSetList = this.refreshParSetList.bind(this);
  }

  handleTabChange(tabIndex) {
    this.setState({
      activeParameterGroupIndex: tabIndex
    });
  }

  setOwnPar(name, value) {
    this.props.setPar(this.props.experiment.name, name, value);
  }

  setSharedPar(name, value) {
    this.props.setPar('shared', name, value);
  }

  refreshParSetList() {
    return this.props.deviceQuery('list_parameter_sets', {
      experiment_name: this.props.experiment.name
    })
    .then((data) => {
      this.setState(update(this.state, {
        parSetNames: {$set: data}
      }));
    });
  }

  parSetLoad(name) {
    return this.props.deviceQuery('load_parameter_set', {
      experiment_name: this.props.experiment.name,
      par_set_name: name
    })
    .then(data => {
      Object.keys(data).forEach(parName => {
        let parDef = this.props.experiment.parameters[parName];
        if (parDef) {
          if (parDef.shared) {
            this.setSharedPar(parName, data[parName]);
          } else {
            this.setOwnPar(parName, data[parName]);
          }
        }
      });
    });
  }

  parSetSave(name) {
    let pars = Object.assign({},
      this.props.parValues[this.props.experiment.name],
      this.props.parValues['shared']
    );
    return this.props.deviceCommand('save_parameter_set', {
      experiment_name: this.props.experiment.name,
      par_set_name: name,
      parameters: pars
    }).then(this.refreshParSetList);
  }

  run() {
    return this.props.deviceCommand('set_parameters', {
      experiment_name: this.props.experiment.name,
      parameters: Object.assign({},
        this.props.parValues[this.props.experiment.name],
        this.props.parValues['shared'])
    })
    .then(data => {
      console.log('running '+this.props.experiment.name);
      return this.props.deviceCommand('run', {
        experiment_name: this.props.experiment.name
      });
    })
    .then(data => {
      console.log('done '+this.props.experiment.name);
      this.replot();
    })
    .catch(err => {
      console.log(err);
    });
  }

  abort() {
    return this.props.deviceCommand('abort', {
      experiment_name: this.props.experiment.name
    })
    .catch(err => {
      console.log(err);
    });
  }

  handleCommand(command) {
    if (command==='run') {
      this.props.setRunning(true);
      this.run()
      .then(data => {
        this.props.setRunning(false);
      });
    } else if (command==='runinf') {
      this.props.setRunning(true);
      this.runinf = true;
      let runinf = () => {
        if (this.runinf) {
          return this.run().then(runinf);
        } else {
          return Promise.resolve();
        }
      }
      runinf()
      .then(data => {
        this.props.setRunning(false);
      });
    } else if (command==='abort') {
      this.runinf = false;
      this.abort()
      .then(data => {
        this.props.setRunning(false);
      });
    }
  }

  replot() {
    this.replotting = true;
    return Promise.all(this.plotrefs.map(p => {
      return p.current.replot();
    })).then(() => {
      this.replotting = false;
    });
  }

  componentDidMount() {
    this.refreshParSetList();
  }

  componentDidUpdate(prevProps) {
    if (!this.plots_initialised && this.props.active) {
      this.plots_initialised = true;
      this.replotting = true;
      this.replot().then(() => {
        this.replotting = false;
      });
    }

    if (this.props.experiment.progress.value != prevProps.experiment.progress.value) {
      if (this.props.experiment.canrun && !this.props.experiment.progress.finished) {
        this.props.setRunning(true);
      }
      else if (!this.props.experiment.canrun && this.props.experiment.progress.finished) {
        this.props.setRunning(false);
      }
    }

    if (this.props.experiment.progress.value > prevProps.experiment.progress.value) {
      if  (!this.replotting || this.props.experiment.progress.finished) {
        this.replotting = true;
        this.replot().then(() => {
          this.replotting = false;
        });
      }
    }
  }

  render() {
    const experiment = this.props.experiment;
    const active = this.props.active;

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
          visible={active}
          plotMethod={'query'}
          defaultPlot={plotName}
          experiment={experiment}
          deviceQuery={this.props.deviceQuery}
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
      <div className={classNames('tab-content')} style={active ? {} : {display: 'none'}}>
        <div className={classNames('plots-container')}>
          {plots}
        </div>
        <div className={classNames('parameters-controls-row')}>
          <div className={classNames('parameters-block')}>
            <div className={classNames('own-parameters-parcontrols-row')}>
              <div className={classNames('own-parameters')}>
                <div className="title-tab-bar">
                  <div className="par-box-title">Parameters</div>
                  <Tabs
                    tabNames={parameterGroups.map(g => g.name)}
                    activeIndex={this.state.activeParameterGroupIndex}
                    onTabChange={this.handleTabChange}
                  />
                </div>
                <ParameterPanes
                  parameterGroups={parameterGroups}
                  parameterValues={this.props.parValues[experiment.name] || {}}
                  activeParameterGroupIndex={this.state.activeParameterGroupIndex}
                  language={this.props.language}
                  onValueChange={this.setOwnPar}
                />
              </div>
              <ParameterControls
                parSetNames={this.state.parSetNames}
                parSetLoad={this.parSetLoad}
                parSetSave={this.parSetSave}
              />
            </div>
            <div className={classNames('shared-parameters')}>
              <div className="par-box-title">Shared</div>
              <ParameterBox
                parameters={sharedParameters}
                parameterValues={this.props.parValues['shared'] || {}}
                active={true}
                language={this.props.language}
                onValueChange={this.setSharedPar}
              />
            </div>
          </div>
          <div className={classNames('controls-block')}>
            <RunControls
              running={experiment.running}
              canrun={experiment.canrun}
              commandHandler={this.handleCommand}
            />
            <Progress
              progress={experiment.progress.value}
              progressMax={experiment.progress.max}
            />
            <ExportControls
              experimentName={experiment.name}
              deviceQuery={this.props.deviceQuery}
              exports={experiment.exports}
            />
            <MessageBox messages={this.props.messages} />
          </div>
        </div>
      </div>
    );
  };
}
