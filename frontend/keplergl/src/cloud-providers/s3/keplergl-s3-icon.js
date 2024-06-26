import React, {Component} from 'react';
import {Icons} from 'kepler.gl/components';
import PropTypes from 'prop-types';

class KeplerglS3Icon extends Component {
  static propTypes = {
    height: PropTypes.string,
    colors: PropTypes.arrayOf(PropTypes.string)
  };

  static defaultProps = {
    height: '16px',
    predefinedClassName: 'data-ex-icons-keplergl-s3',
    totalColor: 1
  };

  render() {
    return (
      <Icons.IconWrapper {...this.props} viewBox={'0 0 256 310'} colors={['#0060ff']}>
        <g>
          <path d="M20.624,53.686 L0,64 L0,245.02 L20.624,255.274 L20.748,255.125 L20.748,53.828 L20.624,53.686" fill="#8C3123"></path>
          <path d="M131,229 L20.624,255.274 L20.624,53.686 L131,79.387 L131,229" fill="#E05243"></path>
          <path d="M81.178,187.866 L127.996,193.826 L128.29,193.148 L128.553,116.378 L127.996,115.778 L81.178,121.652 L81.178,187.866" fill="#8C3123"></path>
          <path d="M127.996,229.295 L235.367,255.33 L235.536,255.061 L235.533,53.866 L235.363,53.686 L127.996,79.682 L127.996,229.295" fill="#8C3123"></path>
          <path d="M174.827,187.866 L127.996,193.826 L127.996,115.778 L174.827,121.652 L174.827,187.866" fill="#E05243"></path>
          <path d="M174.827,89.631 L127.996,98.166 L81.178,89.631 L127.937,77.375 L174.827,89.631" fill="#5E1F18"></path>
          <path d="M174.827,219.801 L127.996,211.21 L81.178,219.801 L127.939,232.854 L174.827,219.801" fill="#F2B0A9"></path>
          <path d="M81.178,89.631 L127.996,78.045 L128.375,77.928 L128.375,0.313 L127.996,0 L81.178,23.413 L81.178,89.631" fill="#8C3123"></path>
          <path d="M174.827,89.631 L127.996,78.045 L127.996,0 L174.827,23.413 L174.827,89.631" fill="#E05243"></path>
          <path d="M127.996,309.428 L81.173,286.023 L81.173,219.806 L127.996,231.388 L128.685,232.171 L128.498,308.077 L127.996,309.428" fill="#8C3123"></path>
          <path d="M127.996,309.428 L174.823,286.023 L174.823,219.806 L127.996,231.388 L127.996,309.428" fill="#E05243"></path>
          <path d="M235.367,53.686 L256,64 L256,245.02 L235.367,255.33 L235.367,53.686" fill="#E05243"></path>
        </g>
      </Icons.IconWrapper>
    );
  }
}

export default KeplerglS3Icon;

