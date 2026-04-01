<template>
  <div class="create-section">
    <div id="create" @click="showForm = !showForm">
      <span>Create a New Group</span>
      <span class="arrow" :class="{ 'arrow-up': showForm }">▼</span>
    </div>

    <transition name="slide">
      <div v-if="showForm" class="form-container">
        <div class="form-layout">
          <!-- Left side: User's Group -->
          <div class="user-group">
            <div class="group-header">
              <h3>{{ dealName }} Group</h3>
            </div>
            <div class="group-members">
              <div class="member-card">
                <img
                  :src="userData?.profilePicURL || '/src/assets/avatar.png'"
                  alt="Profile"
                  class="member-pic"
                />
                <div class="member-info">
                  <div id="nameRating">
                    <h4>{{ userData?.firstName }} {{ userData?.lastName }}</h4>
                    <div id="stars">
                      <span v-for="index in 5" :key="index" id="starIcon">
                        <component :is="getStarComponent(index)" />
                      </span>
                    </div>
                  </div>
                  <span class="leader-badge">Leader</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Right side: Create Group Form -->
          <div class="group-form">
            <form @submit.prevent="handleSubmit">
              <div class="form-group">
                <label for="date">Proposed Date:</label>
                <input type="date" id="date" v-model="formData.date" required />
              </div>
              <div class="form-group">
                <label for="time">Proposed Time:</label>
                <input type="time" id="time" v-model="formData.time" required />
              </div>
              <div class="form-buttons">
                <button type="submit" class="submit-btn">Create Group!</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { auth } from "@/firebase/firebase.js";
import {
  getUser,
  addGroup,
  addGroupMember,
  addChat,
  getReviews,
} from "@/firebase/firestore.js";
import { doc } from "firebase/firestore";
import { db } from "@/firebase/firebase.js";
import { onAuthStateChanged } from "firebase/auth";
import EmptyStar from "@/assets/icons/EmptyStar.vue";
import FullStar from "@/assets/icons/FullStar.vue";
import HalfStar from "@/assets/icons/HalfStar.vue";

export default {
  name: "CreateGroupButton",
  props: {
    dealId: {
      type: String,
      required: true,
    },
    dealName: {
      type: String,
      required: true,
    },
  },
  components: {
    FullStar,
    HalfStar,
    EmptyStar,
  },
  data() {
    return {
      showForm: false,
      formData: {
        date: "",
        time: "",
        groupSize: "",
      },
      userData: null,
      leaderRating: 0,
    };
  },
  async created() {
    // Set up auth state listener
    onAuthStateChanged(auth, async (user) => {
      if (user) {
        // Fetch user data from Firestore
        this.userData = await getUser(user.uid);
        // console.log("User data loaded:", this.userData);
        // fetch ratings
        await this.getReviews();
      } else {
        this.userData = null;
        // console.log("No user logged in");
      }
    });
  },
  methods: {
    async handleSubmit() {
      const userRef = doc(db, "User", this.userData.id);
      const dealRef = doc(db, "Deal", this.dealId);
      const proposedDateTime = new Date(
        `${this.formData.date}T${this.formData.time}`
      );
      const groupRef = await addGroup(dealRef.id, false, proposedDateTime);

      await addGroupMember(this.dealId, groupRef.id, userRef, true);
      await addChat(`${this.dealName} Deal Chat`, groupRef); // change name of chat if needed

      // Handle form submission here
      // console.log("Form submitted:", this.formData);
      alert("Group created");
      this.showForm = false;
      this.formData = {
        date: "",
        time: "",
        groupSize: "",
      };
      window.location.reload();
    },
    async getReviews() {
      // console.log("Fetching reviews for user:", this.userData.id);
      const reviews = await getReviews(this.userData.id);
      // console.log("Reviews Length:", reviews.length);
      if (reviews.length > 0) {
        const totalRating = reviews.reduce(
          (sum, review) => sum + review.rating,
          0
        );
        this.leaderRating = parseFloat(
          (totalRating / reviews.length).toFixed(1)
        );
      }
    },
    getStarComponent(index) {
      if (this.leaderRating >= index) return "FullStar";
      if (this.leaderRating >= index - 0.5) return "HalfStar";
      return "EmptyStar";
    },
  },
};
</script>

<style scoped>
.create-section {
  margin-bottom: 20px;
}

/* Create Button Styles */
#create {
  background-color: #f3f3f3;
  border-radius: 15px;
  padding: 20px 40px;
  cursor: pointer;
  text-align: center;
  border: none;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.3s ease;
  position: relative;
  z-index: 1;
  box-sizing: border-box;
}

#create:hover {
  background-color: #d3d3d3;
}

.arrow {
  transition: transform 0.3s ease;
}

.arrow-up {
  transform: rotate(180deg);
}

/* Form Container Styles */
.form-container {
  background-color: white;
  padding: 20px 30px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-top: 10px;
  border: 1px solid #ddd;
  width: 100%;
  box-sizing: border-box;
}

.form-layout {
  display: flex;
  width: 100%;
  gap: 20px;
  justify-content: space-between;
  align-items: flex-start;
}

/* User Group Styles */
.user-group {
  width: 30%;
  /* background-color: #f8f9fa; */
  border-radius: 10px;
  padding: 15px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
  font-size: 1.1em;
}

.group-header h3 {
  margin: 0;
  color: #333;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  /* font-size: 1.1em; */
}

.member-pic {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info h4 {
  margin: 0;
  font-size: 0.95em;
  color: #333;
}

.leader-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8em;
}

/* Form Styles */
.group-form {
  width: 300px;
  padding-top: 20px;
}

.form-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.form-group label {
  font-weight: bold;
  margin-right: 10px;
  width: 40%;
}

.form-group input {
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  width: 60%;
}

.form-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Button Styles */
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  background-color: #17334b;
  color: white;
}

.submit-btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

#stars {
  padding-top: 5px;
}

#starIcon {
  width: 20px;
  height: 20px;
  display: inline-block;
  margin-right: 2px;
}

#nameRating {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

/* Animation */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0;
  margin: 0;
}
</style>
