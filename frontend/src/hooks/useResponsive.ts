import { useEffect, useState } from 'react';

type BreakpointKey = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

interface Breakpoints {
  xs: boolean;
  sm: boolean;
  md: boolean;
  lg: boolean;
  xl: boolean;
  '2xl': boolean;
}

/**
 * useResponsive Hook
 * Provides information about the current device/screen size
 * Useful for responsive behavior and conditionally rendering components
 *
 * @returns Object with breakpoint boolean flags and isMobile boolean
 *
 * @example
 * const { isMobile, isTablet, isDesktop, md } = useResponsive();
 * if (isMobile) {
 *   // Show mobile-specific UI
 * }
 */
export const useResponsive = () => {
  const [breakpoints, setBreakpoints] = useState<Breakpoints>({
    xs: false,
    sm: false,
    md: false,
    lg: false,
    xl: false,
    '2xl': false,
  });

  useEffect(() => {
    const checkBreakpoints = () => {
      // Tailwind breakpoints: xs: 0px, sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px
      const width = window.innerWidth;
      setBreakpoints({
        xs: width < 640,
        sm: width >= 640 && width < 768,
        md: width >= 768 && width < 1024,
        lg: width >= 1024 && width < 1280,
        xl: width >= 1280 && width < 1536,
        '2xl': width >= 1536,
      });
    };

    checkBreakpoints();
    window.addEventListener('resize', checkBreakpoints);
    return () => window.removeEventListener('resize', checkBreakpoints);
  }, []);

  return {
    ...breakpoints,
    isMobile: breakpoints.xs || breakpoints.sm,
    isTablet: breakpoints.md || breakpoints.lg,
    isDesktop: breakpoints.xl || breakpoints['2xl'],
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
  };
};

export default useResponsive;
