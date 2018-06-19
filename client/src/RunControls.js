import React from 'react';
import classNames from 'classnames';

import './css/RunControls.css'

export default class RunControls extends React.Component {
  render() {
    const commandHandler = this.props.commandHandler;
    return (
      <div className="run-controls">
        <div
          className={classNames(
            'button',
            'run',
            {'disabled': !this.props.canrun}
          )}
          onClick={() => {if (this.props.canrun) commandHandler('run');}}
        >Run</div>
        <div
          className={classNames(
            'button',
            'runinf',
            {'disabled': !this.props.canrun}
          )}
          onClick={() => {if (this.props.canrun) commandHandler('runinf');}}
        >Run ∞</div>
        <div
          className="button abort"
          onClick={() => commandHandler('abort')}
        >Abort</div>
      </div>
    );
  };
}
