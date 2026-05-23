import React, { useState } from 'react';
import { Button, Input, Card } from '@/components/ui';
import { Lock, AlertCircle, CheckCircle } from 'lucide-react';

export interface ChangePasswordFormProps {
  onSubmit: (currentPassword: string, newPassword: string, confirmPassword: string) => Promise<void>;
  loading?: boolean;
  error?: string | null;
  success?: boolean;
  onCancel?: () => void;
}

export const ChangePasswordForm: React.FC<ChangePasswordFormProps> = ({
  onSubmit,
  loading = false,
  error = null,
  success = false,
  onCancel,
}) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const passwordsMatch = newPassword === confirmPassword && newPassword.length > 0;
  const isValid =
    currentPassword.length > 0 &&
    newPassword.length >= 8 &&
    passwordsMatch;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!isValid) {
      setLocalError('Please check all fields');
      return;
    }

    try {
      await onSubmit(currentPassword, newPassword, confirmPassword);
      // Reset form on success
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setLocalError(err.message || 'Failed to change password');
    }
  };

  const displayError = localError || error;

  if (success) {
    return (
      <Card className="p-8 max-w-md w-full">
        <div className="text-center">
          <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Password Changed</h2>
          <p className="text-gray-600 mb-6">
            Your password has been successfully updated.
          </p>
          <Button
            variant="primary"
            className="w-full"
            onClick={onCancel}
          >
            Back to Settings
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-8 max-w-md w-full">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Change Password</h2>

      {displayError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{displayError}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Current Password */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Current Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <Input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              className="pl-10"
            />
          </div>
        </div>

        {/* New Password */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            New Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <Input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              className="pl-10"
            />
          </div>
          {newPassword && newPassword.length < 8 && (
            <p className="mt-2 text-sm text-red-600">
              Password must be at least 8 characters
            </p>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Confirm New Password
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
          {newPassword && !passwordsMatch && (
            <p className="mt-2 text-sm text-red-600">
              Passwords do not match
            </p>
          )}
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          className="w-full"
          disabled={loading || !isValid}
        >
          {loading ? 'Changing...' : 'Change Password'}
        </Button>
      </form>

      {/* Footer Links */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <Button
          variant="ghost"
          className="w-full text-gray-600 hover:text-gray-700"
          onClick={onCancel}
        >
          Cancel
        </Button>
      </div>
    </Card>
  );
};

ChangePasswordForm.displayName = 'ChangePasswordForm';
