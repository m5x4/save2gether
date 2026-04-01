<template>
  <!-- on click leads to a pop up to choose fields -->
  <button @click="showModal = true" id="filter">
    {{ isActive ? "Active Filter" : "Filter" }}
  </button>

  <div v-if="showModal" id="filter-modal-overlay" @click.self="closeModal">
    <div class="filter-modal">
      <h3>Filter Deals</h3>
      <label>
        Valid Until:
        <input type="datetime-local" v-model="filters.validUntil" />
      </label>

      <label>
        Maximum Distance Away (km):
        <input type="number" v-model="filters.maxDistance" />
      </label>
      <div class="modal-buttons">
        <button @click="applyFilters" id="apply-button">Apply</button>
        <button @click="resetFilters" id="reset-button">Reset</button>
        <button @click="closeModal" id="cancel-button">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showModal: false,
      filters: {
        validUntil: null,
        maxDistance: null,
      },
    };
  },
  computed: {
    isActive() {
      return Object.values(this.filters).some(
        (value) => value !== null && value !== ""
      );
    },
  },
  emits: ["apply-filters"],
  methods: {
    applyFilters() {
      this.$emit("apply-filters", this.filters);
      this.closeModal();
    },
    resetFilters() {
      this.filters = {
        validUntil: null,
        maxDistance: null,
      };
      this.$emit("apply-filters", this.filters);
      this.closeModal();
    },
    closeModal() {
      this.showModal = false;
    },
  },
};
</script>

<style scoped>
#filter {
  background-color: #2a4a6a;
  color: white;
  padding: 10px 30px;
  border-radius: 10px;
  border: none;
  box-shadow: none;
  cursor: pointer;
}

#filter:hover {
  background-color: #1a2e3f;
  transform: scale(1.05); /* Slight scale effect */
}

#filter-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5); /* Dark overlay */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.filter-modal {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.modal-buttons button {
  padding: 5px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

#apply-button {
  background-color: #4caf50;
  color: white;
}

#reset-button {
  background-color: #818181;
  color: white;
}

#cancel-button {
  background-color: #f44336;
  color: white;
}
</style>
