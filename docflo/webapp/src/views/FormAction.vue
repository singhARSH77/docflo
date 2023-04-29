<!--
Component for form actions.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <div class="card">
      <div class="card-header">
        <div class="float-start">Form Actions</div>
        <div class="float-end">
          <button class="btn btn-sm btn-outline-primary" @click="addActions">Add</button>
        </div>
      </div>
      <div class="card-body">
        <p v-if="formActions.length == 0">Nothing to show yet!</p>
        <div v-else>
          <div class="row fw-bold">
            <div class="col-md-2">S#. Form</div>
            <div class="col">User Role</div>
            <div class="col">Status (Current)</div>
            <div class="col">Action</div>
            <div class="col">Status (After)</div>
            <div class="col-md-3">Allowed for OU</div>
          </div>
          <div class="row mb-2" :class="{'border border-success': !pb.id}" v-for="(pb, i) in formActions" :key="pb.id">
            <div class="col-md-2">
              <div class="input-group">
                <span class="fw-bold me-2">{{i+1}}. </span>
                <select class="form-select" v-model="pb.doc_type">
                  <option v-for="x in allDocTypes" v-bind:value="x.id" :key="x.id">
                    {{ x.value }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col">
              <select class="form-select" v-model="pb.user_role ">
                <option v-for="x in SD.UserRoles" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
            <div class="col">
              <select class="form-select" v-model="pb.status_now" >
                <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
                <option value="ANY">Any type</option>
              </select>
            </div>
            <div class="col">
              <input class="form-control" type="text" v-model="pb.action" />
            </div>
            <div class="col">
              <select class="form-select" v-model="pb.status_after" >
                <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
                <option value="ANY">Any type</option>
              </select>
            </div>
            <div class="col-md-3">
              <div class="input-group">
                <select class="form-select" v-model="pb.allowed_ou">
                  <option value="*">All OUs</option>
                  <option value=".">User's OU</option>
                  <option value="-">Other</option>
                </select>
                <input v-if="pb.allowed_ou == '-'"  class="form-control" type="text" v-model="pb.allowed_ou">
                <button title="Save this item" class="btn btn-sm btn-outline-primary me-2" @click="saveItem(pb)"><i class="bi bi-save" role="button"></i></button>
                <button title="Copy this item as new row" class="btn btn-sm btn-outline-success me-2" @click="copyItem(pb)"><i class="bi bi-clipboard-plus" role="button"></i></button>
                <button title="Delete this item" class="btn btn-sm btn-outline-danger" @click="removeItem(pb)"><i class="bi bi-trash-fill"></i></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: "FormAction",
  data: function () {
    return {
      formActions: [],
      allDocTypes: []
    };
  },
  computed: { },
  async mounted() {
    console.log("Mounting FormAction");
    const vm = this;
    await vm.doGet("list_form_actions", b => { vm.formActions = b },
            vm.setStatusMessage)
    
    await vm.doGet("all_doc_types/1", b => { vm.allDocTypes = b },
            vm.setStatusMessage)
  },
  methods: {
    addActions() {
      this.formActions.push({})
    },
    async saveItem(obj) {
      if (!confirm("Confirm save?")) return
      const vm = this;
      await vm.doPost("fa_save", obj, 
        (b) => {
          obj.id = b.id
          vm.setStatusMessage("Saved the form action!")
        }, vm.setStatusMessage)
    },
    async removeItem(obj) {
      if (!confirm("Confirm delete?")) return
      const vm = this;
      vm.formActions = vm.formActions.filter(function(item) {
          return item.id !== obj.id
      })
      if (obj.id !== undefined) {
        await vm.doGet("fa_delete/"+obj.id, 
          vm.setStatusMessage, vm.setStatusMessage)
      }
    },
    copyItem(obj) {
      let cp = {}
      Object.assign(cp, obj)
      cp.id = undefined
      this.formActions.push(cp)
    }
  },
};
</script>
