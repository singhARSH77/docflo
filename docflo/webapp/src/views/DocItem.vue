<!--
Component for searching doc types.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Doc Item</h5>
    <div>
      <div class="row mb-2">
        <div class="col-md-2">
          <label for="diStatus">Status</label>
          <select class="form-select" id="diStatus" v-model="doc_item.status" 
            disabled="disabled">
            <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select> 
        </div>
        <div class="col-md-6">
          <label for="dfile" class="form-label">Doc Files</label>
          <input :disabled="viewOnly" class="form-control" type="file"
          id="dfile" ref="dataFiles" multiple />
          <span v-if="doc_item.doc_files.length > 0">
            <a class="me-4" v-for="f in doc_item.doc_files" :key="f" 
              :href="'get_file/'+f">{{toFileName(f)}}</a>
          </span>
        </div>
        <div class="col-md-4">
          <label for="actn" class="form-label">Action Note</label>
          <workflow-actions :button-label="Actions" 
            :role-actions="actions" @action-selected="onAction" />
        </div>
      </div>
      <div class="card">
        <div class="card-body">
          <div class="row row-cols-3">
            <div class="col" v-for="df in doc_fields" :key="df.id">
              <doc-field-comp :doc-field="df" 
              v-model="doc_item['__DF'+df.id]"/>
            </div>
          </div>
        </div>
      </div>
      <div class="card mt-2">
        <div class="card-header">Notes History</div>
        <div class="card-body">
          <div class="row hdr-row">
            <div class="col-md-1">S#</div>
            <div class="col-md-2">Note By</div>
            <div class="col-md-2">Date</div>
            <div class="col">Note</div>
          </div>
          <div v-if="doc_item.doc_notes.length == 0" class="row"><div class="col-md-12">Nothing to show yet!</div></div>
          <div v-else class="row border-top" v-for="(n, i) in doc_item.doc_notes" :key="n">
            <div class="col-md-1">{{i+1}}</div>
            <div class="col-md-2">
              {{n.author.first_name + " " + n.author.last_name +
              " (" + n.author.email+") " + n.author.org_unit}}</div>
            <div class="col-md-2">{{fmtDate(n.ins_ts)}}</div>
            <div class="col">{{n.note}}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import WorkflowActions from './WorkflowActions.vue';
import DocFieldComp from './DocFieldComp.vue';
export default {
  name: "DocItem",
  components: {
    WorkflowActions, DocFieldComp
  },
  // Will be set by the router definition
  props: ["docTypeId", "id"],
  data: function () {
    return {
      doc_item: {status: "DRA", doc_notes: [], doc_files: []  },
      doc_fields: [], actions: []
    };
  },
  computed: {
    isEdit() {
      return this.id > 0;
    }
  },
  async mounted() {
    console.log("Creating DocItem");
    const vm=this;
    vm.doc_item.doc_type = vm.docTypeId
    await vm.loadDocFields()
    if (vm.isEdit) await vm.load()
    await vm.getDocTypeActions(vm.docTypeId, vm.doc_item.status,
                            (b)=>{vm.actions = b;})
  },
  methods: {
    addFileToPayload(payload, elm, propName) {
      if (elm.files.length > 0) {
        for (let i = 0; i < elm.files.length; i++) {
          const f = elm.files[i];
          payload.set(propName, f, f.name);
        }
      } else {
        console.debug("No file is being uploaded.")
      }
    },
    async onAction(act, note) {
      if (!confirm("Confirm action?")) return;
      console.log("Action: " + JSON.stringify(act));
      // Action 'arg' has the status value to be set
      this.doc_item.status = act.arg
      this.doc_item.action_note = note
      await this.save()
    },
    async save() {
      let vm = this;
      console.log("DocItem details: "+JSON.stringify(vm.doc_item))
      try {
        const payload = new FormData();
        for (const [key, value] of Object.entries(vm.doc_item)) {
          payload.set(key, value);
        }
        vm.addFileToPayload(payload, vm.$refs.dataFiles, "dataFiles");
        const cfg = { headers: { "Content-Type": "multipart/form-data" } };
        let res = await vm.$http.post("doc_item_save", payload, cfg);
        if (res.data.status == "OK") {
          vm.doc_item = res.data.body;
          if(!vm.isEdit) {
            vm.$router.push({path: `/doc_item/${vm.docTypeId}/${vm.doc_item.id}`, query: { nr: 1}});
          } else {
            vm.setStatusMessage("Saved the Doc Item!");
          }
          vm.action_note = ""
        } else {
          vm.setStatusMessage(res.data.body);
        }
      } catch (error) {
        console.log(error);
        vm.setStatusMessage("Error: " + error);
      }
    },
    async load() {
      let vm = this;
      console.log("Loading doc item details. id=" + vm.id);
      await vm.doGet(`doc_item_get/${vm.id}`, (b) => { vm.doc_item = b; },
        vm.setStatusMessage)
    },
    async loadDocFields() {
      let vm = this;
      console.log("Loading doc fields for id=" + vm.docTypeId);
      await vm.doGet(`dtf_get/${vm.docTypeId}`, (b) => { vm.doc_fields = b; },
        vm.setStatusMessage)
    },
    async clear() {
      this.doc_item = {status: "DRA", doc_notes: [], doc_files: [],
                      doc_type: this.docTypeId }
      this.doc_fields = []
    }
  }
};
</script>
