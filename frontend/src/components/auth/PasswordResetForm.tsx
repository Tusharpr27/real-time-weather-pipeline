import React, { useState } from 'react';
import { Button, Input, Card } from '@/components/ui';
import { Mail, AlertCircle, CheckCircle } from 'lucide-react';

export interface PasswordResetFormProps {
  onSubmit: (email: string) => Promise<void>;
  loading?: boolean;
  error?: string | null;
  success?: boolean;
}

export const PasswordResetForm: React.FC<PasswordResetFormProps> = ({
  onSubmit,
  loading = false,
  error = null,
  success = false,
}) => {
  const [email, setEmail] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!email) {
      setLocalError('Please enter your email address');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setLocalError('Please enter a valid email address');
      return;
    }

    try {
      await onSubmit(email);
    } catch (err: any) {
      setLocalError(err.message || 'Failed to send reset email');
    }
  };

  const displayError = localError || error;

  if (success) {
    return (
      <Card className="p-8 max-w-md w-full">
        <div className="text-center">
          <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Check Your Email</h2>
          <p className="text-gray-600 mb-6">
            We've sent a password reset link to <strong>{email}</strong>. 
            Click the link in the email to reset your password.
          </p>
          <p className="text-sm text-gray-500">
            Didn't receive the email? Check your spam folder or try again.
          </p>
          <Button
            variant="secondary"
            className="w-full mt-6"
            onClick={() => window.location.href = '/login'}
          >
            Back to Sign In
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-8 max-w-md w-full">
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Reset Password</h2>
      <p className="text-gray-600 text-sm mb-6">
        Enter your email address and we'll send you a link to reset your password.
      </p>

      {displayError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{displayError}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              disabled={loading}
              className="pl-10"
            />
          </div>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          className="w-full"
          disabled={loading}
        >
          {loading ? 'Sending...' : 'Send Reset Link'}
        </Button>
      </form>

      {/* Footer Links */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-sm text-gray-600 text-center">
          Remember your password?{' '}
          <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
            Sign In
          </a>
        </p>
      </div>
    </Card>
  );
};

PasswordResetForm.displayName = 'PasswordResetForm';
