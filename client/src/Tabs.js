import React from 'react';
import classNames from 'classnames';

import './css/Tabs.css';

export default class Tabs extends React.Component {
  constructor(props) {
    super(props);

    this.handleTabChange = this.handleTabChange.bind(this);
  }

  handleTabChange(tabIndex) {
    this.props.onTabChange(tabIndex);
  }

  render() {
    const tabNames = this.props.tabNames.map(n => n.replace(/_/g, ' ').trim());
    const activeIndex = this.props.activeIndex;
    const buttons = [];
    tabNames.forEach((name, i) => {
      buttons.push(
        <div
          key={i}
          className={classNames('tab-link', {'active': activeIndex===i})}
          onClick={() => this.handleTabChange(i)}
        >
          {name}
        </div>
      );
    });
    return (
      <div className="tab-bar">{buttons}</div>
    );
  };
}
