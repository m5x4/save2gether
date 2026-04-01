/**
 * Image caching service
 * Stores merchant image URLs in localStorage to reduce API calls
 */

// Cache keys
const MERCHANT_IMAGE_CACHE_KEY = "merchantImageCache";
const CACHE_EXPIRY_KEY = "merchantImageCacheExpiry";
const CACHE_EXPIRY_TIME = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds

/**
 * Initialize cache if it doesn't exist
 */
const initializeCache = () => {
  if (!localStorage.getItem(MERCHANT_IMAGE_CACHE_KEY)) {
    localStorage.setItem(MERCHANT_IMAGE_CACHE_KEY, JSON.stringify({}));
    localStorage.setItem(
      CACHE_EXPIRY_KEY,
      JSON.stringify(Date.now() + CACHE_EXPIRY_TIME)
    );
  }

  // Check if cache has expired
  const expiry = JSON.parse(localStorage.getItem(CACHE_EXPIRY_KEY) || "0");
  if (Date.now() > expiry) {
    // Reset cache if expired
    localStorage.setItem(MERCHANT_IMAGE_CACHE_KEY, JSON.stringify({}));
    localStorage.setItem(
      CACHE_EXPIRY_KEY,
      JSON.stringify(Date.now() + CACHE_EXPIRY_TIME)
    );
  }
};

/**
 * Get image URL from cache
 * @param {string} merchantKey - Unique key for merchant (name + location)
 * @returns {string|null} - Image URL or null if not found
 */
export const getMerchantImageFromCache = (merchantKey) => {
  initializeCache();

  try {
    const cache = JSON.parse(
      localStorage.getItem(MERCHANT_IMAGE_CACHE_KEY) || "{}"
    );
    return cache[merchantKey] || null;
  } catch (error) {
    console.error("Error getting image from cache:", error);
    return null;
  }
};

/**
 * Store image URL in cache
 * @param {string} merchantKey - Unique key for merchant (name + location)
 * @param {string} imageUrl - Image URL to cache
 */
export const storeMerchantImageInCache = (merchantKey, imageUrl) => {
  if (!merchantKey || !imageUrl) return;

  try {
    initializeCache();
    const cache = JSON.parse(
      localStorage.getItem(MERCHANT_IMAGE_CACHE_KEY) || "{}"
    );
    cache[merchantKey] = imageUrl;
    localStorage.setItem(MERCHANT_IMAGE_CACHE_KEY, JSON.stringify(cache));
  } catch (error) {
    console.error("Error storing image in cache:", error);
  }
};

/**
 * Clear the entire merchant image cache
 */
export const clearMerchantImageCache = () => {
  localStorage.removeItem(MERCHANT_IMAGE_CACHE_KEY);
  localStorage.removeItem(CACHE_EXPIRY_KEY);
  initializeCache();
};
