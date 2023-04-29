<!--
This is the main component of the application which
holds the main nav bar and views container.

@author Balwinder Sodhi
-->
<template>
  <div id="appMain" class="container-fluid">
    <Navbar
      v-bind:navItems="navData"
      v-bind:user="currentUser"
      v-on:logout-user="onLogout"
    />
    <br />
    <div
      style="z-index: 1100"
      class="position-fixed top-50 start-50 translate-middle"
    >
      <div
        v-if="statusMsg != ''"
        class="alert alert-warning alert-dismissible fade show"
        role="alert"
      >
        {{ statusMsg }}
        <button
          @click="setStatusMessage('')"
          type="button"
          class="btn-close"
          data-bs-dismiss="alert"
          aria-label="Close"
        ></button>
      </div>
    </div>
    <router-view
      v-on:user-logged-in="onLogin"
      :key="$route.fullPath"
    ></router-view>
  </div>
</template>

<script>
import Navbar from "./views/Navbar.vue";

export default {
  name: "App",
  components: {
    Navbar,
  },

  /**
   * App component will update auth status via $root
   * We use this value in the auth check navigation gaurd below.
   */
  data() {
    return {
      navData: {
        menus: {},
        links: [],
      },
      user: {},
      statusMessage: "",
      staticData: {},
      viewOnlyFlag: false,
    };
  },
  async mounted() {
    let vm = this;
    // Add AJAX interceptors
    vm.$http.interceptors.request.use(
      function (config) {
        // Do something before request is sent
        vm.statusMessage = "Please wait...";
        return config;
      },
      function (error) {
        // Do something with request error
        return Promise.reject(error);
      }
    );
    vm.$http.interceptors.response.use(
      function (response) {
        // Any status code that lie within the range of 2xx cause this function to trigger
        // Do something with response data
        vm.statusMessage = "";
        return response;
      },
      function (error) {
        // Any status codes that falls outside the range of 2xx cause this function to trigger
        // Do something with response error
        vm.statusMessage = "Error occurred: " + error;
        return Promise.reject(error);
      }
    );
    await vm.initSession();
  },

  methods: {
    async initSession() {
      sessionStorage.clear();
      localStorage.clear();
      let vm = this;
      try {
        console.log("Loading logged in user if any.");
        let res = await vm.$http.get("./current_user");
        if (res.data.status == "OK") {
          await vm.onLogin(res.data.body);
        } else {
          console.log("No logged in user found.");
          await vm.onLogout();
        }
      } catch (error) {
        console.log(error);
        vm.setStatusMessage("Error occurred when getting current user.");
      }
    },
    async getStaticData() {
      let vm = this;
      console.log("Loading static data.");
      try {
        let res = await vm.$http.get("./get_static_data");
        if (res.data.status == "OK") {
          vm.setStaticData(res.data.body);
        } else {
          vm.setStatusMessage("Failed to load static data: " + res.data.body);
        }
      } catch (error) {
        console.log(error);
        vm.setStatusMessage("Error occurred when getting static data.");
      }
    },
    async onLogin(sessData) {
      console.log("User logged IN. Route name: " + this.$route.name);
      this.setCurrentUser(sessData.user);
      this.isOAuth =
        sessData.user.is_oauth !== undefined && sessData.user.is_oauth;
      await this.getStaticData();
      if (sessData.nav !== undefined) {
        this.navData = sessData.nav;
      }
      this.$router.push("/");
    },
    async onLogout() {
      console.log("User logged OUT.");
      sessionStorage.clear();
      localStorage.clear();
      let vm = this;
      vm.setCurrentUser({});
      vm.navData = { menus: {}, links: [] };
      try {
        let res = await vm.$http.get("logout");
        if (res.data.status == "OK") {
          console.log("User logged out.");
          vm.$router.push("/login");
          if (vm.isOAuth) {
            vm.setStatusMessage(
              "You are logged out only from this app, and not your Google account!"
            );
          }
        } else {
          console.log("Logout failed: " + res.data.body);
        }
      } catch (error) {
        console.log(error);
        vm.setStatusMessage("Error occurred when logging out.");
      }
    },
  },
};
</script>