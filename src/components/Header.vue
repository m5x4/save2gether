<template>
  <header class="app-header">
    <div class="header-content" v-if="isSimpleHeader">
      <img
        src="@/assets/save2gether_logo.png"
        alt="Logo"
        class="logo centered"
      />
    </div>

    <div class="header-content" v-else>
      <!-- Full header for logged-in users -->
      <div class="left-section">
        <img
          src="@/assets/save2gether_logo.png"
          alt="Save2Gether Logo"
          class="logo"
          @click="goToHome"
        />
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search..."
          class="search-input"
        />
        <button class="header-btn" @click="handleSearch">
          <i class="fa-solid fa-magnifying-glass"></i>
          <!-- <span class="tooltip">Search Deals</span> -->
        </button>

        <button class="header-btn" @click="resetSearch">
          <i class="fa-solid fa-rotate-left"></i>
          <!-- <span class="tooltip">Reset Search</span> -->
        </button>
      </div>

      <div class="right-section">
        <router-link to="/createDeal" class="header-btn">
          <i class="fas fa-plus-circle"></i>
          <span class="tooltip">Create Deal</span>
        </router-link>

        <router-link to="/chat" class="header-btn">
          <i class="fas fa-envelope"></i>
          <span class="tooltip">Chat</span>
        </router-link>

        <router-link to="/ProfilePage" class="header-btn">
          <i class="fas fa-user"></i>
          <span class="tooltip">Profile</span>
        </router-link>
        <div class="header-btn" @click="logoutUser()">
          <i class="fas fa-sign-out-alt"></i>
          <span class="tooltip" style="margin-right: 50px">Logout</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { logoutUser } from "@/firebase/session";
import "@fortawesome/fontawesome-free/css/all.css";

export default {
  name: "HeaderVD",
  props: {
    query: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      searchQuery: this.query || "",
      isSimpleHeader: false,
    };
  },
  emits: ["apply-search", "reset-search"],
  methods: {
    handleSearch() {
      if (this.searchQuery.trim()) {
        this.$router.push({
          name: "SearchView",
          query: { q: this.searchQuery },
        });
      }
    },
    resetSearch() {
      this.searchQuery = "";
      this.$router.push("/HomeView");
    },
    goToHome() {
      this.$router.push("/HomeView");
    },
    logoutUser() {
      logoutUser()
        .then(() => {
          this.$router.push("/");
          // console.log("User logged out successfully");
        })
        .catch((error) => {
          console.error("Error logging out:", error);
        });
    },
    checkRoute() {
      const simpleRoutes = ["/", "/login", "/signup"];
      this.isSimpleHeader = simpleRoutes.includes(this.$route.path);
    },
  },
  watch: {
    $route() {
      this.checkRoute();
    },
  },
  mounted() {
    this.checkRoute(); // set initial state when header mounts
  },
};
</script>

<style scoped>
.app-header {
  background-color: #17334b;
  color: white;
  padding: 10px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: auto;
  padding: 0 30px;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.right-section {
  display: flex;
  align-items: center;
  gap: 30px;
}

.logo {
  height: 70px;
  width: auto;
  object-fit: contain;
  cursor: pointer;
}

.search-input {
  padding: 10px 16px;
  margin: 0px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 10px;
  width: 250px;
  outline: none;
  background-color: #f0f0f0;
  color: #333;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  border-color: #17334b;
}

.header-btn {
  background-color: transparent;
  color: white;
  border: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
  text-decoration: none;
  font-size: 1.3em;
  position: relative;
}

.header-btn:hover {
  transform: scale(1.1);
}

.tooltip {
  visibility: hidden;
  width: 80px;
  background-color: rgba(0, 0, 0, 0.75);
  color: #fff;
  text-align: center;
  border-radius: 5px;
  padding: 5px;
  position: absolute;
  z-index: 1;
  bottom: -150%;
  /* left: 50%; */
  /* margin-left: -50px; */
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.7em;
}

.header-btn:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

.logo.centered {
  margin: 0 auto;
  display: block;
}
</style>
