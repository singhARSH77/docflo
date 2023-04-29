<!--
Component for searching doc types.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Find Doc Types</h5>
    <form @submit.prevent="find(false)">
      <div class="row mb-2">
        <div class="col">
          <label for="grp">Group Name</label>
          <input id="grp" class="form-control" type="text" v-model="crit.group" />  
        </div>
        <div class="col">
          <label for="sub_role">Doc Type Name</label>
          <input class="form-control" type="text" v-model="crit.name" />  
        </div>
        <div class="col-md-4">
          <div class="mt-4">
            <button class="btn btn-outline-success me-2" type="submit">
              <i class="bi bi-search"></i>
            </button>
            <button class="btn btn-outline-danger me-2" @click="reset" type="reset">
              <i class="bi bi-eraser"></i>
            </button>
            <a class="btn btn-sm btn-primary float-end" href="#/doc_type">Create New</a>
          </div>
        </div>
      </div>
    </form>
    <div class="card">
      <div class="card-header">
        <span class="fs-5">Results</span>
        <span class="float-end">
          <button class="btn btn-outline-info btn-sm me-4" v-if="crit.pg_no > 1" @click="prev_pg">Prev</button>
          <button class="btn btn-outline-info btn-sm me-4" v-if="results.has_next" @click="next_pg">Next</button>
        </span>
      </div>
      <div class="card-body">
        <div class="row fw-bold border-info border-bottom border-2">
          <div class="col-md-1">S#</div>
          <div class="col-md-2">Name</div>
          <div class="col-md-2">Group</div>
          <div class="col">Details</div>
        </div>
        <p v-if="!hasResults">Nothing to show yet!</p>
        <div v-else class="row row-striped mt-4" v-for="(r, i) in results.items" :key="r.id">
          <div class="col-md-1">{{ (results.pg_no - 1) * results.pg_size + i + 1 }}</div>
          <div class="col-md-2">
            <a :href="'#/doc_type/' + r.id">{{r.name}}</a>
          </div>
          <div class="col-md-2">{{r.group}}</div>
          <div class="col">
            {{r.description}}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DocTypeSearch",
  data: function () {
    return {
      crit: { pg_no: 1 },
      results: { items: [], has_next: false }
    };
  },
  computed: {
    hasResults() {
      if (this.results == undefined) return false;
      if (this.results.items == undefined) return false;
      if (this.results.items.length == 0) return false;
      return true
    }
  },
  created: function () {
    console.log("Creating DocTypeSearch");
  },
  mounted: function () {
    if (sessionStorage.dtSrch) {
      this.crit = JSON.parse(sessionStorage.dtSrch);
    }
    if (sessionStorage.myDtRes) {
      this.results = JSON.parse(sessionStorage.myDtRes);
    } else {
      this.results = { items: [], has_next: false };
    }
  },
  methods: {
    async next_pg() {
      this.crit.pg_no += 1;
      await this.find(true);
    },
    async prev_pg() {
      this.crit.pg_no -= 1;
      await this.find(true);
    },
    async find(is_paging) {
      let vm = this;
      if (!is_paging) vm.crit.pg_no = 1;
      sessionStorage.dtSrch = JSON.stringify(vm.crit);
      vm.results = [];
      await vm.doPost("doc_type_search", vm.crit,
        (b) => {
          vm.results = b;
          sessionStorage.myDtRes = JSON.stringify(vm.results);
        }, vm.setStatusMessage);
    },
    reset() {
      this.results = { items: [], has_next: false };
      this.crit = { pg_no: 1 };
      sessionStorage.myDtRes = undefined;
      sessionStorage.dtSrch = undefined;
    }
  }
};
</script>
