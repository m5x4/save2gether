<template>
  <div class="popup-overlay">
    <div class="popup review-popup">
      <div class="review-header">
        <h3>Leave a Review</h3>
        <div class="nav">
          <button
            v-for="member in groupMembers"
            :key="member.id"
            @click="activeMember = member.id"
            :class="{ active: activeMember === member.id }"
          >
            {{ member.fullname }}
          </button>
        </div>
      </div>

      <div class="review-body" v-if="activeMember">
        <textarea
          v-model="reviews[activeMember]"
          placeholder="Write a review..."
        />
        <div class="stars">
          <span
            v-for="star in 5"
            :key="star"
            @click="rateMember(activeMember, star)"
            :class="{ selected: star <= ratings[activeMember] }"
            >★</span
          >
        </div>

        <div class="review-footer">
          <button class="cancel-btn" @click="$emit('close')">Cancel</button>
          <button class="submit-btn" @click="submitReview">Submit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { db, doc } from "@/firebase/firebase";
import {
  getChatUsers,
  addReview,
  extractDealAndGroupIdFromChatId,
  closeGroup,
} from "@/firebase/firestore";

export default {
  props: {
    chatId: {
      type: String,
      required: true,
    },
    currentUserId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      groupMembers: [],
      activeMember: null,
      ratings: {},
      reviews: {},
    };
  },
  async mounted() {
    await this.loadGroupMembers();
  },
  methods: {
    async loadGroupMembers() {
      try {
        const users = await getChatUsers(this.chatId); // iterate through the users

        if (!users || users.length === 0) return;

        for (const user of users) {
          if (user.id === this.currentUserId) continue;

          this.groupMembers.push({
            id: user.id,
            fullname: `${user.firstName} ${user.lastName}`,
          });
          this.ratings[user.id] = 0;
          this.reviews[user.id] = "";
        }

        if (this.groupMembers.length > 0) {
          this.activeMember = this.groupMembers[0].id;
        }
      } catch (err) {
        console.error("Error loading group members:", err);
      }
    },
    async submitReview() {
      const reviewerRef = doc(db, "User", this.currentUserId);

      for (const member of this.groupMembers) {
        const memberId = member.id;

        if (this.ratings[memberId] === 0 || !this.reviews[memberId]?.trim()) {
          alert(`Please rate and review ${member.fullname} before submitting.`);
          this.activeMember = memberId;
          return;
        }
      }

      try {
        const users = await getChatUsers(this.chatId);

        for (const member of this.groupMembers) {
          const user = users.find((u) => u.id === member.id);
          if (!user) continue;

          await addReview(
            // used the correct parameters for addReview
            user.id,
            reviewerRef,
            this.reviews[user.id],
            this.ratings[user.id]
          );
        }

        const { dealId, groupId } = await extractDealAndGroupIdFromChatId(
          this.chatId
        );
        if (!dealId || !groupId) {
          console.error("Missing dealId or groupId for chatId:", this.chatId);
          return;
        }

        await closeGroup(dealId, groupId);

        alert("All reviews submitted.");
        this.$emit("submitted");
        this.$emit("close");
      } catch (err) {
        console.error("Error submitting reviews:", err);
        alert("Something went wrong.");
      }
    },

    // Helper functions

    rateMember(memberId, rating) {
      this.ratings[memberId] = rating;
    },
  },
};
</script>

<style scoped>
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}
.popup {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
}
.nav {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 10px;
}
.nav button.active {
  font-weight: bold;
  border-bottom: 2px solid #4caf50;
}
textarea {
  width: 100%;
  height: 100px;
  margin: 10px 0;
  padding: 8px;
  border: 1px solid #ddd;
}
.stars {
  text-align: center;
  font-size: 24px;
}
.stars .selected {
  color: gold;
}
.review-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}
</style>

<!-- <ReviewModal :chatId="chatId" :currentUserId="userId" @close="showReviewPopup = false" /> -->
