import React, { useState } from 'react';
import { Button, Input, Card } from '@/components/ui';
import { User, Mail, AlertCircle, CheckCircle } from 'lucide-react';

export interface ProfileData {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
  bio?: string;
  location?: string;
  phone?: string;
}

export interface ProfileSettingsFormProps {
  profile: ProfileData;
  onSave: (profile: ProfileData) => Promise<void>;
  onChangePassword?: () => void;
  loading?: boolean;
  error?: string | null;
  success?: boolean;
}

export const ProfileSettingsForm: React.FC<ProfileSettingsFormProps> = ({
  profile: initialProfile,
  onSave,
  onChangePassword,
  loading = false,
  error = null,
  success = false,
}) => {
  const [profile, setProfile] = useState(initialProfile);
  const [hasChanges, setHasChanges] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleChange = <K extends keyof ProfileData>(
    key: K,
    value: ProfileData[K]
  ) => {
    setProfile((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
    setLocalError(null);
  };

  const handleSave = async () => {
    if (!profile.name || !profile.email) {
      setLocalError('Name and email are required');
      return;
    }

    try {
      await onSave(profile);
      setHasChanges(false);
    } catch (err: any) {
      setLocalError(err.message || 'Failed to save profile');
    }
  };

  const displayError = localError || error;

  return (
    <div className="space-y-6">
      {/* Avatar Section */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Picture</h3>
        
        <div className="flex items-center gap-6">
          {profile.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt={profile.name}
              className="w-20 h-20 rounded-full object-cover"
            />
          ) : (
            <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
              <User className="w-10 h-10 text-gray-400" />
            </div>
          )}
          
          <Button variant="secondary">
            Change Picture
          </Button>
        </div>
      </Card>

      {/* Profile Information */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h3>

        <div className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <Input
                type="text"
                value={profile.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="Your name"
                disabled={loading}
                className="pl-10"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <Input
                type="email"
                value={profile.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="your@email.com"
                disabled={loading}
                className="pl-10"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              We'll use this for your account and notifications
            </p>
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number (optional)
            </label>
            <Input
              type="tel"
              value={profile.phone || ''}
              onChange={(e) => handleChange('phone', e.target.value)}
              placeholder="+1 (555) 000-0000"
              disabled={loading}
            />
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location (optional)
            </label>
            <Input
              type="text"
              value={profile.location || ''}
              onChange={(e) => handleChange('location', e.target.value)}
              placeholder="City, Country"
              disabled={loading}
            />
          </div>

          {/* Bio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bio (optional)
            </label>
            <textarea
              value={profile.bio || ''}
              onChange={(e) => handleChange('bio', e.target.value)}
              placeholder="Tell us about yourself"
              disabled={loading}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              {(profile.bio || '').length}/500
            </p>
          </div>
        </div>
      </Card>

      {/* Security Section */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Security</h3>
        
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Manage your password and security settings
          </p>
          <Button
            variant="secondary"
            onClick={onChangePassword}
            disabled={loading}
          >
            Change Password
          </Button>
        </div>
      </Card>

      {/* Error Message */}
      {displayError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{displayError}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-700">Profile updated successfully</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={loading || !hasChanges}
        >
          {loading ? 'Saving...' : 'Save Changes'}
        </Button>
        <Button
          variant="secondary"
          onClick={() => {
            setProfile(initialProfile);
            setHasChanges(false);
          }}
          disabled={loading || !hasChanges}
        >
          Cancel
        </Button>
      </div>
    </div>
  );
};

ProfileSettingsForm.displayName = 'ProfileSettingsForm';
