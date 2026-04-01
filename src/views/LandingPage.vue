<template>
  <Header />
  <div class="container">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-grid">
        <div class="hero-text">
          <h1>
            Find Deal Buddies, <br /><span class="highlight">Save2gether</span>
          </h1>
          <p>
            Save2gether connects you with compatible partners to share 1-for-1
            deals, group discounts, and other offers across food, retail,
            entertainment, and more.
          </p>
          <div class="deal-tags">
            <span class="deal-tag">1-for-1 Deals</span>
            <span class="deal-tag">Group Offers</span>
            <span class="deal-tag">Save Money</span>
            <span class="deal-tag">Meet New People</span>
          </div>
          <div class="hero-buttons">
            <button @click="checkUser('/HomeView')">Discover Deals</button>
            <button @click="navigate('/signup')">Create Account</button>
            <button @click="navigate('/login')">Login</button>
          </div>
        </div>

        <div class="hero-card">
          <div class="card-grid">
            <div class="main-card">
              <div class="card-tags">
                <span class="primary-tag">Food & Beverage</span>
              </div>
              <h3>Buy 1 Get 1 Free at Starbucks</h3>
              <p>541 Orchard Rd, #01-01A Liat Towers, Singapore 238881</p>
            </div>

            <div class="mini-card">
              <span class="entertainment-tag">Entertainment</span>
              <h3>4-for-2 Concert Tickets</h3>
            </div>

            <div class="mini-card">
              <span class="retail-tag">Retail</span>
              <h3>50% Off Second Item at H&M</h3>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="section">
      <h2>How <span style="color: #ade8ff">Save2gether</span> works</h2>
      <p style="font-size: 18px">
        Connect with like-minded deal hunters in just three simple steps
      </p>
      <div class="info-grid">
        <div class="info-card">
          <h3>Discover Deals</h3>
          <p>
            Browse available deals or post your own offers to find the perfect
            match.
          </p>
        </div>
        <div class="info-card">
          <h3>Join Group</h3>
          <p>Join an existing group or create a new group for an offer.</p>
        </div>
        <div class="info-card">
          <h3>Enjoy & Save</h3>
          <p>
            Arrange a time via the chat feature to meet up, redeem your deal
            together, and enjoy the savings!
          </p>
        </div>
      </div>
    </section>

    <!-- Categories Section -->
    <section class="categories-section">
      <div class="categories-head">
        <h1>Browse Deal Categories</h1>
        <p>We've got deals across all your favorite categories</p>
      </div>
      <div class="category-grid">
        <div
          @click="checkUser('/ViewDeal?category=Food+%26+Beverage')"
          class="category-card"
        >
          <img src="/src/assets/icons/food.png" alt="" />
          <h3>Food & Beverage</h3>
          <p>Coffees, meals, and more</p>
        </div>
        <div
          @click="checkUser('/ViewDeal?category=Lifestyle+%26+Fitness')"
          class="category-card"
        >
          <img src="/src/assets/icons/lifestyle.png" alt="" />
          <h3>Lifestyle & Fitness</h3>
          <p>Gym memberships, wellness, and more</p>
        </div>
        <div
          @click="checkUser('/ViewDeal?category=Travel+%26+Attractions')"
          class="category-card"
        >
          <img src="/src/assets/icons/travel.png" alt="" />
          <h3>Travel</h3>
          <p>Tours, activities, and experiences</p>
        </div>
        <div
          @click="checkUser('/ViewDeal?category=Retail')"
          class="category-card"
        >
          <img src="/src/assets/icons/retail.png" alt="" />
          <h3>Retail</h3>
          <p>Fashion, electronics, and more</p>
        </div>
        <div
          @click="checkUser('/ViewDeal?category=Games+%26+Entertainment')"
          class="category-card"
        >
          <img src="/src/assets/icons/games.png" alt="" />
          <h3>Entertainment</h3>
          <p>Game credits, concerts, and more</p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <h2>Ready to Start Saving?</h2>
      <p>Join users who are already sharing deals on Save2gether!</p>
      <button class="button" @click="checkUser('/HomeView')">
        Get Started Now
      </button>
    </section>
  </div>
</template>

<script>
import Header from "@/components/Header.vue";
import { checkAuthState } from "@/firebase/session.js";

export default {
  methods: {
    navigate(path) {
      this.$router.push(path);
    },
    async checkUser(path) {
      try {
        await checkAuthState();
        this.navigate(path);
      } catch (error) {
        alert("Please log in to browse available deals!");
      }
    },
  },
  components: { Header },
};
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: #f9fafb;
}
.hero-section {
  padding: 5rem 1rem;
  max-width: 75rem;
  margin: auto;
  /* width: 80%; */
}
.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
}
@media (min-width: 768px) {
  .hero-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.hero-text h1 {
  font-size: 2.25rem;
  font-weight: bold;
  color: black;
}
.highlight {
  color: #2a4a6a;
}
.hero-text p {
  color: #4b5563;
  font-size: 1.125rem;
}

.deal-tags {
  display: flex;
  gap: 1rem;
}
.deal-tag {
  background-color: #e5e7eb;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 0.875rem;
  color: #111827;
}

.hero-buttons {
  display: flex;
  /* buttons in a row */
  flex-direction: row;
  gap: 1rem;
  margin-top: 1rem;
}
.hero-buttons button,
.button {
  background-color: #2a4a6a;
  color: white;
  padding: 10px 30px;
  border-radius: 10px;
  border: none;
  box-shadow: none;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
}

.deal-tags span,
.hero-buttons button,
.info-card,
.category-card {
  transition: transform 0.3s ease;
}

.category-card {
  text-align: center;
}
.category-card img {
  width: 100px;
  height: 100px;
  object-fit: contain;
  border-radius: 0.5rem;
}
.hero-buttons button:hover,
.info-card:hover {
  transform: translateY(-0.25rem);
}

.category-card:hover {
  transform: translateY(-1.25rem);
  background-color: lightgrey;
}
.hero-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.card-grid {
  display: grid;
  gap: 1rem;
}
.main-card {
  grid-column: span 2;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
.mini-card {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
.primary-tag {
  /* background-color: rgba(59, 130, 246, 0.2); */
  color: #3b82f6;
}
.entertainment-tag {
  /* background-color: #bfdbfe; */
  color: #1d4ed8;
}
.retail-tag {
  /* background-color: #fde68a; */
  color: #92400e;
}
.section {
  padding: 4rem 1rem;
  /* max-width: 80rem; */
  margin: auto;
  text-align: center;
  background: url("@/assets/landing_bg.png") no-repeat center center;
  background-size: cover;
  /* color: white; */
  height: auto;
  text-align: center;
  color: white;
}
.section h2 {
  font-size: 1.875rem;
  font-weight: bold;
  color: white;
}
.info-grid {
  display: grid;
  gap: 2rem;
  margin-top: 2rem;
}
@media (min-width: 768px) {
  .info-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
.info-card {
  padding: 1.5rem;
  background: #edeef1;
  color: #111827;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
.categories-section {
  padding: 4rem 1rem;
  background: #f9fafb;
}

.categories-head {
  text-align: center;
  font-size: large;
}
.category-grid {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 2rem;
}
/* @media (min-width: 768px) {
  .category-grid {
    grid-template-columns: repeat(4, 1fr);
  }
} */
.category-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  align-items: center;
  width: 15%;
}
.cta-section {
  padding: 5rem 1rem;
  background: rgba(59, 130, 246, 0.1);
  text-align: center;
}
.cta-section h2 {
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
}
</style>

<!-- <template>
  <Header />
  <div class="landingcontainer">
    <img src="@/assets/save2gether_logo.png" alt="App Logo" class="logo" />

    <div class="auth-buttons">
      <button class="auth-button" @click="clickLogin">Login</button>
      <button class="auth-button" @click="clickSignUp">Sign Up</button>
    </div>
  </div>
</template>

<script setup>
import Header from "@/components/Header.vue";
import { useRouter } from "vue-router";

const router = useRouter();

// Handles regular login (e.g., email & password login)
const clickLogin = () => {
  console.log("Regular Login button clicked");
  router.push("/login");
};

// Handles sign-up logic (e.g., show a registration form)
const clickSignUp = () => {
  console.log("Sign Up button clicked");
  router.push("/signup");
};
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
}

.landingcontainer {
  display: flex;
  flex-direction: column;
  justify-content: center; /* Centers content vertically */
  align-items: center; /* Centers content horizontally */
  background: url("@/assets/landing_bg.png") no-repeat center center;
  background-size: cover;
  color: white;
  height: 100vh; /* Full-screen height */
  text-align: center;
}

.logo {
  width: 1000px;
  height: auto; /* Set a fixed size for consistency */
  margin-bottom: 20px; /* Adds spacing between logo and buttons */
  margin-top: -30px;
}

.auth-buttons {
  display: flex;
  flex-direction: column; /* Stack buttons vertically */
  align-items: center;
  gap: 30px; /* Space between buttons */
}

.auth-button {
  padding: 15px 40px;
  font-family: inherit;
  font-size: 18px;
  font-weight: bold;
  color: black;
  background-color: #f0f0f0;
  border: none;
  border-radius: 50px; /* Oval shape */
  cursor: pointer;
  transition: background-color 0.3s ease-in-out;
  width: 220px;
  height: 70px; /* Same width for both buttons */
  text-align: center;
}

.auth-button:hover {
  background-color: grey;
}
</style> -->
