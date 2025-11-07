import React, { useState, useEffect } from 'react';
import { api_unauthenticated } from '../services/api';
import './ConnectionStatus.css';

const ConnectionStatus = () => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await api_unauthenticated.get('/health');
        setIsConnected(true);
      } catch (error) {
        setIsConnected(false);
      }
    };

    checkConnection();
  }, []);

  return (
    <div className="connection-status">
      <span className={`status-icon ${isConnected ? 'connected' : 'disconnected'}`}></span>
    </div>
  );
};

export default ConnectionStatus;
