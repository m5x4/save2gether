<template>
  <div class="chat-card" @click="handleClick">
    <img
      :src="avatar || 'https://via.placeholder.com/50'"
      alt="Profile"
      class="avatar"
    />
    <div class="chat-info">
      <h3>{{ name }}</h3>
      <p>{{ lastMessage || "No messages yet" }}</p>
    </div>
  </div>
</template>
<script>
import {
  getChat,
  getLatestMessage,
  getGroupLeaderProfilePic,
  onMessagesUpdate,
} from "@/firebase/firestore";

export default {
  name: "ChatCard",
  props: {
    chatId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      name: "",
      lastMessage: "",
      avatar: "",
      isLoading: true,
      messageListener: null,
    };
  },
  async created() {
    await this.fetchChatData();
  },
  mounted() {
    this.setupMessageListener();
  },
  beforeUnmount() {
    this.removeMessageListener();
  },
  methods: {
    async fetchChatData() {
      try {
        const chat = await getChat(this.chatId);
        if (chat) {
          this.name = chat.chatName;
        }

        const message = await getLatestMessage(this.chatId);
        if (message) {
          this.lastMessage = message;
        }

        const profilePic = await getGroupLeaderProfilePic(this.chatId);
        if (profilePic) {
          this.avatar = profilePic;
        }
      } catch (error) {
        console.error("Error fetching chat data:", error);
      } finally {
        this.isLoading = false;
      }
    },
    setupMessageListener() {
      this.messageListener = onMessagesUpdate(this.chatId, (messages) => {
        if (messages && messages.length > 0) {
          // Get the latest message (last one in the array)
          const latestMessage = messages[messages.length - 1];

          if (latestMessage.content) {
            // console.log("latest message: ", latestMessage);
            this.lastMessage = latestMessage.content;
          } else {
            this.lastMessage = "New message";
          }
        }
      });
    },
    removeMessageListener() {
      // Unsubscribe from the real-time listener
      if (this.messageListener) {
        this.messageListener();
        this.messageListener = null;
      }
    },
    handleClick() {
      this.$emit("load-chat-window", this.chatId);
    },
  },
};
</script>

<style scoped>
.chat-card {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-card:hover {
  background-color: #f5f5f5;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 15px;
}

.chat-info {
  flex: 1;
}

.chat-info h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.chat-info p {
  margin: 5px 0 0;
  font-size: 14px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
