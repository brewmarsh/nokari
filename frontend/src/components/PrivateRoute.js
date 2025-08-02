import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const PrivateRoute = ({ children, userCount }) => {
  const location = useLocation();

  if (userCount === 0 && location.pathname !== '/onboarding') {
    return <Navigate to="/onboarding" />;
  }

  return children;
};

export default PrivateRoute;
