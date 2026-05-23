import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { RegisterForm } from '@/components/auth';
import { PageContainer } from '@/components/common';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated, loading, error } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // RegisterForm calls onSubmit(email, name, password, confirmPassword)
  const handleSubmit = async (
    email: string,
    name: string,
    password: string,
    confirmPassword?: string
  ) => {
    try {
      // useAuth.register expects (email, name, password)
      await register(email, name, password);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Registration error:', err);
    }
  };

  return (
    <div className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center min-h-screen p-4">
      <PageContainer maxWidth="sm" padding="none">
        <div className="w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Create Account
            </h1>
            <p className="text-gray-600">
              Join the Weather Pipeline community
            </p>
          </div>

          {/* Register Form */}
          <RegisterForm
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
          />

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                className="text-indigo-600 hover:text-indigo-700 font-medium underline"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>
      </PageContainer>
    </div>
  );
};

export default Register;
