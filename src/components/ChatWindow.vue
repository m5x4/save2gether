<template>
  <main class="chat-window">
    <div v-if="!chatId" class="no-chat-selected">
      <p>Select a chat to start messaging</p>
    </div>
    <template v-else>
      <header class="chat-header">
        <div class="chat-info">
          <div class="header-title">
            <img :src="leaderAvatar" alt="Avatar" class="avatar-large" />
            <h2>{{ groupName }}</h2>
          </div>
          <div class="subheader">
            <span class="leader-text">{{ leaderName }}'s Group</span>
            <span class="timing">Proposed Time: {{ proposedTiming }}</span>
          </div>
          <div class="members">
            <span>Members: </span>
            <span
              v-for="(member, index) in groupMembers"
              :key="member.id"
              class="member-item"
            >
              <span class="user-link" @click="goToProfile(member.id)">
                {{ member.firstName }} {{ member.lastName }}
              </span>
              <span v-if="index < groupMembers.length - 1">, </span>
              <span class="tooltip">
                Click to view {{ member.firstName }} {{ member.lastName }}'s
                profile!
              </span>
            </span>
          </div>
        </div>
        <div class="chat-actions">
          <button class="leave-btn" @click="showLeaveModal = true">
            Leave Group
          </button>
          <button
            class="complete-btn"
            @click="showReviewModal = true"
            :disabled="hasSubmittedReview"
          >
            {{ hasSubmittedReview ? "Review Submitted" : "Order Complete" }}
          </button>
        </div>
      </header>

      <div class="messages" ref="messagesContainer">
        <template v-if="isLoading">
          <div class="loading">Loading messages...</div>
        </template>
        <template v-else-if="messages.length === 0">
          <div class="no-messages">
            No messages yet. Start the conversation!
          </div>
        </template>
        <template v-else>
          <Message
            v-for="(msg, index) in messages"
            :key="index"
            :content="msg.content"
            :senderId="msg.senderId"
            :time="msg.time"
            :isMine="msg.senderId === userId"
            :isSystem="msg.senderId === 'system'"
          />
        </template>
      </div>

      <footer class="chat-input">
        <textarea
          v-model="newMessage"
          placeholder="Send a message..."
          class="auto-resize"
          @input="resizeInput"
        ></textarea>
        <button @click="sendMessage">Send</button>
      </footer>
    </template>
  </main>
  <LeaveModal
    v-if="showLeaveModal"
    :chat-id="chatId"
    :current-user-id="userId"
    @close="showLeaveModal = false"
    @leave="handleLeave"
  />

  <ReviewModal
    v-if="showReviewModal"
    :chat-id="chatId"
    :current-user-id="userId"
    @close="showReviewModal = false"
    @submitted="handleReviewSubmitted"
  />
</template>

<script>
import {
  addMessage,
  onMessagesUpdate,
  getGroupLeader,
  getChat,
  getGroupByChatId,
  getUser,
  deleteGroupMember,
  extractDealAndGroupIdFromChatId,
  removeChatFromUser,
  getChatUsers,
  getGroupMembers,
  updateGroupMember,
  getGroupMemberIdByUserId,
  deleteGroup,
} from "@/firebase/firestore";
import Message from "./Message.vue";
import LeaveModal from "./LeaveModal.vue";
import ReviewModal from "./ReviewModal.vue";

export default {
  name: "ChatWindow",
  props: {
    chatId: {
      type: String,
      required: true,
    },
    userId: {
      type: String,
      required: true,
    },
  },
  components: {
    Message,
    LeaveModal,
    ReviewModal,
  },
  data() {
    return {
      newMessage: "",
      messages: [],
      isLoading: false,
      error: null,
      unsubscribe: null,
      leaderName: "",
      leaderAvatar: "",
      groupName: "",
      proposedTiming: "",
      showLeaveModal: false,
      showReviewModal: false,
      groupMembers: [],
      hasSubmittedReview: false, // added this variable to track if the user has submitted a review
    };
  },
  watch: {
    chatId: {
      immediate: true,
      async handler(newChatId) {
        if (this.unsubscribe) {
          this.unsubscribe(); // Remove previous listener
        }

        if (newChatId) {
          this.setupMessageListener(); // Connect to the new chat
          await this.fetchGroupDetails(); // Fetch the group leader, chat info and proposed timing
          const reviewed = localStorage.getItem(`reviewed-${newChatId}`);
          this.hasSubmittedReview = reviewed === "true";
        } else {
          this.hasSubmittedReview = false;
          this.messages = [];
          this.leaderName = "";
          this.leaderAvatar = "";
          this.groupName = "";
          this.proposedTiming = "";
          this.groupMembers = [];
        }
      },
    },
  },
  methods: {
    handleReviewSubmitted() {
      this.showReviewModal = false;
      this.hasSubmittedReview = true; // Set the flag to true when the review is submitted
      localStorage.setItem(`reviewed-${this.chatId}`, "true"); // taken from local storage to preserve state when refreshing / navigating; the alternative would be to create a field in the database to track this but nah
    },
    setupMessageListener() {
      this.isLoading = true;
      this.unsubscribe = onMessagesUpdate(this.chatId, (messages, error) => {
        if (error) {
          this.error = error.message;
          this.messages = [];
        } else {
          this.messages = messages;
        }
        this.isLoading = false;

        // Scroll to bottom when new messages arrive
        this.$nextTick(() => {
          const container = this.$refs.messagesContainer;
          if (container) {
            container.scrollTop = container.scrollHeight;
          }
        });
      });
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return;

      try {
        await addMessage(this.chatId, this.userId, this.newMessage);
        this.newMessage = "";
      } catch (error) {
        console.error("Error sending message:", error);
      }
    },
    async fetchGroupDetails() {
      try {
        const [leader, chat, group, members] = await Promise.all([
          getGroupLeader(this.chatId),
          getChat(this.chatId),
          getGroupByChatId(this.chatId),
          getChatUsers(this.chatId),
        ]);

        if (leader) {
          this.leaderName = `${leader.firstName} ${leader.lastName}`;
          this.leaderAvatar =
            leader.profilePicURL || "https://via.placeholder.com/50";
        } else {
          this.leaderName = "Unknown";
          this.leaderAvatar = "https://via.placeholder.com/50";
        }

        if (chat) {
          this.groupName = chat.chatName;
        } else {
          this.groupName = "Unknown Group";
        }

        if (group) {
          this.proposedTiming = group.proposedDateTime;
        } else {
          this.proposedTiming = "No proposed timing";
        }
        this.groupMembers = members || [];
      } catch (error) {
        console.error("Error fetching group info:", error);
        this.leaderName = "Unknown";
        this.leaderAvatar = "https://via.placeholder.com/50";
        this.groupName = "Unknown Group";
        this.groupMembers = [];
      }
    },
    goToProfile(userId) {
      if (!userId) {
        console.error("User ID is not provided");
        return;
      }
      this.$router.push(`/ProfilePage/${userId}`);
    },
    resizeInput(event) {
      event.target.style.height = "auto";
      event.target.style.height = event.target.scrollHeight + "px";
    },
    async handleLeave() {
      const { dealId, groupId } = await extractDealAndGroupIdFromChatId(
        this.chatId
      );
      if (!dealId || !groupId) {
        console.error("Missing dealId or groupId for chatId:", this.chatId);
        return;
      }

      try {
        const leader = await getGroupLeader(this.chatId);
        const isLeaderLeaving = leader?.id === this.userId;

        const memberId = await getGroupMemberIdByUserId(
          dealId,
          groupId,
          this.userId
        );
        if (!memberId) {
          console.warn("Group member ID for current user not found");
          return;
        }

        await deleteGroupMember(dealId, groupId, memberId);
        await removeChatFromUser(this.userId, this.chatId);

        if (isLeaderLeaving) {
          const remainingMembers = await getGroupMembers(dealId, groupId);

          if (remainingMembers.length > 0) {
            const [newLeader, ...others] = remainingMembers;

            await updateGroupMember(
              dealId,
              groupId,
              newLeader.id,
              newLeader.user,
              true
            );
            await Promise.all(
              others.map((m) =>
                updateGroupMember(dealId, groupId, m.id, m.user, false)
              )
            );
            this.$emit("chat-updated", this.chatId);
          } else {
            await deleteGroup(dealId, groupId);
          }
        }

        const user = await getUser(this.userId);
        const name = user ? `${user.firstName} ${user.lastName}` : "A user";

        await addMessage(this.chatId, "system", `${name} has left the group`);

        this.$emit("left-chat", this.chatId);
        this.showLeaveModal = false;

        alert("You left the group.");
      } catch (err) {
        console.error("Failed to leave group:", err);
      }
    },
  },

  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe(); // Clean up listener when component is destroyed
    }
  },
};
</script>

<style scoped>
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  font-family: serif;
  background-color: white;
  height: 100%;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px 12px;
  font-family: serif;
  flex-shrink: 0;
  border-bottom: 1px solid #eee;
}

.chat-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.header-title {
  display: flex;
  align-items: center;
}

.header-title h2 {
  margin: 0;
  font-size: 1.1rem;
}

.avatar-large {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-right: 8px;
}

.subheader {
  display: flex;
  font-size: 0.85rem;
  color: #555;
  gap: 10px;
}

.leader-text {
  font-style: italic;
}

.timing {
  color: #666;
}

.members {
  font-size: 0.8rem;
  margin-top: 2px;
}

.messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: white;
  display: flex;
  flex-direction: column;
  font-family: serif;
}

.loading,
.no-messages {
  text-align: center;
  color: #666;
  padding: 20px;
}

.chat-input {
  display: flex;
  align-items: flex-end;
  /* key change */
  padding: 10px;
  background: white;
  font-family: serif;
  gap: 10px;
  /* spacing between textarea and button */
}

.chat-input textarea {
  flex: 1;
  padding: 12px 12px;
  /* vertically centered padding */
  border: none;
  border-radius: 5px;
  font-family: serif;
  background: #f1f1f1;
  font-size: 15px;
  line-height: 20px;
  resize: none;
  overflow-y: hidden;
  box-sizing: border-box;
  /* ensures padding doesn't increase height */
}

.chat-input button {
  height: 65px;
  padding: 0 16px;
  font-size: 14px;
  border: none;
  background: #123456;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font-family: serif;
}

.chat-actions {
  display: flex;
  gap: 10px;
}

.no-chat-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-family: serif;
  font-size: 1.2em;
  color: #666;
}

.member-item {
  display: inline-block;
  margin-right: 5px;
  position: relative;
  cursor: default;
}

.user-link {
  color: blue;
  text-decoration: none;
  cursor: pointer;
}

.user-link:hover {
  text-decoration: underline;
}

.tooltip {
  visibility: hidden;
  width: max-content;
  background-color: rgba(0, 0, 0, 0.75);
  color: #fff;
  text-align: center;
  border-radius: 5px;
  padding: 5px 10px;
  position: absolute;
  z-index: 10;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.8em;
  white-space: nowrap;
}

.member-item:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

.leave-btn,
.complete-btn {
  border-radius: 6px;
  border: none;
  padding: 6px 10px;
  font-family: serif;
  cursor: pointer;
  font-size: 0.85rem;
}

.leave-btn {
  background-color: #dfc0be;
}

.complete-btn {
  background-color: #abc6a9;
}
</style>
