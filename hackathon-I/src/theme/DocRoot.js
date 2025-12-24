import React, { useEffect } from 'react';
import Layout from '@theme/Layout';
import ChatWidget from '../components/ChatWidget/ChatWidget';
import '../components/ChatWidget/ChatWidget.css';

// Custom DocRoot to include the chat widget
function DocRoot(props) {
  const { route, versionMetadata, doc } = props;

  return (
    <Layout {...props}>
      <div style={{ display: 'flex', flexDirection: 'row', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          {props.children}
        </div>
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 1000
        }}>
          <ChatWidget />
        </div>
      </div>
    </Layout>
  );
}

export default DocRoot;