import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { PageContainer } from '@/components/common';
import { Card } from '@/components/ui';
import {
  ProfileSettingsForm,
  UserPreferencesForm,
  ChangePasswordForm,
} from '@/components/auth';
import { User, Settings, Lock } from 'lucide-react';

type TabType = 'profile' | 'preferences' | 'password';

const SettingsPage: React.FC = () => {
  const {
    user,
    preferences,
    fetchProfile,
    fetchPreferences,
    updateProfile,
    updatePreferences,
    changePassword,
    loading,
    error,
  } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [preferencesLoading, setPreferencesLoading] = useState(false);
  const [preferencesError, setPreferencesError] = useState<string | null>(null);
  const [preferencesSuccess, setPreferencesSuccess] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  useEffect(() => {
    // Fetch profile and preferences on component mount
    fetchProfile();
    fetchPreferences();
  }, []);

  const handleProfileSave = async (
    fullName: string,
    email: string,
    phone: string,
    location: string,
    bio: string
  ) => {
    setProfileLoading(true);
    setProfileError(null);
    setProfileSuccess(false);

    try {
      await updateProfile({
        fullName,
        email,
        phone,
        location,
        bio,
      });
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 3000);
    } catch (err: any) {
      setProfileError(err.message || 'Failed to update profile');
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePreferencesSave = async (prefs: any) => {
    setPreferencesLoading(true);
    setPreferencesError(null);
    setPreferencesSuccess(false);

    try {
      await updatePreferences(prefs);
      setPreferencesSuccess(true);
      setTimeout(() => setPreferencesSuccess(false), 3000);
    } catch (err: any) {
      setPreferencesError(err.message || 'Failed to update preferences');
    } finally {
      setPreferencesLoading(false);
    }
  };

  const handlePasswordChange = async (
    currentPassword: string,
    newPassword: string
  ) => {
    setPasswordLoading(true);
    setPasswordError(null);
    setPasswordSuccess(false);

    try {
      await changePassword(currentPassword, newPassword);
      setPasswordSuccess(true);
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: any) {
      setPasswordError(err.message || 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const tabs: Array<{
    id: TabType;
    label: string;
    icon: React.ReactNode;
  }> = [
    {
      id: 'profile',
      label: 'Profile',
      icon: <User className="w-4 h-4" />,
    },
    {
      id: 'preferences',
      label: 'Preferences',
      icon: <Settings className="w-4 h-4" />,
    },
    {
      id: 'password',
      label: 'Security',
      icon: <Lock className="w-4 h-4" />,
    },
  ];

  return (
    <PageContainer>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Account Settings
          </h1>
          <p className="text-gray-600">
            Manage your profile, preferences, and security
          </p>
        </div>

        {/* Tabs Navigation */}
        <Card className="mb-6">
          <div className="flex border-b border-gray-200">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors border-b-2 ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </Card>

        {/* Tab Content */}
        <div className="space-y-6">
          {/* Profile Tab */}
          {activeTab === 'profile' && user && (
            <Card>
              <ProfileSettingsForm
                profile={user}
                onSave={handleProfileSave}
                onChangePassword={() => setActiveTab('password')}
                loading={profileLoading}
                error={profileError}
                success={profileSuccess}
              />
            </Card>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && preferences && (
            <Card>
              <UserPreferencesForm
                preferences={preferences}
                onSave={handlePreferencesSave}
                loading={preferencesLoading}
                error={preferencesError}
                success={preferencesSuccess}
              />
            </Card>
          )}

          {/* Password Tab */}
          {activeTab === 'password' && (
            <Card>
              <ChangePasswordForm
                onSubmit={handlePasswordChange}
                loading={passwordLoading}
                error={passwordError}
                success={passwordSuccess}
                onCancel={() => setActiveTab('profile')}
              />
            </Card>
          )}
        </div>
      </div>
    </PageContainer>
  );
};

export default SettingsPage;
