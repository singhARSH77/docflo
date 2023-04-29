import { createRouter, createWebHashHistory } from 'vue-router'
import Dummy from '../views/Dummy.vue'
import HomeView from '../views/HomeView.vue'
import UserDetails from '../views/UserDetails.vue'
import UserSearch from '../views/UserSearch.vue'
import FormAction from "../views/FormAction.vue"
import DocType from "../views/DocType.vue"
import DocItem from "../views/DocItem.vue"
import DocTypeSearch from "../views/DocTypeSearch.vue"
import DocItemSearch from "../views/DocItemSearch.vue"

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/dummy',
      name: 'Dummy',
      component: Dummy
    },
    {
      path: '/',
      name: 'HomeView',
      component: HomeView
    },
    {
      path: '/user/:id?',
      name: 'UserDetails',
      component: UserDetails
    },
    {
      path: '/user.find',
      name: 'UserSearch',
      component: UserSearch
    },
    {
      path: '/doc_type/:id?',
      name: 'DocType',
      component: DocType
    },
    {
      path: '/doc_item.find',
      name: 'DocItemSearch',
      component: DocItemSearch
    },
    {
      path: '/doc_item/:docTypeId/:id?',
      name: 'DocItem',
      component: DocItem,
      props: true
    },
    {
      path: '/doc_type.find',
      name: 'DocTypeSearch',
      component: DocTypeSearch
    },
    {
      path: '/form.actions',
      name: 'FormAction',
      component: FormAction
    }
  ]
})

export default router
