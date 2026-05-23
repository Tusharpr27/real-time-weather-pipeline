import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { PasswordResetForm } from '@/components/auth';
import { PageContainer } from '@/components/common';
import { ArrowLeft } from 'lucide-react';

const ForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const { requestPasswordReset, loading, error } = useAuth();
  const [resetSent, setResetSent] = useState(false);

  const handleSubmit = async (email: string): Promise<void> => {
    try {
      await requestPasswordReset(email);
      setResetSent(true);
    } catch (err: any) {
      console.error('Password reset request error:', err);
    }
  };

  return (
    <div className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center min-h-screen p-4">
      <PageContainer maxWidth="sm" padding="none">
        <div className="w-full">
          {/* Back Button */}
          <button
            onClick={() => navigate('/login')}
            className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium mb-8 group"
          >
            <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
            Back to Login
          </button>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Reset Password
            </h1>
            <p className="text-gray-600">
              Enter your email address and we'll send you a link to reset your password
            </p>
          </div>

          {/* Password Reset Form */}
          <PasswordResetForm
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
            success={resetSent}
          />
        </div>
      </PageContainer>
    </div>
  );
};

export default ForgotPassword;
