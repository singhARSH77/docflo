<!--
Component for user lookup using typeahead.

@author Balwinder Sodhi
-->
<template>
  <vue-bootstrap-typeahead
        placeholder="Type part of name."
        :initialValue="initialValue"
        :data="users"
        :serializer="s => (s.first_name + ' ' +s.last_name )"
        @mta-item-selected="onUserSelect"
        @mta-input-changed="debouncedQuery"
        />
</template>

<script>
import _ from "lodash";
import VueBootstrapTypeahead from "./VueBootstrapTypeahead.vue";

export default {
  name: "UserLookupComp",
  components: {VueBootstrapTypeahead},
  props: { "initialValue": String },
  emits: ["userSelected"],
  data: function () {
    return { users: [], selectedValue: "" };
  },
  async mounted() {
    console.log("Mounting UserLookupComp. Initial value="+this.initialValue);
  },
  methods: {
    onUserSelect(c) {
      console.log("Selected user: " + JSON.stringify(c));
      this.$emit("userSelected", c)
    },
    debouncedQuery: _.debounce(async function(inp) {
      await this.lookupUser(inp)
    }, 400),
    async lookupUser(query) {
      let vm = this;
      console.log("Looking up user: "+query);
      if (_.isEmpty(query) || query.length < 3) {
        console.log("Min. 3 charaters needed. Ignored.");
        return;
      }
      await vm.doGet(`user_lookup/${query}`,
        (b)=>{vm.users = b}, vm.setStatusMessage)
    },
  },
};
</script>
