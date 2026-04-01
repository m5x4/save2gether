<template>
  <div id="dealCard" @click="handleClick">
    <div id="info1">
      <img
        :src="imageError ? getCategoryImage(category) : merchantImage"
        @error="onImageError"
        @load="onImageLoad"
        alt=""
        :class="imageError ? 'fallback-image' : 'merchant-image'"
      />
      <div id="info1-text">
        <h3 id="title">{{ dealName }}</h3>
        <p id="location">{{ location }}</p>
        <p id="distance">{{ distance }}</p>
        <p id="createdTime">{{ createdTime }}</p>
      </div>
    </div>
    <div id="info2">
      <p id="expiry">Expires: {{ expiryDate }}</p>
      <p id="remainingTime">{{ remainingTime }}</p>
    </div>
  </div>
</template>

<script>
import { getDeal } from "@/firebase/firestore.js";
import { Loader } from "@googlemaps/js-api-loader";
import { db } from "@/firebase/firebase.js";
import { doc, updateDoc, increment } from "firebase/firestore";
import {
  getMerchantImageFromCache,
  storeMerchantImageInCache,
} from "@/services/imageCache.js";

export default {
  props: {
    dealId: String,
    dealName: String,
    merchantName: String,
    location: String,
    distance: String,
    expiryDate: String,
    remainingTime: String,
    category: String,
  },
  data() {
    return {
      merchantImage: null,
      placesService: null,
      categoryImages: {
        "Food & Beverage": "/src/assets/icons/food.png",
        "Lifestyle & Fitness": "/src/assets/icons/lifestyle.png",
        "Travel & Attractions": "/src/assets/icons/travel.png",
        Retail: "/src/assets/icons/retail.png",
        "Games & Entertainment": "/src/assets/icons/games.png",
      },
      imageLoaded: false,
      imageError: false,
      createdTime: "Not Available",
    };
  },
  async created() {
    try {
      const deal = await getDeal(this.dealId);
      if (deal) {
        // Get merchant image from cache or API
        await this.getMerchantImage(deal);
        await this.getTime(deal);
      }
    } catch (error) {
      console.error("Error fetching merchant image:", error);
    }
  },
  methods: {
    async getTime(deal) {
      const time = deal.createdDateTime;
      const date = new Date(time.seconds * 1000);
      // return Created x hours ago
      const hours = Math.floor((Date.now() - date) / (1000 * 60 * 60));
      const minutes = Math.floor(
        ((Date.now() - date) % (1000 * 60 * 60)) / (1000 * 60)
      );
      if (hours > 24) {
        this.createdTime = `Created ${Math.floor(hours / 24)} day${
          Math.floor(hours / 24) > 1 ? "s" : ""
        } ago`;
      } else if (hours > 0) {
        this.createdTime = `Created ${hours} hour${hours > 1 ? "s" : ""} ago`;
      } else if (minutes > 5) {
        this.createdTime = `Created ${minutes} minute${
          minutes > 1 ? "s" : ""
        } ago`;
      } else {
        this.createdTime = "Created Just now";
      }
    },
    async getMerchantImage(deal) {
      // Generate a unique key for this merchant
      const merchantKey = `${deal.merchantName || deal.dealName}-${
        deal.location
      }`;

      // Try to get from cache first
      const cachedImage = getMerchantImageFromCache(merchantKey);
      if (cachedImage) {
        // Add image validation here
        const isValid = await this.validateImageUrl(cachedImage);
        if (isValid) {
          this.merchantImage = cachedImage;
          return;
        }
        // If cached image is invalid, continue to fetch a new one
      }

      // If not in cache, fetch from Google Places API
      await this.initializePlacesService();
      await this.fetchMerchantImage(deal, merchantKey);

      // If still no image, use category fallback
      if (this.merchantImage === null) {
        this.imageError = true; // Explicitly set error state to use fallback image
        this.merchantImage = this.getCategoryImage(this.category);
      }
    },
    // Add this method to validate image URLs
    validateImageUrl(url) {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = url;
      });
    },
    async initializePlacesService() {
      const loader = new Loader({
        apiKey: import.meta.env.VITE_GOOGLEMAPS_API_KEY,
        version: "weekly",
        libraries: ["places"],
      });
      await loader.load();
      const map = new google.maps.Map(document.createElement("div"));
      this.placesService = new google.maps.places.PlacesService(map);
    },
    async fetchMerchantImage(deal, merchantKey) {
      return new Promise((resolve) => {
        const request = {
          query: deal.merchantName
            ? deal.merchantName + " " + deal.location
            : deal.dealName + " " + deal.location,
          fields: ["photos"],
        };

        this.placesService.textSearch(request, (results, status) => {
          if (
            status === google.maps.places.PlacesServiceStatus.OK &&
            results[0]
          ) {
            const place = results[0];
            if (place.photos && place.photos.length > 0) {
              const photo = place.photos[0];
              const imageUrl = photo.getUrl({
                maxWidth: 2000,
                maxHeight: 2000,
              });

              if (imageUrl) {
                this.merchantImage = imageUrl;
                // Store in cache for future use
                storeMerchantImageInCache(merchantKey, imageUrl);
              } else {
                this.merchantImage = this.getCategoryImage(this.category);
              }
            }
          }
          resolve(); // resolve whether image is set or not
        });
      });
    },
    onImageLoad() {
      this.imageLoaded = true;
    },
    onImageError() {
      this.imageError = true;
      this.imageLoaded = false;
    },
    getCategoryImage(category) {
      return (
        this.categoryImages[category] || this.categoryImages["Food & Beverage"]
      );
    },
    async handleClick() {
      const dealRef = doc(db, "Deal", this.dealId);
      await updateDoc(dealRef, {
        clickCount: increment(1),
      });
      this.goToDealGroups();
    },
    goToDealGroups() {
      this.$router.push({
        path: "/ViewGroup",
        query: { dealId: this.dealId },
      });
    },
  },
};
</script>

<style scoped>
#dealCard {
  background-color: #f3f3f3;
  border-radius: 15px;
  padding: 20px 30px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

#dealCard:hover {
  transform: scale(1.01);
}

.merchant-image {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  object-fit: cover;
  margin-right: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  align-self: center;
}

.fallback-image {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  object-fit: contain;
  margin-right: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  align-self: center;
}

#info1 {
  display: flex;
  flex-direction: row;
  gap: 10px;
}

#info2 {
  text-align: right;
}

#distance,
#remainingTime {
  font-style: italic;
}

:hover {
  cursor: pointer;
}
</style>
