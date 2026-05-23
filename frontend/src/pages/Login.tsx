import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { LoginForm } from '@/components/auth';
import { PageContainer } from '@/components/common';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, loading, error } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (email: string, password: string) => {
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
    }
  };

  return (
    <div className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center min-h-screen p-4">
      <PageContainer maxWidth="sm" padding="none">
        <div className="w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Weather Pipeline
            </h1>
            <p className="text-gray-600">
              Real-time weather monitoring and analytics
            </p>
          </div>

          {/* Login Form */}
          <LoginForm
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
          />
        </div>
      </PageContainer>
    </div>
  );
};

export default Login;
