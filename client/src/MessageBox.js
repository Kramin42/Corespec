import React from 'react';

import './css/MessageBox.css';

export default class MessageBox extends React.Component {
  render() {
    const messages = [];
    ['test','test2','test3','test','test2','test3','test','test2','test3'].forEach(m => {
      messages.push(
        <div className="message">{m}</div>
      )
    });
    return (
      <div className="message-box">
        {messages}
      </div>
    );
  };
}
