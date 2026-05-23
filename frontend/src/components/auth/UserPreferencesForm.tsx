import React, { useState } from 'react';
import { Button, Card, Toggle, Select } from '@/components/ui';
import { Bell, Palette, Clock, AlertCircle } from 'lucide-react';

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  emailNotifications: boolean;
  weatherAlerts: boolean;
  alertSummary: 'immediate' | 'daily' | 'weekly' | 'never';
  temperatureUnit: 'celsius' | 'fahrenheit';
  windSpeedUnit: 'ms' | 'kmh' | 'mph' | 'knots';
  language: 'en' | 'es' | 'fr' | 'de';
}

export interface UserPreferencesFormProps {
  preferences: UserPreferences;
  onSave: (preferences: UserPreferences) => Promise<void>;
  loading?: boolean;
  error?: string | null;
  success?: boolean;
}

export const UserPreferencesForm: React.FC<UserPreferencesFormProps> = ({
  preferences: initialPreferences,
  onSave,
  loading = false,
  error = null,
  success = false,
}) => {
  const [preferences, setPreferences] = useState(initialPreferences);
  const [hasChanges, setHasChanges] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleChange = <K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ) => {
    setPreferences((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
    setLocalError(null);
  };

  const handleSave = async () => {
    try {
      await onSave(preferences);
      setHasChanges(false);
    } catch (err: any) {
      setLocalError(err.message || 'Failed to save preferences');
    }
  };

  const displayError = localError || error;

  return (
    <div className="space-y-6">
      {/* Appearance Section */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Palette className="w-5 h-5" />
          Appearance
        </h3>

        <div className="space-y-4">
          {/* Theme */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Theme
            </label>
            <Select
              options={[
                { label: 'Light', value: 'light' },
                { label: 'Dark', value: 'dark' },
                { label: 'System', value: 'system' },
              ]}
              value={preferences.theme}
              onChange={(value) => handleChange('theme', value as any)}
              disabled={loading}
            />
          </div>

          {/* Language */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <Select
              options={[
                { label: 'English', value: 'en' },
                { label: 'Spanish', value: 'es' },
                { label: 'French', value: 'fr' },
                { label: 'German', value: 'de' },
              ]}
              value={preferences.language}
              onChange={(value) => handleChange('language', value as any)}
              disabled={loading}
            />
          </div>
        </div>
      </Card>

      {/* Units Section */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Units & Format
        </h3>

        <div className="space-y-4">
          {/* Temperature Unit */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temperature Unit
            </label>
            <Select
              options={[
                { label: 'Celsius (°C)', value: 'celsius' },
                { label: 'Fahrenheit (°F)', value: 'fahrenheit' },
              ]}
              value={preferences.temperatureUnit}
              onChange={(value) => handleChange('temperatureUnit', value as any)}
              disabled={loading}
            />
          </div>

          {/* Wind Speed Unit */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Wind Speed Unit
            </label>
            <Select
              options={[
                { label: 'Meters/second (m/s)', value: 'ms' },
                { label: 'Kilometers/hour (km/h)', value: 'kmh' },
                { label: 'Miles/hour (mph)', value: 'mph' },
                { label: 'Knots', value: 'knots' },
              ]}
              value={preferences.windSpeedUnit}
              onChange={(value) => handleChange('windSpeedUnit', value as any)}
              disabled={loading}
            />
          </div>
        </div>
      </Card>

      {/* Notifications Section */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notifications
        </h3>

        <div className="space-y-4">
          {/* Email Notifications Toggle */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900">Email Notifications</p>
              <p className="text-xs text-gray-600">Receive updates via email</p>
            </div>
            <Toggle
              checked={preferences.emailNotifications}
              onChange={(checked) => handleChange('emailNotifications', checked)}
              disabled={loading}
            />
          </div>

          {/* Weather Alerts Toggle */}
          <div className="flex items-center justify-between pb-4 border-b border-gray-200">
            <div>
              <p className="text-sm font-medium text-gray-900">Weather Alerts</p>
              <p className="text-xs text-gray-600">Get notified of severe weather</p>
            </div>
            <Toggle
              checked={preferences.weatherAlerts}
              onChange={(checked) => handleChange('weatherAlerts', checked)}
              disabled={loading}
            />
          </div>

          {/* Alert Summary Frequency */}
          {preferences.emailNotifications && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Alert Summary Frequency
              </label>
              <Select
                options={[
                  { label: 'Immediate', value: 'immediate' },
                  { label: 'Daily', value: 'daily' },
                  { label: 'Weekly', value: 'weekly' },
                  { label: 'Never', value: 'never' },
                ]}
                value={preferences.alertSummary}
                onChange={(value) => handleChange('alertSummary', value as any)}
                disabled={loading || !preferences.emailNotifications}
              />
            </div>
          )}
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
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-700">Preferences saved successfully</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={loading || !hasChanges}
        >
          {loading ? 'Saving...' : 'Save Preferences'}
        </Button>
        <Button
          variant="secondary"
          onClick={() => {
            setPreferences(initialPreferences);
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

UserPreferencesForm.displayName = 'UserPreferencesForm';
