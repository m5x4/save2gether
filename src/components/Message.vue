<template>
  <div :class="['message', isSystem ? 'system-message' : messageClass]">
    <template v-if="isSystem">
      <p class="system-msg">{{ content }}</p>
    </template>
    <template v-else>
      <p class="sender-name">{{ senderName }}</p>
      <p class="message-content">{{ content }}</p>
      <p class="message-time">{{ formattedTime }}</p>
    </template>
  </div>
</template>

<script>
import { getUser } from "@/firebase/firestore";

export default {
  name: "Message",
  props: {
    content: {
      type: String,
      required: true,
    },
    senderId: {
      type: String,
      required: true,
    },
    time: {
      type: String,
      required: true,
    },
    isMine: {
      type: Boolean,
      required: true,
    },
    isSystem: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      senderName: "Loading...",
    };
  },
  computed: {
    messageClass() {
      return this.isMine ? "my-message" : "their-message";
    },
    formattedTime() {
      const date = new Date(this.time);
      const options = {
        day: "2-digit",
        month: "short",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      };
      const parts = new Intl.DateTimeFormat("en-US", options).formatToParts(
        date
      );

      const day = parts.find((p) => p.type === "day")?.value;
      const month = parts.find((p) => p.type === "month")?.value;
      const hour = parts.find((p) => p.type === "hour")?.value;
      const minute = parts.find((p) => p.type === "minute")?.value;
      const dayPeriod = parts.find((p) => p.type === "dayPeriod")?.value;

      return `${day} ${month}, ${hour}:${minute}${dayPeriod}`;
    },
  },
  async mounted() {
    if (this.isSystem) return;
    try {
      const user = await getUser(this.senderId);
      if (user) {
        this.senderName = `${user.firstName} ${user.lastName}`;
      }
    } catch (error) {
      console.error("Error fetching sender name:", error);
      this.senderName = "Unknown User";
    }
  },
};
</script>

<style scoped>
.message {
  max-width: 70%;
  padding: 10px;
  margin: 5px 0;
  border-radius: 10px;
  font-family: serif;
  display: flex;
  flex-direction: column;
}

.my-message {
  background: #b9d4f2;
  align-self: flex-end;
}

.their-message {
  background: #f1f1f1;
  align-self: flex-start;
}

.sender-name {
  font-size: 12px;
  color: #666;
  margin-bottom: 0px;
  margin-top: 1px;
  font-style: italic;
}

.message-content {
  font-size: 14px;
  color: #000;
  margin-bottom: 1px;
  margin-top: 5px;
}

.message-time {
  font-size: 10px;
  color: #666;
  margin-top: 5px;
  align-self: flex-end;
  margin-bottom: 1px;
}

.system-message {
  background: none;
  padding: 0;
  margin: 10px auto;
  text-align: center;
  font-style: italic;
  color: #888;
  max-width: 100%;
  display: flex;
  justify-content: center;
}
</style>
