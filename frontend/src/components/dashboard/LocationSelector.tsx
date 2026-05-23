import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button } from '@/components/ui';
import { MapPin, Plus, X } from 'lucide-react';

export interface LocationSelectorProps {
  selectedLocations: string[];
  availableLocations: Array<{ id: string; name: string }>;
  onSelectionChange: (locationIds: string[]) => void;
  maxSelections?: number;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({
  selectedLocations,
  availableLocations,
  onSelectionChange,
  maxSelections = 10,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLocations = availableLocations.filter((loc) =>
    (loc.name || '').toLowerCase().includes((searchTerm || '').toLowerCase()) &&
    !selectedLocations.includes(loc.id)
  );

  const addLocation = useCallback(
    (locationId: string) => {
      if (selectedLocations.length < maxSelections) {
        onSelectionChange([...selectedLocations, locationId]);
        setSearchTerm('');
      }
    },
    [selectedLocations, maxSelections, onSelectionChange]
  );

  const removeLocation = useCallback(
    (locationId: string) => {
      onSelectionChange(selectedLocations.filter((id) => id !== locationId));
    },
    [selectedLocations, onSelectionChange]
  );

  const selectedLocationNames = selectedLocations
    .map((id) => availableLocations.find((loc) => loc.id === id)?.name)
    .filter(Boolean)
    .join(', ');

  return (
    <Card>
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-center gap-2">
          <MapPin size={18} className="text-blue-600" />
          <h3 className="font-semibold text-gray-900">Locations</h3>
          <span className="ml-auto text-xs text-gray-600">
            {selectedLocations.length} / {maxSelections}
          </span>
        </div>

        {/* Selected Locations */}
        {selectedLocations.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedLocations.map((locationId) => {
              const location = availableLocations.find(
                (loc) => loc.id === locationId
              );
              return (
                <div
                  key={locationId}
                  className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                >
                  <span>{location?.name}</span>
                  <button
                    onClick={() => removeLocation(locationId)}
                    className="ml-1 hover:opacity-75 transition-opacity"
                  >
                    <X size={14} />
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Add Location Button */}
        {selectedLocations.length < maxSelections && (
          <div className="relative">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              fullWidth
              leftIcon={<Plus size={14} />}
            >
              Add Location
            </Button>

            {/* Dropdown */}
            {isOpen && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                {/* Search */}
                <input
                  type="text"
                  placeholder="Search locations..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border-b border-gray-200 focus:outline-none text-sm"
                  autoFocus
                />

                {/* Options */}
                <div className="max-h-48 overflow-y-auto">
                  {filteredLocations.length === 0 ? (
                    <div className="px-3 py-2 text-sm text-gray-600">
                      No locations available
                    </div>
                  ) : (
                    filteredLocations.map((location) => (
                      <button
                        key={location.id}
                        onClick={() => {
                          addLocation(location.id);
                          setIsOpen(false);
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-blue-50 text-sm text-gray-700 transition-colors"
                      >
                        {location.name}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Backdrop */}
            {isOpen && (
              <div
                className="fixed inset-0 z-0"
                onClick={() => setIsOpen(false)}
              />
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

LocationSelector.displayName = 'LocationSelector';
