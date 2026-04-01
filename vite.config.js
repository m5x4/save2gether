import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  // Add assets handling for images
  assetsInclude: ["**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.gif", "**/*.svg"],

  build: {
    // Increase the warning limit if needed
    chunkSizeWarningLimit: 1000, // in kBs (optional)

    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor packages into a separate chunk
          vendor: [
            "vue",
            "vue-router",
            "firebase/app",
            "firebase/auth",
            "firebase/firestore",
          ],

          // Group Firebase related code - using import paths instead of relative paths
          "firebase-core": [
            "@/firebase/firebase.js",
            "@/firebase/firestore.js",
            "@/firebase/storage.js",
            "@/firebase/session.js",
          ],

          // Component chunks using import paths
          "ui-components": [
            "@/components/Header.vue",
            "@/components/FilterButton.vue",
            "@/components/SortButton.vue",
          ],
          "app-services": ["@/services/imageCache.js"],
          "deal-components": [
            "@/components/DealCard.vue",
            "@/components/ReviewCard.vue",
            "@/components/ReviewModal.vue",
          ],
          "group-components": [
            "@/components/GroupCard.vue",
            "@/components/JoinGroupModal.vue",
            "@/components/LeaveGroupButton.vue",
          ],
          "chat-components": [
            "@/components/ChatCard.vue",
            "@/components/ChatWindow.vue",
            "@/components/Message.vue",
          ],
        },
      },
    },
  },
});
