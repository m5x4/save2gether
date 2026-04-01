<template>
  <div id="map"></div>
</template>

<script>
import { Loader } from "@googlemaps/js-api-loader";

export default {
  props: {
    location: String, // Location from parent
    apiKey: String, // API key from parent
  },
  data() {
    return {
      map: null,
      marker: null,
    };
  },
  async mounted() {
    await this.loadMap();
  },
  watch: {
    location(newLocation) {
      if (newLocation) {
        this.updateMap(newLocation);
      }
    },
  },
  methods: {
    async loadMap() {
      const loader = new Loader({
        apiKey: this.apiKey,
        version: "weekly",
        libraries: ["places"],
      });

      await loader.load();
      this.map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 1.3521, lng: 103.8198 }, // Default to Singapore
        zoom: 12,
      });
    },
    async updateMap(location) {
      const geocoder = new google.maps.Geocoder();
      geocoder.geocode({ address: location }, (results, status) => {
        if (status === "OK") {
          const position = results[0].geometry.location;
          this.map.setCenter(position);

          if (this.marker) {
            this.marker.setMap(null);
          }

          this.marker = new google.maps.Marker({
            map: this.map,
            position: position,
            title: location,
          });
        } else {
          alert("Location not found: " + status);
        }
      });
    },
  },
};
</script>

<style>
#map {
  width: 600px;
  height: 400px;
}
</style>
