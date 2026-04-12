import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_RECOMMENDATION_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

const normalizeTimestamp = (value) => {
  if (!value) return value;
  if (typeof value === "object" && typeof value.seconds === "number")
    return value;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return {
    seconds: Math.floor(date.getTime() / 1000),
  };
};

const normalizeDeal = (deal) => ({
  ...deal,
  validUntil: normalizeTimestamp(deal.validUntil),
  createdDateTime: normalizeTimestamp(deal.createdDateTime),
});

export const getRecommendationDeals = async ({
  userId,
  limit = 20,
  category = null,
  maxDistance = null,
  userLat = null,
  userLng = null,
}) => {
  if (!userId) return [];

  const params = {
    limit,
    category,
    max_distance: maxDistance,
    user_lat: userLat,
    user_lng: userLng,
  };

  Object.keys(params).forEach((key) => {
    if (
      params[key] === null ||
      params[key] === undefined ||
      params[key] === ""
    ) {
      delete params[key];
    }
  });

  const response = await api.get(`/recommendations/${userId}`, { params });
  const recommendations = response?.data?.recommendations || [];

  return recommendations.map(normalizeDeal);
};
