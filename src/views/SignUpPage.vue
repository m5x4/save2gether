<template>
  <Header />
  <form class="signUpForm" @submit.prevent="handleSignUp">
    <div class="formRow">
      <label for="firstName">First Name:</label>
      <input id="firstName" v-model="firstName" type="text" />
    </div>

    <div class="formRow">
      <label for="lastName">Last Name:</label>
      <input id="lastName" v-model="lastName" type="text" />
    </div>

    <div class="formRow">
      <label for="email">Email:</label>
      <input id="email" v-model="email" type="email" />
      <!-- form default warning message is active for email field -->
    </div>

    <div class="formRow">
      <label for="password">Password:</label>
      <input id="password" v-model="password" type="password" />
      <!--default is 6 char long -->
    </div>

    <div class="formRow">
      <label for="confirmPassword">Confirm Password:</label>
      <input id="confirmPassword" v-model="confirmPassword" type="password" />
    </div>

    <button type="submit">Sign Up</button>
  </form>
</template>

<script setup>
import Header from "@/components/Header.vue";

import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  auth,
  db,
  createUserWithEmailAndPassword,
  doc,
  setDoc,
} from "@/firebase/firebase.js";

const router = useRouter();
const firstName = ref("");
const lastName = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");

// Default avatar URL from Firebase Storage
const DEFAULT_AVATAR_URL =
  "https://firebasestorage.googleapis.com/v0/b/save2gether-90146.firebasestorage.app/o/profile-pictures%2Fdefault_avatar.png?alt=media&token=82b6ba98-653d-46c9-b612-7ea3ad667bcc";

// Sign-Up Function with Email & Password
const handleSignUp = async () => {
  if (
    !firstName.value.trim() ||
    !lastName.value.trim() ||
    !email.value.trim() ||
    !password.value.trim() ||
    !confirmPassword.value.trim()
  ) {
    alert("Please fill in all fields.");
    return;
  }
  if (password.value !== confirmPassword.value) {
    console.error("Passwords do not match.");
    alert("Passwords do not match.");
    return;
  }

  try {
    // Create User in Firebase Authentication
    const result = await createUserWithEmailAndPassword(
      auth,
      email.value,
      password.value
    );
    // console.log("User:", result.user);

    // Store Additional User Info in Firestore
    await setDoc(doc(db, "User", result.user.uid), {
      firstName: firstName.value,
      lastName: lastName.value,
      profilePicURL: DEFAULT_AVATAR_URL,
      joinDateTime: new Date(),
      chats: [], // initialize empty chats array
      deals: [], // initialize empty deals array
    });

    // console.log("User data saved in Firestore!");
    alert("Sign up successful.");
    router.push("/login");
  } catch (error) {
    const errorCode = error.code || error?.error?.code || null;
    const errorMsg = error.message || error?.error?.message || "Unknown error";

    console.error(errorCode, errorMsg);

    if (error.code === "auth/email-already-in-use") {
      alert("This email is already registered. Please log in instead.");
    } else if (errorCode === "auth/invalid-email") {
    alert("Please enter a valid email address.");
  } else {
    alert("Sign up failed: " + errorMsg);
  }
  }
};
</script>

<style scoped>
.signUpForm {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-top: 100px;
}

.formRow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 450px;
  margin-right: 150px;
}

label {
  width: 150px;
  text-align: right;
  font-weight: 500;
}

input {
  width: 250px;
  padding: 8px;
  font-size: 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  width: 120px;
  border-radius: 20px;
  border: none;
  font-family: inherit;
}
</style>
