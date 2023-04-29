<!--
Component for leave rules.

@author Balwinder Sodhi
-->
<template>
  <div class="card">
    <div class="card-header">
      <span>Doc Type</span>
      <a class="btn btn-outline-success float-end" href="#/doc_type">Add Another</a>
    </div>
    <div class="card-body">
      <div class="row mb-2">
        <div class="col-md-3">
          <label for="doc_name">Name</label>
          <input type="text" required class="form-control" id="doc_name"
          v-model="doc_type.name" :disabled="viewOnly" />
        </div>
        <div class="col-md-3">
          <label for="grp">Group Name</label>
          <input type="text" required class="form-control" id="grp"
          v-model="doc_type.group" :disabled="viewOnly" />
        </div>
        <div class="col">
          <label for="docdesc">Description</label>
          <input type="text" required class="form-control" id="docdesc"
          v-model="doc_type.description" :disabled="viewOnly" />
        </div>
        <div class="col-md-2">
          <span class="float-end mt-4" v-if="!viewOnly">
            <button type="button" class="btn btn-sm btn-outline-primary me-2" @click="saveDocType">Save</button>
            <button type="button" class="btn btn-sm btn-outline-danger" @click="reset">Clear</button>
          </span>
        </div>
      </div>
    </div>
    <div class="card-header">
      <span>Doc Fields</span>
      <span class="float-end" v-if="!viewOnly">
        <button type="button" class="btn btn-sm btn-outline-primary me-2" @click="addDocField">Add</button>
      </span>
    </div>
    <div class="card-body">
      <p v-if="!hasFields">Nothing to show yet!</p>
      <div v-else>
        <div class="row fw-bold">
          <div class="col-md-1">S#.</div>
          <div class="col-md-2">Field Name</div>
          <div class="col-md-2">Field Type</div>
          <div class="col-md-1">Optional</div>
          <div class="col-md-1">Finder</div>
          <div class="col-md-1">Display Seq.</div>
          <div class="col">Label</div>
        </div>
        <div class="row mb-2" :class="{'border border-success': !pb.id}"
          v-for="(pb, i) in doc_type.doc_fields" :key="pb.id">
          <div class="col-md-1">
            <span class="fw-bold me-2">{{i+1}}.</span>
          </div>
          <div class="col-md-2">
            <div class="input-group">
              <input class="form-control" type="text" v-model="pb.name" />
            </div>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="pb.field_type ">
              <option v-for="x in SD.DocFieldTypes" v-bind:value="x.id" :key="x.id">
                {{ x.value }}
              </option>
            </select>
          </div>
          <div class="col-md-1">
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="checkbox" v-model="pb.optional">
            </div>
          </div>
          <div class="col-md-1">
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="checkbox" v-model="pb.finder">
            </div>
          </div>
          <div class="col-md-1">
            <input class="form-control" type="number" min="0" v-model="pb.display_seq" />
          </div>
          <div class="col">
            <div class="input-group">
              <input class="form-control" type="text" v-model="pb.label" />
              <button title="Save this item" class="btn btn-sm btn-outline-primary me-2" @click="saveItem(pb)"><i class="bi bi-save" role="button"></i></button>
              <button title="Copy this item as new row" class="btn btn-sm btn-outline-success me-2" @click="copyItem(pb)"><i class="bi bi-clipboard-plus" role="button"></i></button>
              <button title="Delete this item" class="btn btn-sm btn-outline-danger" @click="removeItem(pb)"><i class="bi bi-trash-fill"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash"

export default {
  name: "DocType",
  components: {},
  data: function () {
    return { doc_type: { doc_fields: []} }
  },
  async mounted() {
    console.log("Mounting Doc Type");
    let vm = this;
    try {
      if (vm.isEdit) {
        await vm.load();
      } else {
        vm.reset();
      }
      if (vm.$route.query["nr"] == 1) {
        vm.setStatusMessage("Saved the doc type!");
        vm.$route.query = {};
      }
    } catch (error) {
      vm.setStatusMessage(error)
    }
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    },
    hasFields() {
      return this.doc_type !== undefined && 
      this.doc_type.doc_fields !== undefined &&
      this.doc_type.doc_fields.length > 0
    }
  },
  methods: {
    async reset() {
      this.doc_type = {doc_fields: []}
    },

    async load() {
      let vm = this;
      let uid = vm.$route.params.id;
      let error = false
      console.log("Loading doc type. id=" + uid);
      await vm.doGet(`doc_type/${uid}`, (b) => { vm.doc_type = b; },
        (b)=> {error = b})
      if (error) throw error
    },
    isValid() {
      return !(_.isEmpty(this.doc_type.name));
    },
    async saveDocType() {
      let vm = this;
      if (!this.isValid()) {
        vm.setStatusMessage("Please supply all required fields!");
        return;
      }
      if (!confirm("Confirm save?")) {
        return;
      }
      console.log("Saving doc type details.");
      await vm.doPost("doc_type_save", vm.doc_type,
        (b) => {
          vm.doc_type = b;
          vm.setStatusMessage("Saved successfully!");
          if (!vm.isEdit) {
            vm.$router.push({ path: "/doc_type/" + vm.doc_type.id, query: { nr: 1 } });
          }
        }, vm.setStatusMessage);
    },

    async addDocField() {
      let dt = this.doc_type
      if (!this.hasFields) dt.doc_fields = []
      dt.doc_fields.push({"doc_type": dt.id})
    },

    async saveItem(obj) {
      let vm = this;
      if (!confirm("Confirm save?")) {
        return;
      }
      console.log("Saving doc type field.");
      await vm.doPost("dtf_save", obj,
        (b) => {
          Object.assign(obj, b)
          vm.setStatusMessage("Saved successfully!");
        }, vm.setStatusMessage);
    },

    async copyItem(obj) {
      let cp = {}
      Object.assign(cp, obj)
      cp.id = undefined
      this.doc_type.doc_fields.push(cp)
    },

    async removeItem(obj) {
      if (!confirm("Confirm delete?")) return
      const vm = this;
      let df = vm.doc_type.doc_fields;
      vm.doc_type.doc_fields = df.filter(function(item) {
          return item.id !== obj.id
      });
      if (obj.id !== undefined) {
        await vm.doGet("dtf_delete/"+obj.id, 
          (b)=>{
            vm.setStatusMessage(b);
          }
          , vm.setStatusMessage)
      }     
    }

  },
};
</script>
