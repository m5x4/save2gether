<template>
  <div>
    <button @click="toggleDropdown" id="sort">
      {{ currentCriteria }}
      <span class="arrow" v-if="showDropdown">&#9660;</span>
    </button>
    <div v-if="showDropdown" class="dropdown">
      <button @click="sortDeals('name')">By Name</button>
      <button @click="sortDeals('distance')">By Distance</button>
      <button @click="sortDeals('expiry')">By Expiry</button>
      <button @click="sortDeals('newest')">By Newest</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showDropdown: false,
      currentCriteria: "Sort", // Default text for the button
    };
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    sortDeals(criteria) {
      if (criteria === "name") {
        this.currentCriteria = "Sort: Name";
      } else if (criteria === "distance") {
        this.currentCriteria = "Sort: Distance";
      } else if (criteria === "expiry") {
        this.currentCriteria = "Sort: Expiry";
      } else if (criteria === "newest") {
        this.currentCriteria = "Sort: Newest";
      }
      this.$emit("sort-deals", criteria); // Emit the selected criteria
      this.showDropdown = false; // Close dropdown after selection
    },
  },
};
</script>

<style scoped>
#sort {
  background-color: #2a4a6a;
  color: white;
  padding: 10px 30px;
  border-radius: 10px;
  border: none;
  box-shadow: none;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
}

#sort:hover {
  background-color: #1a2e3f;
  transform: scale(1.05); /* Slight scale effect */
}

.dropdown {
  position: absolute;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-top: 5px;
  z-index: 10;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); /* Add shadow for depth */
  animation: fade-in 0.2s; /* Animation for dropdown */
}

.dropdown button {
  display: block;
  width: 100%;
  padding: 10px;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
}

.dropdown button:hover {
  background-color: #f0f0f0; /* Light background on hover */
}

/* Animation for dropdown */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
