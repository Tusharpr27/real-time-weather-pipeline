import React, { useState } from 'react';
import { Button, Input, Card, Checkbox } from '@/components/ui';
import { Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react';

export interface RegisterFormProps {
  onSubmit: (email: string, name: string, password: string, confirmPassword: string) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

const PASSWORD_REQUIREMENTS = [
  { label: 'At least 8 characters', check: (pwd: string) => pwd.length >= 8 },
  { label: 'Contains uppercase letter', check: (pwd: string) => /[A-Z]/.test(pwd) },
  { label: 'Contains lowercase letter', check: (pwd: string) => /[a-z]/.test(pwd) },
  { label: 'Contains number', check: (pwd: string) => /[0-9]/.test(pwd) },
];

export const RegisterForm: React.FC<RegisterFormProps> = ({
  onSubmit,
  loading = false,
  error = null,
}) => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const passwordValid = PASSWORD_REQUIREMENTS.every((req) => req.check(password));
  const passwordsMatch = password === confirmPassword && password.length > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!email || !name || !password || !confirmPassword) {
      setLocalError('Please fill in all fields');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setLocalError('Please enter a valid email address');
      return;
    }

    if (!passwordValid) {
      setLocalError('Password does not meet requirements');
      return;
    }

    if (!passwordsMatch) {
      setLocalError('Passwords do not match');
      return;
    }

    if (!agreed) {
      setLocalError('You must agree to the terms and conditions');
      return;
    }

    try {
      await onSubmit(email, name, password, confirmPassword);
    } catch (err: any) {
      setLocalError(err.message || 'Registration failed');
    }
  };

  const displayError = localError || error;

  return (
    <Card className="p-8 max-w-md w-full">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Account</h2>

      {displayError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{displayError}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Full Name
          </label>
          <div className="relative">
            <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <Input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              disabled={loading}
              className="pl-10"
            />
          </div>
        </div>

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

          {/* Password Requirements */}
          <div className="mt-3 space-y-2">
            {PASSWORD_REQUIREMENTS.map((req, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm">
                {req.check(password) ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-gray-300" />
                )}
                <span className={req.check(password) ? 'text-green-700' : 'text-gray-600'}>
                  {req.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Confirm Password Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Confirm Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              className="pl-10"
            />
          </div>
          {password && !passwordsMatch && (
            <p className="mt-2 text-sm text-red-600">Passwords do not match</p>
          )}
          {passwordsMatch && (
            <p className="mt-2 text-sm text-green-600">Passwords match</p>
          )}
        </div>

        {/* Terms Agreement */}
        <div className="flex items-start gap-3 pt-2">
          <Checkbox
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            disabled={loading}
          />
          <label className="text-sm text-gray-600">
            I agree to the{' '}
            <a href="/terms" className="text-blue-600 hover:text-blue-700 font-medium">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-blue-600 hover:text-blue-700 font-medium">
              Privacy Policy
            </a>
          </label>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          className="w-full"
          disabled={loading || !passwordValid || !passwordsMatch || !agreed}
        >
          {loading ? 'Creating account...' : 'Sign Up'}
        </Button>
      </form>

      {/* Footer Links */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-sm text-gray-600 text-center">
          Already have an account?{' '}
          <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
            Sign In
          </a>
        </p>
      </div>
    </Card>
  );
};

RegisterForm.displayName = 'RegisterForm';
