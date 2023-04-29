<template>
    <button disabled class="btn btn-primary" v-if="!hasActions">Actions</button>
    <div v-else>
        <div class="input-group">
            <textarea class="form-control" v-model="note" rows="2"
            placeholder="A note is required for all actions."></textarea>
            <div class="btn-group">
                <div class="dropdown">
                    <button :disabled="noteEmpty" v-if="showActions" type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown"
                        aria-expanded="false">
                        {{ buttonLabel }}
                    </button>
                    <ul class="dropdown-menu">
                        <li v-for="act in roleActions" :key="act">
                            <a class="dropdown-item" @click.prevent="onAction(act)">{{
                                    act.label
                            }}</a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import _ from "lodash"
export default {
    name: "WorkflowActions",
    components: {},
    props: {
        showActions: {
            type: Boolean,
            default: true
        },
        buttonLabel: {
            type: String,
            default: "Actions",
        },
        roleActions: {
            type: Object,
            default: { }
        }
    },
    emits: ["actionSelected"],
    data: function () {
        return { note: "" };
    },
    computed: {
        hasActions() {
            return Object.keys(this.roleActions).length > 0
        },
        noteEmpty() {
            return _.isEmpty(this.note)
        }
    },
    async mounted() {
        console.log("Mounting WorkflowActions");
    },
    methods: {
        async onAction(act) {
            this.$emit("actionSelected", act, this.note)
        }
    },
};
</script>
