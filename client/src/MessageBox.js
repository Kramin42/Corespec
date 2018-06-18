import React from 'react';
import classNames from 'classnames';

import './css/MessageBox.css';

export default class MessageBox extends React.Component {
  render() {
    const messages = [];
    this.props.messages.forEach(m => {
      messages.push(
        <div className={classNames('message', m.type)}>{m.text}</div>
      );
    });
    return (
      <div className="message-box">
        {messages}
      </div>
    );
  };
}
