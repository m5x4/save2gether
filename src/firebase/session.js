import { auth } from "./firebase.js";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { useRouter } from "vue-router";

// Function to check if user is authenticated
export const checkAuthState = () => {
  return new Promise((resolve, reject) => {
    onAuthStateChanged(auth, (user) => {
      if (user) {
        resolve(user);
      } else {
        reject("No user is signed in.");
      }
    });
  });
};

// Function to handle user redirection based on auth state
export const handleAuthRedirect = () => {
  const router = useRouter();
  onAuthStateChanged(auth, (user) => {
    if (user) {
      router.push("/HomeView"); // Redirect to home if logged in
    } else {
      router.push("/"); // Redirect to landing page if not logged in
    }
  });
};

// Function to log out the user
export const logoutUser = async () => {
  try {
    await signOut(auth);
    // The router navigation will be handled by the auth state listener
    return true;
  } catch (error) {
    console.error("Logout error:", error);
    return false;
  }
};
