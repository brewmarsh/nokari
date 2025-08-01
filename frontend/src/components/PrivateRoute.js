import React from 'react';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children, userCount }) => {
  if (userCount === 0) {
    return <Navigate to="/onboarding" />;
  }

  return children;
};

export default PrivateRoute;
