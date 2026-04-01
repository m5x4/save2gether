<template>
  <Header />
  <div class="loginPage">
    <div class="buttonContainer">
      <button class="google-signin-btn" @click="handleGoogleSignIn">
        <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" />
        <span>Sign in with Google</span>
      </button>
    </div>


    <div class="separator">
      <span>OR</span>
    </div>

    <form class="loginForm" @submit.prevent="loginEmailPassword">
      <div class="formRow">
        <label for="email">Email:</label>
        <input id="email" v-model="email" type="email" />
      </div>

      <div class="formRow">
        <label for="password">Password:</label>
        <input id="password" v-model="password" type="password" />
      </div>

      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script setup>
import Header from "@/components/Header.vue";

import { ref } from "vue";
import { useRouter } from "vue-router";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { getUser } from "@/firebase/firestore.js";
import {
  auth,
  db,
  signInWithEmailAndPassword,
  setDoc,
  doc,
} from "@/firebase/firebase.js";

const router = useRouter();

const email = ref("");
const password = ref("");

// Default avatar URL from Firebase Storage
const DEFAULT_AVATAR_URL =
  "https://firebasestorage.googleapis.com/v0/b/save2gether-90146.firebasestorage.app/o/profile-pictures%2Fdefault_avatar.png?alt=media&token=82b6ba98-653d-46c9-b612-7ea3ad667bcc";

// Google Sign-In Credential Handler
const handleGoogleSignIn = async () => {
  try {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    const user = result.user;

    const fullName = user.displayName || "";
    const [fName, ...rest] = fullName.split(" ");
    const lName = rest.join(" ") || "";

    const existingUser = await getUser(user.uid);

    if (!existingUser) {
      const userRef = doc(db, "User", user.uid);
      await setDoc(userRef, {
        firstName: fName,
        lastName: lName,
        profilePicURL: user.photoURL || DEFAULT_AVATAR_URL,
        joinDateTime: new Date(),
        deals: [],
        chats: [],
      });
      alert("Google account created successfully!");
    } else {
      alert("User already exists. Logging you in.");
    }

    router.push("/HomeView");
  } catch (error) {
    console.error("Google Sign-In Failed:", error.message);
    alert("Sign-In Failed: " + error.message);
  }
};

// Email/Password Login Function
const loginEmailPassword = async () => {
  try {
    const userCredential = await signInWithEmailAndPassword(
      auth,
      email.value,
      password.value
    );
    // console.log("Email/Password User:", userCredential.user);

    // Store user session (handled by firebase auth)
    // localStorage.setItem("user", JSON.stringify(userCredential.user));

    alert("Login successful!");
    router.push("/HomeView"); // replace this later with the correct routing
  } catch (error) {
    const errorCode = error.code || error?.error?.code || null;
    const errorMsg = error.message || error?.error?.message || "Unknown error";

    console.error("Login Error:", errorCode, errorMsg);

    if (errorCode === "auth/user-not-found") {
      alert("No account found with this email.");
    } else if (errorCode === "auth/wrong-password") {
      alert("Incorrect password. Please try again.");
    } else if (errorCode === "auth/invalid-email") {
      alert("Please enter a valid email address.");
    } else if (errorCode === "auth/missing-password") {
      alert("Please enter your password.");
    } else if (errorCode === "auth/invalid-credential") {
      alert("Invalid email/password combination.");
    } else if (errorCode === "auth/too-many-requests") {
      alert("Too many failed attempts. Please try again later.");
    } else {
      alert("Login failed: " + errorMsg);
    }
  }
};
</script>

<style scoped>
.loginPage {
  display: flex;
  flex-direction: column;
  text-align: center;
  margin-top: 100px;
}

.buttonContainer {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.google-signin-btn {
  display: flex;
  align-items: center;
  width: fit-content;
  gap: 10px;
  background-color: #fff;
  border: 1px solid #dadce0;
  border-radius: 20px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  font-family: Roboto, sans-serif;
  color: #3c4043;
  cursor: pointer;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s ease;
  height: 40px;
}

.google-signin-btn:hover {
  background-color: #f7f8f8;
}

.google-signin-btn img {
  width: 18px;
  height: 18px;
}

.separator {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 800px;
  margin: 30px auto;
  font-weight: bold;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.separator::before,
.separator::after {
  content: "";
  flex: 1;
  height: 1px;
  background-color: #ccc;
  margin: 0 10px;
}

.loginForm {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
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

.loginForm button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  width: 100px; 
  border-radius: 20px;
  border: none;
  font-family: inherit;
}
</style>
