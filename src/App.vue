<template>
  <!-- <h1>App.vue</h1>
  <router-link to="/signup">Sign Up</router-link>
  <br />
  <router-link to="/login">Login</router-link>
  <br />
  <router-link to="/">Landing Page</router-link>
  <br />
  <router-link to="/distance">Test</router-link>
  <br />
  <router-link to="/chat">Chat</router-link>
  <br />
  <router-link to="/test2">Test2</router-link>
  <br />
  <router-link to="/test2">Test2</router-link>
  <br />
  <router-link :to="`/ProfilePage`">My Profile Page</router-link> -->
  <router-view />
</template>

<script>
import Header from "./components/Header.vue";

export default {
  components: {
    Header,
  },
};
</script>
<style>
body {
  font-family: "Arial", "Helvetica", sans-serif;
}
</style>
