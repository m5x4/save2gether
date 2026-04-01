<template>
  <Header></Header>
  <div v-if="userData" id="userInfo">
    <img
      id="profilePic"
      :src="userData.profilePicURL || '/src/assets/avatar.png'"
      alt="Profile"
    />
    <div id="userDetails">
      <div id="nameRatingSection">
        <h2>{{ userData.firstName + " " + userData.lastName }}</h2>
        <div id="stars">
          <span v-for="index in 5" :key="index" id="starIcon">
            <component :is="getStarComponent(index)" />
          </span>
        </div>
      </div>
      <p>{{ "Joined since: " + formatJoinDate(joinDateTime) }}</p>
      <button v-if="isOwnProfile" @click="showEditProfile">Edit Profile</button>
    </div>
  </div>
  <div id="infoSection">
    <div id="tabs">
      <button
        :class="{ activeTab: activeTab === 'deals' }"
        @click="activeTab = 'deals'"
      >
        Deal History
      </button>
      <button
        v-if="isOwnProfile"
        :class="{ activeTab: activeTab === 'reviews' }"
        @click="activeTab = 'reviews'"
      >
        Your Profile Reviews
      </button>
      <button
        v-else
        :class="{ activeTab: activeTab === 'reviews' }"
        @click="activeTab = 'reviews'"
      >
        Profile Reviews
      </button>
      <button
        :class="{ activeTab: activeTab === 'analytics' }"
        @click="activeTab = 'analytics'"
      >
        User Analytics Dashboard
      </button>
    </div>
    <div id="cards">
      <div v-if="activeTab === 'deals'" id="dealHistory">
        <h2>Deal History Tab</h2>
        <ExistingGroupCards
          v-for="(group, index) in existingGroups"
          :key="index"
          :dealName="group.dealName"
          :groupLeader="group.groupLeader"
          :proposedDateTime="formatDate(group.proposedDateTime)"
          :numFilled="group.numFilled"
          :groupSize="group.groupSize"
          :remainingTime="group.remainingTime"
        />
        <OldGroupCards
          v-for="(group, index) in oldGroups"
          :key="index"
          :dealName="group.dealName"
          :groupLeader="group.groupLeader"
          :proposedDateTime="formatDate(group.proposedDateTime)"
          :numFilled="group.numFilled"
          :groupSize="group.groupSize"
        />
      </div>

      <div v-if="activeTab === 'reviews'" id="reviews">
        <h2 v-if="isOwnProfile">Your Reviews</h2>
        <h2 v-else>Profile Reviews</h2>
        <p v-if="reviews.length === 0">No reviews available for this user.</p>
        <ReviewCard
          v-for="review in reviews"
          :key="review.id"
          :reviewerName="review.reviewerName"
          :content="review.content"
          :rating="review.rating"
        />
      </div>

      <div v-if="activeTab === 'analytics'" id="analytics">
        <h2>User Analytics Dashboard</h2>
        <UserAnalyticsDashboard :userId="profileUserId" />
      </div>
    </div>
  </div>
  <!-- Add EditProfile modal -->
  <EditProfile
    v-if="isEditProfileVisible"
    :user="userData"
    @close="hideEditProfile"
    @profile-updated="handleProfileUpdated"
  />
</template>

<script>
import EmptyStar from "@/assets/icons/EmptyStar.vue";
import FullStar from "@/assets/icons/FullStar.vue";
import HalfStar from "@/assets/icons/HalfStar.vue";
import ExistingGroupCards from "@/components/ExistingGroupCards.vue";
import OldGroupCards from "@/components/OldGroupCards.vue";
import ReviewCard from "@/components/ReviewCard.vue";
import EditProfile from "../components/EditProfileModal.vue";
import UserAnalyticsDashboard from "@/components/UserAnalyticsDashboard.vue";
import Header from "@/components/Header.vue";
import { auth } from "@/firebase/firebase.js";
import { onAuthStateChanged } from "firebase/auth";
import {
  getUser,
  getDeal,
  getReviews,
  getGroups,
  getGroupMembers,
} from "@/firebase/firestore.js";

export default {
  data() {
    return {
      userData: null,
      profileUserId: null,
      activeTab: "deals", // default tab when load
      reviews: [],
      oldGroups: [],
      existingGroups: [],
      averageRating: 0,
      isOwnProfile: false,
      isEditProfileVisible: false,
      authUser: null,
      unsubscribeAuth: null,
    };
  },
  components: {
    ReviewCard,
    OldGroupCards,
    ExistingGroupCards,
    FullStar,
    HalfStar,
    EmptyStar,
    EditProfile,
    UserAnalyticsDashboard,
    Header,
  },
  async created() {
    // Set up auth state listener
    this.unsubscribeAuth = onAuthStateChanged(auth, async (user) => {
      if (user) {
        this.authUser = user;
        // Get user id from route params or take current user logged in id
        this.profileUserId = this.$route.params.userId || user.uid;
        this.isOwnProfile = this.profileUserId === user.uid;

        // Get user data
        if (this.profileUserId) {
          this.userData = await getUser(this.profileUserId);
          this.joinDateTime = this.userData.joinDateTime;
          // Fetch user reviews
          await this.fetchReviews();
          // Fetch old and existing groups for deal history tab
          await this.fetchDealHistory();
        }
      } else {
        // If no user is logged in, redirect to login page
        this.$router.push("/");
      }
    });
  },
  beforeUnmount() {
    // Clean up auth state listener
    if (this.unsubscribeAuth) {
      this.unsubscribeAuth();
    }
  },
  methods: {
    formatCreationDate(timestamp) {
      try {
        const date = new Date(timestamp);
        const options = {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          timeZone: "Asia/Singapore",
        };
        const formattedDate = date.toLocaleDateString("en-SG", options);
        return formattedDate;
      } catch (error) {
        console.error("Error formatting date: ", error);
        return "Invalid Date";
      }
    },
    formatDate(timestamp) {
      try {
        const date = new Date(timestamp.seconds * 1000);
        const formattedDate = date.toLocaleString("en-SG", {
          day: "2-digit",
          month: "2-digit",
          year: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hour12: true,
        });
        return formattedDate;
      } catch (error) {
        console.error("There is an error converting time: ", error);
        return "System unable to fetch Date";
      }
    },
    formatJoinDate(timestamp) {
      try {
        const date = new Date(timestamp.seconds * 1000);
        const formattedDate = date.toLocaleString("en-SG", {
          day: "2-digit",
          month: "2-digit",
          year: "2-digit",
        });
        return formattedDate;
      } catch (error) {
        console.error("There is an error converting time: ", error);
        return "System unable to fetch Date";
      }
    },
    calculateRemainingTime(timestamp) {
      const now = new Date();
      const endTime = new Date(timestamp);
      const timeDiff = endTime - now;
      if (timeDiff <= 0) {
        return "Happening Now";
      }
      const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
      const hours = Math.floor(
        (timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
      );
      const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
      let result = "";
      if (days > 0) {
        result += `${days} days `;
      }
      if (hours > 0) {
        result += `${hours} hours `;
      }
      if (minutes > 0) {
        result += `${minutes} minutes`;
      }
      return result.trim();
    },
    async fetchReviews() {
      try {
        const reviews = await getReviews(this.profileUserId);
        const processReviews = await Promise.all(
          reviews.map(async (review) => {
            const reviewer = await getUser(review.reviewerRef.id);
            return {
              ...review,
              reviewerName: reviewer
                ? `${reviewer.firstName} ${reviewer.lastName}`
                : "Unknown User",
            };
          })
        );
        this.reviews = processReviews;
        // calculate average rating for user
        if (processReviews.length > 0) {
          const totalRating = processReviews.reduce(
            (sum, review) => sum + review.rating,
            0
          );
          this.averageRating = parseFloat(
            (totalRating / processReviews.length).toFixed(1)
          );
        } else {
          this.averageRating = 0;
        }
      } catch (error) {
        console.error("Error fetching reviews: ", error);
      }
    },
    // fetch the old and existing groups for the deal history tab
    async fetchDealHistory() {
      const oldGroupsList = [];
      const existingGroupsList = [];
      // loop through all deals
      for (const dealRef of this.userData.deals || []) {
        const dealId = dealRef.id;
        // get deal details
        const dealDoc = await getDeal(dealId);
        const dealName = dealDoc.dealName;
        const groupSize = dealDoc.numRequired.toString();

        const groups = await getGroups(dealId);
        // loop through all groups in the deal
        for (const group of groups) {
          const groupMembers = await getGroupMembers(dealId, group.id);
          const isMember = groupMembers.some(
            (member) => member.user?.id === this.profileUserId
          );
          // if do not have user in group, continue
          if (!isMember) {
            continue;
          }
          // find leader info
          const leaderMember = groupMembers.find((member) => member.isLeader);
          let leaderName = "Unknown";
          if (leaderMember?.user) {
            const leaderDetails = await getUser(leaderMember.user.id);
            if (leaderDetails) {
              leaderName = `${leaderDetails.firstName} ${leaderDetails.lastName}`;
            }
          }
          const remainingTime = this.calculateRemainingTime(
            group.proposedDateTime.seconds * 1000
          );
          const groupInfo = {
            dealName,
            groupLeader: leaderName,
            proposedDateTime: group.proposedDateTime,
            numFilled: groupMembers.length.toString(),
            groupSize,
            remainingTime,
          };
          // allocate to either old or existing groups
          if (group.isClosed) {
            oldGroupsList.push(groupInfo);
          } else {
            existingGroupsList.push(groupInfo);
          }
        }
      }
      this.oldGroups = oldGroupsList.sort(
        (a, b) => b.proposedDateTime.seconds - a.proposedDateTime.seconds
      ); // sort desc
      this.existingGroups = existingGroupsList.sort(
        (a, b) => a.proposedDateTime.seconds - b.proposedDateTime.seconds
      ); // sort asc
    },
    getStarComponent(index) {
      if (this.averageRating >= index) return "FullStar";
      if (this.averageRating >= index - 0.5) return "HalfStar";
      return "EmptyStar";
    },
    showEditProfile() {
      this.isEditProfileVisible = true;
    },
    hideEditProfile() {
      this.isEditProfileVisible = false;
    },
    async handleProfileUpdated() {
      // Refresh user data after profile update
      if (this.profileUserId) {
        this.userData = await getUser(this.profileUserId);
      }
      this.hideEditProfile();
    },
  },
};
</script>

<style scoped>
#userInfo {
  margin: 30px 60px;
  display: flex;
  align-items: center;
  gap: 20px;
}

#infoSection {
  margin: 0 60px;
  margin-top: 50px;
}

#userDetails h2 {
  margin-top: 5px;
  margin-bottom: 10px;
}

#userDetails p {
  margin-top: 10px;
  margin-bottom: 10px;
}

#userDetails button {
  background-color: #f3f3f3;
  border-radius: 5px;
  padding: 5px 20px;
  text-align: center;
  border: none;
  cursor: pointer;
  color: black;
}

#profilePic {
  width: 100px;
  height: 100px;
}

#tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

#tabs button {
  padding: 10px 20px;
  background-color: #d9d9d9;
  color: black;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

#tabs button.activeTab {
  background-color: #17334b;
  color: white;
}

#nameRatingSection {
  display: flex;
  align-items: center;
  gap: 20px;
}

#nameRatingSection h2 {
  margin: 0;
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

#analytics {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding-bottom: 20px;
}

#dealHistory {
  display: flex;
  flex-direction: column;
  padding-bottom: 20px;
}

#reviews {
  display: flex;
  flex-direction: column;
  padding-bottom: 20px;
}
</style>
