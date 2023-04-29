<!--
Component for searching users.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Find Users</h5>
    <form @submit.prevent="find(false)">
      <div class="row mb-2">
        <div class="col-md-2">
          <label for="st_role">Role</label>
          <select class="form-select" id="st_role" v-model="user.role">
            <option v-for="x in SD.UserRoles" v-bind:value="x.id" :key="x.id">{{ x.value }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <label for="st_area">Area</label>
          <select class="form-select" id="st_area" v-model="user.area">
            <option v-for="x in SD.WorkAreas" v-bind:value="x.id" :key="x.id" :disabled="x.disabled">{{ x.value }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <label for="eml">Email</label>
          <input type="text" class="form-control" id="eml" v-model="user.email" />
        </div>
        <div class="col-md-3">
          <label for="st_firstnm">Name</label>
          <input type="text" class="form-control" id="st_firstnm" v-model="user.name" />
        </div>
        <div class="col">
          <div class="mt-4">
            <button class="btn btn-outline-success me-2" type="submit">
              <i class="bi bi-search"></i>
            </button>
            <button class="btn btn-outline-danger" @click="reset" type="reset">
              <i class="bi bi-eraser"></i>
            </button>
          </div>
        </div>
      </div>
    </form>

    <div class="card">
      <div class="card-header">
        <span class="fs-5">Results</span>
        <span class="float-end">
          <button
            class="btn btn-outline-info btn-sm me-4"
            v-if="user.pg_no > 1"
            @click="prev_pg"
          >Prev</button>
          <button
            class="btn btn-outline-info btn-sm me-4"
            v-if="results.has_next"
            @click="next_pg"
          >Next</button>
        </span>
      </div>
      <div class="card-body">
        <div class="row fw-bold border-info border-bottom border-2">
          <div class="col-md-1">S#</div>
          <div class="col">Name</div>
          <div class="col-md-2">Role</div>
          <div class="col-md-2">Org Unit</div>
          <div class="col-md-1">Locked</div>
        </div>
        <p v-if="results.users.length == 0">Nothing to show yet!</p>
        <div class="row row-striped mt-4" v-for="(r, i) in results.users" :key="r.id">
          <div class="col-md-1">{{(results.pg_no - 1) * results.pg_size + i + 1}}</div>
          <div class="col">
            <a :href="'#/user/'+r.id">{{r.first_name}} {{r.last_name}}</a>
            <span class="ms-2">{{r.email}}</span>
          </div>
          <div class="col-md-2">{{r.org_unit}}</div>
          <div class="col-md-1">{{r.is_locked?"Yes":"No"}}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserSearch",
  data: function() {
    return {
      user: { pg_no: 1 },
      results: { users: [], has_next: false }
    };
  },
  computed: {
  },
  beforeRouteUpdate(to, from, next) {
    console.log("UserSearch.beforeRouteUpdate");
    next();
  },
  created: function() {
    console.log("Creating UserSearch");
  },
  mounted: function() {
    if (sessionStorage.user){
      this.user = JSON.parse(sessionStorage.user);
    }
    if (sessionStorage.myUserS) {
      this.results = JSON.parse(sessionStorage.myUserS);
      if (!this.results.users) {
        this.results = { users: [], has_next: false };
      }
    } else {
      this.results = { users: [], has_next: false };
    }
  },
  methods: {
    async next_pg() {
      this.user.pg_no += 1;
      await this.find(true);
    },
    async prev_pg() {
      this.user.pg_no -= 1;
      await this.find(true);
    },
    async find(is_paging) {
      let vm = this;
      if (!is_paging) vm.user.pg_no = 1;
      sessionStorage.user = JSON.stringify(vm.user);
      vm.results.users = [];
      await vm.doPost("user_find", vm.user,
        (b) => {
          vm.results = b;
          sessionStorage.myUserS = JSON.stringify(vm.results);
        }, vm.setStatusMessage);
    },
    reset() {
      this.results = { users: [], has_next: false };
      this.user = { pg_no: 1 };
      sessionStorage.myUserS = undefined;
      sessionStorage.user = undefined;
    }
  }
};
</script>
