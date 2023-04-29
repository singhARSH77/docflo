import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import _ from "lodash";
const app = createApp(App)
app.config.globalProperties.$http = axios
app.mixin({
    methods: {
        setStaticData(sd) {
            this.$root.staticData = sd;
        },
        setStatusMessage(msg) {
            console.log("Status message event: " + msg);
            this.$root.statusMessage = msg;
        },
        setCurrentUser(user) {
            this.$root.user = user;
        },
        labelFor(items, key) {
            if (!items || !key) return "--";
            let obj = items.find(elm => elm.id == key);
            if (obj) {
                return obj.value;
            }
        },
        fmtNum(n_str, dp = 2) {
            try {
                let f = parseFloat(n_str);
                return f.toFixed(dp);
            } catch (err) {
                console.error("fmtNum: failed to parse as float. " + err);
                return n_str;
            }
        },
        toFileName(fp) {
            if (_.isEmpty(fp)) return "N/A"
            return fp.substring(fp.lastIndexOf("_._") + 3)
        },
        fmtDate(dt) {
            const d = new Date(dt)
            return d.toLocaleString()
        },
        async doPost(url, postData, onOk, onError) {
            await this.doHttp(false, url, postData, onOk, onError)
        },
        async doGet(url, onOk, onError) {
            await this.doHttp(true, url, null, onOk, onError)
        },
        async doHttp(isGet, url, postData, onOk, onError) {
            let vm = this;
            try {
                const res = isGet ? await vm.$http.get(url) : await vm.$http.post(url, postData);
                if (res.data.status == "OK") {
                    onOk(res.data.body)
                } else {
                    onError(res.data.body)
                }
            } catch (error) {
                console.log(error);
                vm.setStatusMessage("Error occurred when contacting the server.");
            }
        },
        async getDocTypeActions(doc_type_id, status, onOk) {
            let vm = this;
            await vm.doGet(`my_form_actions/${doc_type_id}/${status}`,
                    onOk, vm.setStatusMessage)
        },
        isUserOrAdmin(userId) {
            return this.isAdmin || userId == this.currentUser.id
        }
    },
    computed: {
        viewOnly: {
            get: function () {
                return this.$root.viewOnlyFlag;
            },
            // setter
            set: function (newValue) {
                return this.$root.viewOnlyFlag = newValue;
            }
        },
        SD() {
            return this.$root.staticData;
        },
        currentUser() {
            return this.$root.user;
        },
        isOAuth: {
            get: function () {
                return this.$root.is_oauth;
            },
            set: function (val) {
                return this.$root.is_oauth = val;
            }
        },
        statusMsg() {
            return this.$root.statusMessage;
        },
        authenticated() {
            return this.$root.user.email !== undefined
        },
        userRole() {
            return this.$root.user.role
        },
        isAdmin() {
            return this.$root.user.role == "SUP";
        },
        isDean() {
            return this.$root.user.role == "DEA";
        },
        isDir() {
            return this.$root.user.role == "DIR";
        },
        isHOD() {
            return this.$root.user.role == "HOD";
        },
        isManager() {
            return this.$root.user.role == "MGR";
        },
        isStaff() {
            return this.$root.user.role == "STA";
        },
        loginId() {
            return this.$root.user.email
        }
    }
});

app.use(router);

app.mount('#app');
