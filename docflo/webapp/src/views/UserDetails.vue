<!--
Component for user details.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <div class="card">
      <div class="card-header">
        <div class="fs-5 float-start">
          <span v-if="isEdit">
            <span>{{ user.first_name }} {{ user.last_name }}</span>
          </span>
          <span v-else>User Details</span>
        </div>
        <span class="float-end">
          <button class="btn btn-outline-primary me-2"
            @click="save" type="submit">
            Save <i class="bi bi-save-fill"></i>
          </button>
          <button class="btn btn-outline-danger me-2" @click="reset" type="reset">
            Clear <i class="bi bi-eraser-fill"></i>
          </button>
          <a class="btn btn-outline-success" href="#/user">Add Another</a>
        </span>
      </div>
      <div class="card-body">
        <div class="row">
            <div class="col-md-4">
              <label for="st_email">Email</label>
              <input type="email" required class="form-control" id="st_email" v-model="user.email"
                :disabled="viewOnly" />
            </div>
            <div class="col-md-4">
              <label for="st_firstnm">First Name</label>
              <input type="text" required class="form-control" id="st_firstnm" v-model="user.first_name"
                :disabled="viewOnly" />
            </div>
            <div class="col-md-4">
              <label for="st_lastnm">Last Name</label>
              <input type="text" required class="form-control" id="st_lastnm" v-model="user.last_name"
                :disabled="viewOnly" />
            </div>
        </div>
        <div class="row">
          <div class="col-md-4">
            <label for="orgu">Org. Unit</label>
            <input type="text" required class="form-control" id="orgu"
            v-model="user.org_unit" :disabled="viewOnly" />
          </div>
          <div class="col-md-4">
            <label for="st_role">Role</label>
            <select required class="form-select" id="st_role" v-model="user.role" :disabled="viewOnly">
              <option v-for="x in SD.UserRoles" v-bind:value="x.id" :key="x.id">
                {{ x.value }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <div class="form-check mt-4">
              <input class="form-check-input" type="checkbox" id="gridCheck" v-model="user.is_locked"
                :disabled="viewOnly" />
              <label class="form-check-label" for="gridCheck">
                Locked?
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
export default {
  name: "UserDetails",
  components: { },
  data: function () {
    return {
      user: {},
    };
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    }
  },
  async created() {
    console.log("Creating User Details");
    let vm = this;
    if (vm.isEdit) {
      await vm.load();
    } else {
      vm.reset();
    }
    if (vm.$route.query["nr"] == 1) {
      vm.setStatusMessage("Saved the user details!");
      vm.$route.query = {};
    }
  },
  methods: {
    async load() {
      // Alias 'this' for accessing in promises
      let vm = this;
      let uid = vm.$route.params.id;
      console.log("Loading user details. id=" + uid);
      // Fetch data from an API
      await vm.doGet(`user/${uid}`, (b) => { vm.user = b; },
        vm.setStatusMessage)
    },
    isValid() {
      return !(_.isEmpty(this.user.email) || _.isEmpty(this.user.first_name)
        || _.isEmpty(this.user.last_name));
    },
    async save() {
      let vm = this;
      if (!this.isValid()) {
        vm.setStatusMessage("Please supply all required fields!");
        return;
      }
      if (!confirm("Confirm save?")) {
        vm.setStatusMessage("User canceled save!");
        return;
      }
      console.log("Saving user details.");
      await vm.doPost("user_save", vm.user,
        (b) => {
          vm.user = b;
          vm.setStatusMessage("Saved successfully!");
          if (!vm.isEdit) {
            vm.$router.push({ path: "/user/" + vm.user.id, query: { nr: 1 } });
          }
        }, vm.setStatusMessage);
    },
    reset() {
      this.user = {};
      console.log("Clearing user details.");
    },
  },
};
</script>
