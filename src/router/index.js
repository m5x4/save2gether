import { createRouter, createWebHistory } from "vue-router";
import { checkAuthState } from "@/firebase/session.js";

// Only import the LandingPage statically since it's the entry point
import LandingPage from "../views/LandingPage.vue";

// import HomeView from "../views/HomeView.vue";
import CreateDeal from "../views/CreateDeal.vue";
// import ViewDeal from "../views/ViewDeal.vue";
// import ChatView from "../views/ChatView.vue";
// import ViewGroup from "../views/ViewGroup.vue";
// import SignUpPage from "../views/SignUpPage.vue";
// import LoginPage from "../views/LoginPage.vue";
// import ProfilePage from "../views/ProfilePage.vue";
// import SearchView from "../views/SearchView.vue";

// Use dynamic imports for all other routes
// This creates separate chunks that are loaded only when needed
const HomeView = () => import("../views/HomeView.vue");
// const CreateDeal = () => import("../views/CreateDeal.vue"); // this is buggy, makes white border around the whole page
const ViewDeal = () => import("../views/ViewDeal.vue");
const ChatView = () => import("../views/ChatView.vue");
const ViewGroup = () => import("../views/ViewGroup.vue");
const SignUpPage = () => import("../views/SignUpPage.vue");
const LoginPage = () => import("../views/LoginPage.vue");
const ProfilePage = () => import("../views/ProfilePage.vue");
const SearchView = () => import("../views/SearchView.vue");

const routes = [
  { path: "/", name: "LandingPage", component: LandingPage },
  { path: "/login", name: "LoginPage", component: LoginPage },
  { path: "/signup", name: "SignUpPage", component: SignUpPage },
  { path: "/HomeView", name: "HomeView", component: HomeView },
  // { path: "/HomeView", name: "HomeView", meta: { requiresAuth: true }, component: HomeView },
  {
    path: "/CreateDeal",
    name: "CreateDeal",
    component: CreateDeal,
  },
  {
    path: "/ViewDeal",
    name: "ViewDeal",
    component: ViewDeal,
  },
  // {
  //   path: "/distance",
  //   name: "distance",
  //   component: distance,
  // },
  {
    path: "/chat",
    component: ChatView,
  },
  {
    path: "/ViewGroup",
    name: "ViewGroup",
    component: ViewGroup,
  },
  {
    path: "/ProfilePage/:userId?",
    name: "ProfilePage",
    component: ProfilePage,
  },
  {
    path: "/search",
    name: "SearchView",
    component: SearchView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      await checkAuthState();
      next(); // User is authenticated, proceed to route
    } catch (error) {
      next("/"); // User is not authenticated, redirect to landing page
    }
  } else {
    next(); // Route doesn't require auth, proceed
  }
});

export default router;
