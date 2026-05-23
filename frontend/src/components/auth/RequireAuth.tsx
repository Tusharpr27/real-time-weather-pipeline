import React from 'react';

interface RequireAuthProps {
  children: React.ReactNode;
}

const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  return <>{children}</>;
};

export default RequireAuth;
