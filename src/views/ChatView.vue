<template>
  <Header></Header>
  <div
    class="chat-container"
    :class="{ dimmed: showLeavePopup || showReviewPopup }"
  >
    <aside class="sidebar">
      <input
        type="text"
        v-model="searchInput"
        @input="onSearchInput"
        placeholder="Search for a chat"
        class="search-box"
      />
      <div class="chat-list">
        <ChatCard
          v-for="chat in filteredChats"
          :key="chat.id"
          :chatId="chat.id"
          :refreshKey="chat.refreshKey"
          @load-chat-window="loadChatWindow($event)"
        />
      </div>
    </aside>

    <ChatWindow
      :chatId="selectedChatId"
      :userId="userID"
      @leave="showLeavePopup = true"
      @complete="showReviewPopup = true"
      @left-chat="handleUserLeftChat"
      @chat-updated="refreshChatCard"
    />

    <div v-if="showLeavePopup" class="popup-overlay">
      <div class="popup leave-popup">
        <h3>Leave Group</h3>
        <p>Are you sure you want to leave the group?</p>
        <div class="popup-actions">
          <button class="cancel-btn" @click="showLeavePopup = false">
            Cancel
          </button>
          <button class="confirm-btn" @click="handleUserLeftChat">
            Yes, Leave
          </button>
        </div>
      </div>
    </div>

    <div v-if="showReviewPopup" class="popup-overlay">
      <div class="popup review-popup">
        <div class="review-header">
          <h3>Leave a Review</h3>
          <div class="nav">
            <button
              v-for="member in groupMembers"
              :key="member"
              @click="activeMember = member"
              :class="{ active: activeMember === member }"
            >
              {{ member }}
            </button>
          </div>
        </div>
        <div class="review-body">
          <p>Review for {{ activeMember }}:</p>
          <textarea
            v-model="reviews[activeMember]"
            placeholder="Write a review..."
          ></textarea>
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
            <button class="cancel-btn" @click="showReviewPopup = false">
              Cancel
            </button>
            <button class="submit-btn" @click="submitReview">Submit</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChatCard from "@/components/ChatCard.vue";
import ChatWindow from "@/components/ChatWindow.vue";
import Header from "@/components/Header.vue";
import {
  getUserChats,
  getChat,
  getGroupLeaderProfilePic,
} from "@/firebase/firestore.js";
import { auth } from "../firebase/firebase.js";
import { onAuthStateChanged } from "firebase/auth";

export default {
  components: {
    ChatCard,
    ChatWindow,
    Header,
  },
  data() {
    return {
      userID: auth.currentUser?.uid || null,
      selectedChatId: null,
      showLeavePopup: false,
      showReviewPopup: false,
      activeMember: "Charlie",
      groupMembers: ["Charlie", "Betty"],
      ratings: { Charlie: 0, Betty: 0 },
      reviews: { Charlie: "", Betty: "" },
      chatIds: [],
      chats: [],
      searchInput: "",
    };
  },
  computed: {
    searchQuery() {
      return this.searchInput;
    },
    filteredChats() {
      // console.log("Computing filteredChats with query:", this.searchQuery);
      if (!this.searchQuery || !this.searchQuery.trim()) {
        // console.log("No search query, returning all chats:", this.chats);
        return this.chats;
      }

      const query = this.searchQuery.toLowerCase();
      const filtered = this.chats.filter((chat) => {
        //console.log("chat name: ", chat.name);
        const nameMatch = chat.name && chat.name.toLowerCase().includes(query);
        return nameMatch;
      });

      //console.log("Filtered results:", filtered);
      return filtered;
    },
  },
  watch: {
    searchInput(newVal) {
      // console.log("searchInput changed:", newVal);
    },
  },
  async created() {
    onAuthStateChanged(auth, async (user) => {
      if (user) {
        this.userID = user.uid;
        await this.fetchChats();

        if (this.$route.query.chatId) {
          this.loadChatWindow(this.$route.query.chatId);
        }
      } else {
        console.error("No authenticated user found");
      }
    });
  },
  watch: {
    "$route.query.chatId"(newChatId) {
      if (newChatId) {
        this.loadChatWindow(newChatId);
      } else {
        this.selectedChatId = null;
      }
    },
  },
  methods: {
    async fetchChats() {
      try {
        const chatIds = await getUserChats(this.userID);
        this.chatIds = chatIds;
        // console.log("chatIds: ", this.chatIds);

        // Create a temporary array to store the chat data
        const chatDataArray = [];

        // Fetch detailed chat info for each chat ID
        for (const chatId of chatIds) {
          try {
            const chatData = await getChat(chatId);
            chatDataArray.push({
              id: chatId,
              name: chatData.chatName || `Chat ${chatId.substring(0, 5)}...`,
            });
          } catch (error) {
            console.error(`Error fetching chat ${chatId}:`, error);
            chatDataArray.push({
              id: chatId,
              name: `Chat ${chatId.substring(0, 5)}...`,
            });
          }
        }

        // Set the chats array at once to ensure reactivity
        this.chats = chatDataArray;
        // console.log("All chats loaded:", this.chats);
      } catch (error) {
        console.error("There is an error fetching chats: ", error);
      }
    },
    async handleUserLeftChat(chatId) {
      this.selectedChatId = null;
      this.chats = this.chats.filter((chat) => chat.id !== chatId);
    },
    async refreshChatCard(chatId) {
      try {
        const chatData = await getChat(chatId);
        const avatar = await getGroupLeaderProfilePic(chatId); // Assume this returns a URL

        const index = this.chats.findIndex((c) => c.id === chatId);
        if (index !== -1) {
          this.chats.splice(index, 1, {
            ...this.chats[index],
            name: chatData.chatName || `Chat ${chatId.substring(0, 5)}...`,
            avatar,
            refreshKey: Date.now(), // force re-render
          });
        }

        // console.log("Chat card updated for:", chatId);
      } catch (err) {
        console.error("Failed to refresh chat card:", err);
      }
    },

    loadChatWindow(chatId) {
      this.selectedChatId = chatId;
    },
    onSearchInput(event) {
      // console.log("Search input changed:", this.searchInput);
    },
  },
};
</script>

<style>
.chat-container {
  display: flex;
  height: calc(100vh - 90px); /* Adjust for header height */
  margin-top: 90px; /* Add space for the header */
  font-family: serif;
  overflow: hidden; /* Prevent scrolling of the container itself */
  position: fixed; /* Fix the position */
  width: 100%; /* Full width */
  top: 0; /* Align to top */
  left: 0; /* Align to left */
}

.sidebar {
  width: 25%;
  background: #f1f1f1;
  padding: 20px;
  font-family: serif;
  font-size: large;
  line-height: 1.5;
  white-space: normal;
  overflow-y: auto; /* Allow scrolling in sidebar */
  height: 100%;
}

.search-box {
  width: 90%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-family: serif;
}

.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-box-container {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  /* Ensures the chat box stays at the bottom */
  padding: 10px;
}

.chat-box {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  font-family: serif;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.leave-popup {
  width: 300px;
}

.popup-actions {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.popup-actions button {
  margin: 0 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  background: #f1f1f1;
  color: #333;
}

.confirm-btn,
.submit-btn {
  background: #4caf50;
  color: white;
}

.review-popup {
  width: 400px;
}

.review-header {
  margin-bottom: 15px;
}

.nav {
  display: flex;
  justify-content: center;
  margin-top: 10px;
  border-bottom: 1px solid #eee;
}

.nav button {
  margin: 5px;
  padding: 8px 12px;
  border: none;
  background: none;
  cursor: pointer;
}

.nav .active {
  font-weight: bold;
  border-bottom: 2px solid #4caf50;
}

.review-body {
  text-align: left;
}

.review-body textarea {
  width: 95%;
  height: 100px;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
}

.stars {
  text-align: center;
  margin: 15px 0;
}

.stars span {
  font-size: 30px;
  cursor: pointer;
  color: #ddd;
  transition: color 0.2s;
}

.stars .selected {
  color: #ffd700;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.review-footer button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
