import React from 'react';
import classNames from 'classnames';

import './css/MessageBox.css';

export default class MessageBox extends React.Component {
  componentDidUpdate() {
    this.messagesEnd.scrollIntoView({ behavior: "smooth" });
  }

  render() {
    const messages = [];
    this.props.messages.forEach((m, i) => {
      messages.push(
        <div key={i} className={classNames('message', m.type)}>{m.text}</div>
      );
    });
    return (
      <div className="message-box">
        {messages}
        <div
          style={{float: 'left', clear: 'both'}}
          ref={el => {this.messagesEnd = el;}}
        >
        </div>
      </div>
    );
  };
}
