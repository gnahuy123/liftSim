/**
 * Utility functions for lift position calculations.
 */

const FLOOR_HEIGHT = 36; // pixels per floor

/**
 * Calculate the bottom position of a lift in pixels.
 * @param {number} level - Current floor level
 * @param {number} floorHeight - Height of a single floor in pixels
 * @param {number} offset - Offset from bottom of shaft
 * @returns {number} Bottom position in pixels
 */
export function calculateLiftPosition(level, floorHeight, offset = 2) {
    return (level * floorHeight) + offset;
}

/**
 * Get floor height constant.
 * @returns {number} Floor height in pixels
 */
export function getFloorHeight() {
    return FLOOR_HEIGHT;
}
