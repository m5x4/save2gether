<template>
  <Teleport to="body">
    <div class="modal-overlay" @click="closeModal">
      <div class="edit-profile-container" @click.stop>
        <div class="modal-header">
          <h1>Edit Profile</h1>
          <button class="close-button" @click="closeModal">&times;</button>
        </div>
        <div v-if="user" class="profile-form">
          <div class="profile-pic-section">
            <img
              :src="user.profilePicURL || '/src/assets/avatar.png'"
              alt="Current Profile Picture"
              class="current-profile-pic"
            />
            <input
              type="file"
              @change="handleProfilePicChange"
              accept="image/*"
              class="profile-pic-input"
            />
            <p v-if="uploadError" class="error-message">{{ uploadError }}</p>
          </div>

          <div class="form-group">
            <label for="firstName">First Name</label>
            <input
              type="text"
              id="firstName"
              v-model="formData.firstName"
              required
            />
          </div>

          <div class="form-group">
            <label for="lastName">Last Name</label>
            <input
              type="text"
              id="lastName"
              v-model="formData.lastName"
              required
            />
          </div>

          <div class="button-group">
            <button
              @click="saveProfile"
              class="save-button"
              :disabled="isSaving"
            >
              {{ isSaving ? "Saving..." : "Save Changes" }}
            </button>
            <button
              @click="closeModal"
              class="cancel-button"
              :disabled="isSaving"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { auth } from "@/firebase/firebase.js";
import { updateUser } from "@/firebase/firestore.js";
import { uploadProfilePicture } from "@/firebase/storage.js";

export default {
  name: "EditProfile",
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  emits: ["close", "profile-updated"],
  data() {
    return {
      formData: {
        firstName: "",
        lastName: "",
        profilePicURL: "",
      },
      profilePicFile: null,
      isSaving: false,
      uploadError: null,
    };
  },
  created() {
    this.formData = {
      firstName: this.user.firstName || "",
      lastName: this.user.lastName || "",
      profilePicURL: this.user.profilePicURL || "",
    };
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },
    async handleProfilePicChange(event) {
      const file = event.target.files[0];
      if (file) {
        // Validate file type
        if (!file.type.startsWith("image/")) {
          this.uploadError = "Please select an image file";
          return;
        }

        // Validate file size (max 100KB)
        if (file.size > 100 * 1024) {
          this.uploadError = "Image size should be less than 100KB";
          return;
        }

        this.profilePicFile = file;
        this.uploadError = null;
      }
    },
    async saveProfile() {
      try {
        this.isSaving = true;
        const authUser = auth.currentUser;
        if (!authUser) return;

        let profilePicURL = this.formData.profilePicURL;

        // Upload new profile picture if selected
        if (this.profilePicFile) {
          try {
            profilePicURL = await uploadProfilePicture(
              this.profilePicFile,
              authUser.uid
            );
          } catch (error) {
            this.uploadError =
              "Failed to upload profile picture. Please try again.";
            this.isSaving = false;
            return;
          }
        }

        // Update user profile
        await updateUser(
          authUser.uid,
          this.formData.firstName,
          this.formData.lastName,
          profilePicURL
        );

        this.$emit("profile-updated");
      } catch (error) {
        console.error("Error updating profile:", error);
        this.uploadError = "Failed to update profile. Please try again.";
      } finally {
        this.isSaving = false;
      }
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-profile-container {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  animation: modalFadeIn 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.modal-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px 10px;
  color: #666;
}

.close-button:hover {
  color: #333;
}

.profile-form {
  margin-top: 20px;
}

.profile-pic-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.current-profile-pic {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
  border: 2px solid #eee;
}

.profile-pic-input {
  margin-top: 10px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  max-width: 300px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #17334b;
  box-shadow: 0 0 0 2px rgba(23, 51, 75, 0.1);
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: flex-end;
}

.save-button,
.cancel-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.save-button {
  background-color: #17334b;
  color: white;
}

.cancel-button {
  background-color: #d9d9d9;
  color: black;
}

.save-button:hover:not(:disabled) {
  background-color: #122538;
  transform: translateY(-1px);
}

.cancel-button:hover:not(:disabled) {
  background-color: #c0c0c0;
  transform: translateY(-1px);
}

.save-button:disabled,
.cancel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  color: #ff4444;
  margin-top: 10px;
  text-align: center;
  font-size: 0.9rem;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
