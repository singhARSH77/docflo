<!--
@author Balwinder Sodhi
-->
<template>
  <div>
    <label :for="elmId">{{docField.label}}</label>
    <input :id="elmId" :class="fieldClass" :type="fieldType"
      v-model="value"/>
  </div>
</template>

<script>

export default {
  name: "DocFieldComp",
  props: {'modelValue': null, "docField": Object},
  emits: ['update:modelValue'],
  data: function () {
    return { fieldClass: "form-control" };
  },
  async mounted() {
    console.log("Mounting DocFieldComp. Initial value="+
    this.modelValue+". docField="+JSON.stringify(this.docField));
  },
  computed: {
    elmId() {
      const f = this.docField
      return `d_${f.doc_type}_${f.id}_${f.field_type}`
    },
    isCheckbox() {
      return this.docField.field_type == "boolean"
    },
    value: {
      get() {
        if (this.isCheckbox) return "on" == this.modelValue
        else return this.modelValue
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    },
    fieldType() {
      let myType = "text"
      if (this.isCheckbox) {
        myType = "checkbox"
        this.fieldClass = "form-check-input ms-2"
      } else if (this.docField.field_type == "integer") {
        myType = "number"
      } else if (this.docField.field_type == "date") {
        myType = "date"
      } else {
        myType = "text"
      }
      return myType
    }
  },
  methods: { },
};
</script>
