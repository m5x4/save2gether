<template>
  <Header :query="searchQuery" @apply-search="findDeal($event)" />

  <div id="titleFilter">
    <h2 style="text-decoration: underline">Search Results</h2>
    <div id="filterSortButtons">
      <FilterButton @apply-filters="handleFilters($event)" />
      <SortButton @sort-deals="sortDeals" />
    </div>
  </div>

  <div id="dealList">
    <template v-if="filteredDeals.length > 0">
      <div class="deal-card">
        <DealCard
          v-for="deal in filteredDeals"
          :key="deal.id"
          :dealId="deal.id"
          :dealName="deal.dealName"
          :merchantName="deal.merchantName"
          :location="deal.location"
          :distance="deal.distance"
          :expiryDate="formatDate(deal.validUntil)"
          :remainingTime="calculateRemainingTime(deal.validUntil)"
          :category="deal.category"
        />
      </div>
    </template>
    <h2 v-else id="noDeals">No Deals Found</h2>
  </div>
</template>

<script>
import { getDeals } from "@/firebase/firestore";
import DealCard from "@/components/DealCard.vue";
import FilterButton from "@/components/FilterButton.vue";
import SortButton from "@/components/SortButton.vue";
import Header from "@/components/Header.vue";
import axios from "axios";

export default {
  components: { DealCard, FilterButton, SortButton, Header },
  data() {
    return {
      deals: [],
      filters: {
        validUntil: null,
        maxDistance: null,
      },
      userLat: null,
      userLng: null,
      searchQuery: "",
    };
  },
  computed: {
    filteredDeals() {
      // console.log("Filtering deals with distance:", this.filters.maxDistance);
      return this.deals
        .filter((deal) => {
          const dealExpiry = new Date(deal.validUntil.seconds * 1000);
          const now = new Date();
          // hide expired deals
          if (dealExpiry < now) {
            return false;
          }
          if (this.filters.validUntil) {
            const selectedDate = new Date(this.filters.validUntil);
            if (dealExpiry < selectedDate) {
              return false;
            }
          }
          if (
            this.filters.maxDistance !== null &&
            this.filters.maxDistance !== undefined
          ) {
            // Extract numeric distance value from string (e.g. "3.45 km away" -> 3.45)
            const distanceMatch = String(deal.distance).match(/^(\d+\.?\d*)/);
            const numericDistance = distanceMatch
              ? parseFloat(distanceMatch[1])
              : Infinity;

            if (numericDistance > this.filters.maxDistance) {
              return false;
            }
          }
          return true;
        })
        .filter((deal) =>
          deal.dealName.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
    },
  },
  async created() {
    this.searchQuery = this.$route.query.q || "";
    await this.fetchDeals();
    await this.getUserLocation();
    await this.calculateAllDistances();
  },
  watch: {
    // Watch for changes in the route query
    "$route.query.q": function (newQuery) {
      this.searchQuery = newQuery || "";
    },
  },
  methods: {
    async fetchDeals() {
      try {
        const deals = await getDeals();
        this.deals = deals;
      } catch (error) {
        console.error("There is an error fetching deals: ", error);
      }
    },
    handleFilters(filters) {
      // console.log("Received Filters: ", filters);
      this.filters = filters;
    },
    findDeal(searchQuery) {
      // console.log("Received Search: ", searchQuery);
      if (!searchQuery) {
        this.$router.push("/HomeView");
        return;
      }
      this.searchQuery = searchQuery;
    },
    async getUserLocation() {
      return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              this.userLat = position.coords.latitude;
              this.userLng = position.coords.longitude;
              resolve();
            },
            (error) => {
              console.error("There is an error fetching user location:", error);
              resolve();
            }
          );
        } else {
          resolve();
        }
      });
    },
    formatDate(timestamp) {
      try {
        const date = new Date(timestamp.seconds * 1000);
        return date.toLocaleDateString("en-SG", {
          year: "numeric",
          month: "long",
          day: "numeric",
        });
      } catch (error) {
        console.error("There is an error converting time: ", error);
        return "Unable to fetch Date";
      }
    },
    calculateRemainingTime(timestamp) {
      try {
        const expiryDate = new Date(timestamp.seconds * 1000);
        const now = new Date();
        const timeDiff = expiryDate - now;

        if (timeDiff <= 0) return "Expired";
        const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        const hours = Math.floor(
          (timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
        );
        return `${days} days, ${hours} hours from now`;
      } catch (error) {
        console.error("There is an error calculating remaining time: ", error);
        return "Unable to calculate remaining time";
      }
    },
    async calculateDistance(dealLocation) {
      // console.log(
      //   `Starting distance calculation for location: "${dealLocation}"`
      // );
      const API_KEY = import.meta.env.VITE_GOOGLEMAPS_API_KEY;
      if (!this.userLat || !this.userLng) {
        return "Unable to fetch user location";
      }

      const fetchDistanceFromInput = async (inputLocation) => {
        return await axios.post(
          "https://places.googleapis.com/v1/places:autocomplete",
          {
            input: inputLocation,
            origin: { latitude: this.userLat, longitude: this.userLng },
            locationBias: {
              circle: {
                center: { latitude: 1.3521, longitude: 103.8198 },
                radius: 20000,
              },
            },
          },
          {
            headers: {
              "Content-Type": "application/json",
              "X-Goog-Api-Key": API_KEY,
            },
          }
        );
      };

      try {
        const response = await fetchDistanceFromInput(dealLocation);
        const distanceMeters =
          response.data.suggestions[0]?.placePrediction?.distanceMeters;
        if (distanceMeters) {
          const distanceKm = (distanceMeters / 1000).toFixed(2);
          return `${distanceKm} km away`;
        }
      } catch (error) {
        console.warn(`First attempt failed:`, error.message);
      }

      // Extract postal code of address and use it as fallback
      const match = dealLocation.match(/Singapore\s*(\d{6})/i);
      if (match && match[1]) {
        const postalCode = match[1];
        try {
          const fallbackResponse = await fetchDistanceFromInput(postalCode);
          const fallbackDistance =
            fallbackResponse.data.suggestions[0]?.placePrediction
              ?.distanceMeters;
          if (fallbackDistance) {
            const distanceKm = (fallbackDistance / 1000).toFixed(2);
            return `${distanceKm} km away`;
          }
        } catch (fallbackError) {
          console.warn(`Fallback attempt failed:`, fallbackError.message);
        }
      }
      // If all fails
      console.warn(`Unable to fetch address for: "${dealLocation}"`);
      return "Unable to fetch address";
    },
    async calculateAllDistances() {
      this.deals = await Promise.all(
        this.deals.map(async (deal) => {
          deal.distance = await this.calculateDistance(deal.location);
          return deal;
        })
      );
    },
    sortDeals(criteria) {
      if (criteria === "name") {
        this.deals.sort((a, b) => a.dealName.localeCompare(b.dealName));
      } else if (criteria === "distance") {
        this.deals.sort((a, b) => {
          const distanceA = parseFloat(a.distance) || 100000;
          const distanceB = parseFloat(b.distance) || 100000;
          return distanceA - distanceB;
        });
      } else if (criteria === "expiry") {
        this.deals.sort((a, b) => {
          const expiryA = new Date(a.validUntil.seconds) || 0;
          const expiryB = new Date(b.validUntil.seconds) || 0;
          return expiryB - expiryA;
        });
      } else if (criteria === "newest") {
        this.deals.sort((a, b) => {
          if (!a.createdDateTime) return 1;
          if (!b.createdDateTime) return -1;
          const dateA = new Date(a.createdDateTime.seconds);
          const dateB = new Date(b.createdDateTime.seconds);
          return dateB - dateA;
        });
      }
    },
  },
};
</script>

<style scoped>
#filterSortButtons {
  display: flex;
  gap: 10px;
}

#titleFilter {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 20px 70px;
}

#dealList {
  margin: 0 60px;
}

#noDeals {
  text-align: center;
}
</style>
