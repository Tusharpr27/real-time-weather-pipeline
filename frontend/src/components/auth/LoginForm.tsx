import React, { useState } from 'react';
import { Button, Input, Card } from '@/components/ui';
import { Mail, Lock, AlertCircle } from 'lucide-react';

export interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  loading = false,
  error = null,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!email || !password) {
      setLocalError('Please fill in all fields');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setLocalError('Please enter a valid email address');
      return;
    }

    try {
      await onSubmit(email, password);
    } catch (err: any) {
      setLocalError(err.message || 'Login failed');
    }
  };

  const displayError = localError || error;

  return (
    <Card className="p-8 max-w-md w-full">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>

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

        {/* Password Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
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
          {loading ? 'Signing in...' : 'Sign In'}
        </Button>
      </form>

      {/* Footer Links */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-sm text-gray-600 text-center">
          Don't have an account?{' '}
          <a href="/register" className="text-blue-600 hover:text-blue-700 font-medium">
            Sign Up
          </a>
        </p>
        <p className="text-sm text-gray-600 text-center mt-2">
          <a href="/forgot-password" className="text-gray-600 hover:text-gray-700">
            Forgot your password?
          </a>
        </p>
      </div>
    </Card>
  );
};

LoginForm.displayName = 'LoginForm';
