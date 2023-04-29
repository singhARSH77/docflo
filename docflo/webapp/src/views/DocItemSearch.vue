<!--
Component for searching doc items.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Find Doc Items</h5>
    <div class="row mt-2 mb-2">
      <div class="col-md-10">
        <div class="input-group float-end">
          <span class="input-group-text">Doc Type:</span>
          <select class="form-select" v-model="doc_type_grp">
            <option v-for="x in Object.keys(allDocTypes)" v-bind:value="x" :key="x">
              {{ x }}
            </option>
          </select>
          <select class="form-select" :disabled="doc_type_grp==undefined"
            v-model="crit.doc_type" @change="fetchFinderFields">
            <option v-for="x in allDocTypes[doc_type_grp]" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
        </div>
      </div>
      <div v-if="crit.doc_type > 0" class="col-md-2">
        <button class="btn btn-outline-success me-2" type="button" 
        @click="find(false)">
            <i class="bi bi-search"></i>
        </button>
        <button class="btn btn-outline-danger me-2" @click="reset" type="button">
          <i class="bi bi-eraser"></i>
        </button>
        <a class="btn btn-outline-primary" :href="`#/doc_item/${crit.doc_type}`">Add</a>
      </div>
    </div>
    <div class="row">
      <div class="col-md-2">
        <label for="diStatus">Status</label>
        <select class="form-select" id="diStatus" v-model="crit.status">
          <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
            {{ x.value }}
          </option>
        </select> 
      </div>
      <div class="col-md-2">
        <label for="diNote">Notes Contain</label>
        <input id="diNote" type="text" class="form-control" v-model="crit.note"/>
      </div>
      <div class="col-md-2">
        <label for="filesCt">Files Count</label>
        <div class="input-group">
          <input id="filesCt" type="number" class="form-control" 
          min="0" max="50" v-model="crit.min_files" placeholder="Min."/>
          <span class="input-group-text">To</span>
          <input type="number" class="form-control" 
          :min="crit.min_files" max="50" v-model="crit.max_files"
          placeholder="Max."/>
        </div>
      </div>
      <div class="col">
        <label for="createdBy">Created By</label>
        <user-lookup-comp @userSelected="onCreatorSelect"/>
      </div>
      <div class="col">
        <label for="updBy">Updated By</label>
        <user-lookup-comp @userSelected="onUpdaterSelect"/>
      </div>
    </div>
    <div class="row row-cols-3">
      <div class="col" v-for="df in critFields" :key="df.id">
        <doc-field-comp :doc-field="df" v-model="crit['__DF'+df.id]"/>
      </div>
    </div>

    <div class="card mt-2">
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
          <div class="col">Details</div>
        </div>
        <p v-if="!hasResults">Nothing to show yet!</p>
        <div v-else class="row row-striped mt-4" v-for="(r, i) in results.items" :key="r.id">
          <div class="col-md-1">{{ (results.pg_no - 1) * results.pg_size + i + 1 }}</div>
          <div class="col-md-2">
            <a :href="'#/doc_item/' + r.doc_type.id + '/' + r.id">
              {{r.doc_type.group}}/{{r.doc_type.name}}
            </a>
          </div>
          <div class="col">
            Status: {{labelFor(SD.WfStatuses, r.status)}}. 
            Created by {{r.ins_by}} on {{fmtDate(r.ins_ts)}}.
            Last updated on {{fmtDate(r.upd_ts)}}.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserLookupComp from "./UserLookupComp.vue";
import DocFieldComp from './DocFieldComp.vue';
export default {
  name: "DocItemSearch",
  components: {
    UserLookupComp, DocFieldComp
  },
  data: function () {
    return {
      doc_type_grp: undefined,
      allDocTypes: {},
      critFields: [],
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
  async mounted () {
    console.log("Mounting DocItemSearch");
    const vm = this
    await vm.doGet("all_doc_types/0", b => { vm.allDocTypes = b },
            vm.setStatusMessage)
    if (sessionStorage.ditSrch) {
      vm.crit = JSON.parse(sessionStorage.ditSrch);
    }
    if (sessionStorage.myDitRes) {
      vm.results = JSON.parse(sessionStorage.myDitRes);
    } else {
      vm.results = { items: [], has_next: false };
    }
  },
  methods: {
    onCreatorSelect(usr) {
      this.crit.creator = usr.id
    },
    onUpdaterSelect(usr) {
      this.crit.updater = usr.id
    },
    async fetchFinderFields() {
      let vm = this;
      await vm.doGet(`dtff_get/${vm.crit.doc_type}`, 
        (b) => { vm.critFields = b; },
        vm.setStatusMessage)
    },
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
      sessionStorage.ditSrch = JSON.stringify(vm.crit);
      vm.results = [];
      await vm.doPost("doc_item_search", vm.crit,
        (b) => {
          vm.results = b;
          sessionStorage.myDitRes = JSON.stringify(vm.results);
        }, vm.setStatusMessage);
    },
    reset() {
      this.critFields = []
      this.results = { items: [], has_next: false };
      this.crit = { pg_no: 1 };
      sessionStorage.myDitRes = undefined;
      sessionStorage.ditSrch = undefined;
    }
  }
};
</script>
