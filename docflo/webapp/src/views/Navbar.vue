<!--
Component for the application's navigation bar.

@author Balwinder Sodhi
-->
<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark" 
      v-bind:class=" { 'navbarOpen': show }">
      <div class="container-fluid">
        <a class="navbar-brand" href="/docflo/"><i class="bi bi-bank2"></i></a>
        <button
          class="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarCollapse"
          aria-controls="navbarCollapse"
          aria-expanded="false"
          aria-label="Toggle navigation"
          @click.stop="toggleNavbar()"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse" v-bind:class="{ 'show': show }">
        <ul class="navbar-nav me-auto" >
          <li class="nav-item dropdown" v-for="m in navItems.menus" :key="m.label">
            <a
              class="nav-link dropdown-toggle" data-bs-toggle="dropdown"
              href="#"
              role="button"
              aria-haspopup="true"
              aria-expanded="false"
            >{{m.label}}</a>
            <div class="dropdown-menu">
              <div v-for="mi in m.items" :key="mi.label">
                <a class="dropdown-item" :href="mi.href">{{ mi.label }}</a>
              </div>
            </div>
          </li>
          <li class="nav-item" v-for="l in navItems.links" :key="l.label">
            <a class="nav-link" :href="l.href">{{l.label}}</a>
          </li>
        </ul>
        <span class="me-2">
          <div v-if="isAdmin" class="input-group">
            <label class="input-group-text" for="ig1">Become:</label>
            <select id="ig1" class="form-select" v-model="becomeUser" @change="onUserSelect">
              <option v-for="x in SD.UsersList" v-bind:value="x.id" :key="x.id">
                {{ x.value }}
              </option>
            </select>
          </div>
        </span>
        <span v-if="user.email != undefined">
          <span class="navbar-text me-2" style="font-size: small">
            {{user.first_name}}&nbsp;{{user.last_name}}
            ({{labelFor(SD.UserRoles, user.role)}},
            {{user.org_unit}})
          </span>
          <button class="btn btn-outline-danger" type="button" @click="logout" title="Logout">
            <i class="bi bi-power"></i>
          </button>
        </span>
        <span v-else>
          <a class="btn btn-outline-warning" href="./">Login</a>
        </span>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: "Navbar",
  props: ["navItems", "user"],
  data() {
    return {
      show: true
    };
  },
  methods: {
    logout() {
      console.log("Clicked logged out.");
      this.$emit("logout-user");
    },
    toggleNavbar() {
      this.show = !this.show;
    },
    async onUserSelect() {
      let vm = this;
      console.log("Selected User: "+vm.becomeUser);
      await vm.doGet("to_user/"+vm.becomeUser, 
        (b)=>{location.reload()}, vm.setStatusMessage)
    }
  }
};
</script>

<style>
.nav-link:hover {
    text-decoration-line: overline;
}
</style>