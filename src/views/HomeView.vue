<template>
  <Header @apply-search="findDeal($event)" />

  <h2 class="section-title">Categories</h2>
  <div id="categories">
    <div class="category-buttons">
      <button
        v-for="(category, index) in categories"
        :key="index"
        @click="selectCategory(category)"
        class="category-btn"
      >
        <img
          :src="categoryIcons[category]"
          alt="Category Icon"
          class="category-icon"
        />
        {{ category }}
      </button>
    </div>
  </div>

  <div class="deals-header">
    <h2 class="section-title" style="text-decoration: underline">
      Deals for you
    </h2>
    <div class="filter-sort-buttons">
      <FilterButton @apply-filters="handleFilters($event)" />
      <SortButton @sort-deals="sortDeals" />
    </div>
  </div>

  <div id="dealList">
    <template v-if="filteredDealsByCategory.length > 0">
      <DealCard
        v-for="deal in filteredDealsByCategory"
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
    </template>
    <h2 v-else id="noDeals">No Deals Posted</h2>
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
  components: { FilterButton, SortButton, DealCard, Header },
  data() {
    return {
      categories: [
        "Food & Beverage",
        "Lifestyle & Fitness",
        "Travel & Attractions",
        "Retail",
        "Games & Entertainment",
      ],
      deals: [],
      filters: {
        validUntil: null,
        maxDistance: null,
      },
      userLat: null,
      userLng: null,
      searchQuery: "",
      sortfilterUsed: null,
    };
  },
  computed: {
    categoryIcons() {
      return {
        "Food & Beverage": new URL("@/assets/icons/food.png", import.meta.url)
          .href,
        "Lifestyle & Fitness": new URL(
          "@/assets/icons/lifestyle.png",
          import.meta.url
        ).href,
        "Travel & Attractions": new URL(
          "@/assets/icons/travel.png",
          import.meta.url
        ).href,
        Retail: new URL("@/assets/icons/retail.png", import.meta.url).href,
        "Games & Entertainment": new URL(
          "@/assets/icons/games.png",
          import.meta.url
        ).href,
      };
    },
    categoryIcons() {
      return {
        "Food & Beverage": new URL("@/assets/icons/food.png", import.meta.url)
          .href,
        "Lifestyle & Fitness": new URL(
          "@/assets/icons/lifestyle.png",
          import.meta.url
        ).href,
        "Travel & Attractions": new URL(
          "@/assets/icons/travel.png",
          import.meta.url
        ).href,
        Retail: new URL("@/assets/icons/retail.png", import.meta.url).href,
        "Games & Entertainment": new URL(
          "@/assets/icons/games.png",
          import.meta.url
        ).href,
      };
    },
    filteredDealsByCategory() {
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
    await this.fetchDeals();
    if (!this.sortfilterUsed) {
      this.deals.sort((a, b) => (b.clicks || 0) - (a.clicks || 0)); // Default sort by clicks
    }
    await this.getUserLocation();
    await this.calculateAllDistances();
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
    selectCategory(category) {
      // console.log("Food & Beverage");
      this.$router.push({
        name: "ViewDeal",
        query: { category },
      });
    },
    handleFilters(filters) {
      // console.log("Received Filters: ", filters);
      this.filters = filters;
    },
    findDeal(searchQuery) {
      // console.log("Received Search: ", searchQuery);
      this.searchQuery = searchQuery;
    },
    sortDeals(criteria) {
      if (criteria === "name") {
        this.deals.sort((a, b) => a.dealName.localeCompare(b.dealName));
      } else if (criteria === "distance") {
        this.deals.sort((a, b) => {
          const distanceA = parseFloat(a.distance); // Ensure it's a number
          const distanceB = parseFloat(b.distance); // Ensure it's a number
          return distanceA - distanceB; // Sort numerically
        });
      } else if (criteria === "expiry") {
        this.deals.sort((a, b) => {
          const expiryA = new Date(a.validUntil.seconds * 1000);
          const expiryB = new Date(b.validUntil.seconds * 1000);
          return expiryB - expiryA; // Sort from longest to shortest time to expiry
        });
      } else if (criteria === "newest") {
        this.deals.sort((a, b) => {
          if (!a.createdDateTime) {
            return 1; // Treat deals without createdDateTime as older
          }
          if (!b.createdDateTime) {
            return -1; // Treat deals without createdDateTime as older
          }
          const dateA = new Date(a.createdDateTime.seconds);
          const dateB = new Date(b.createdDateTime.seconds);
          return dateB - dateA; // Sort from newest to oldest
        });
      }
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
  },
};
</script>

<style scoped>
.home {
  padding: 20px;
  font-family: "Inter", sans-serif;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #123456;
  color: white;
  padding: 15px;
  margin-bottom: 20px;
}

.logo {
  height: 40px;
  margin-right: 20px;
}

.search-bar {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  font-family: "Inter", sans-serif;
  border: none;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  outline: none;
}

.section-title {
  text-align: center;
  font-size: 22px;
  color: #333;
  margin-bottom: 10px;
  /* text-decoration: underline; */
}

.category-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.category-btn {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: black;
  border: none;
  padding: 20px 20px;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  text-align: center;
  background-color: white;
  width: 150px;
}

.category-icon {
  width: 50px;
  height: 50px;
  margin-bottom: 10px;
  object-fit: contain;
}

.category-btn:hover {
  background: lightgrey;
}

.deals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 70px;
}

.filter-sort-buttons {
  display: flex;
  gap: 10px;
}

.deals {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.deal-card {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

#dealList {
  margin: 0 60px;
}
</style>
