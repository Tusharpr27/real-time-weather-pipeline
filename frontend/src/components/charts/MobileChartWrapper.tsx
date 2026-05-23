import React, { useRef, useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useResponsive } from '@/hooks/useResponsive';

interface MobileChartProps {
  children: React.ReactNode;
  title?: string;
  height?: string;
  scrollable?: boolean;
}

/**
 * MobileChartWrapper Component
 * Provides mobile-optimized chart container with:
 * - Touch-friendly interactions
 * - Horizontal scrolling support for small screens
 * - Optimized font sizes and spacing for mobile
 * - Responsive height adjustments
 * - Touch-enabled zoom/pan capabilities
 */
const MobileChartWrapper: React.FC<MobileChartProps> = ({
  children,
  title,
  height = 'h-72',
  scrollable = true,
}) => {
  const { isMobile } = useResponsive();
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const checkScroll = () => {
    if (scrollContainerRef.current && scrollable) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft + clientWidth < scrollWidth);
    }
  };

  useEffect(() => {
    checkScroll();
    window.addEventListener('resize', checkScroll);
    return () => window.removeEventListener('resize', checkScroll);
  }, [children, scrollable]);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 300;
      scrollContainerRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      });
      setTimeout(checkScroll, 300);
    }
  };

  return (
    <div className={`${height} flex flex-col`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-3 px-4 md:px-0">
          {title}
        </h3>
      )}

      <div className="flex-1 relative">
        {/* Scroll Container */}
        <div
          ref={scrollContainerRef}
          onScroll={checkScroll}
          className={`
            flex-1 overflow-x-auto overflow-y-hidden
            ${scrollable ? 'touch-pan-y' : ''}
            ${!isMobile ? 'overflow-x-hidden' : ''}
          `}
          style={{ WebkitOverflowScrolling: 'touch' }}
        >
          <div className={`${!isMobile && scrollable ? 'min-w-full' : ''}`}>
            {children}
          </div>
        </div>

        {/* Scroll Indicators - Mobile Only */}
        {isMobile && scrollable && (
          <>
            {canScrollLeft && (
              <button
                onClick={() => scroll('left')}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-r-lg transition-opacity hover:bg-black/70"
                aria-label="Scroll left"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            )}
            {canScrollRight && (
              <button
                onClick={() => scroll('right')}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-l-lg transition-opacity hover:bg-black/70"
                aria-label="Scroll right"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default MobileChartWrapper;
