import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import MyServices from '../views/MyServices.vue'
import Service from '../views/Service.vue'
import ServiceItem from '../views/ServiceItem.vue'
import ServiceItemEdit from '../views/ServiceItemEdit.vue'
import ServiceItemReview from '../views/ServiceItemReview.vue'
import SongSearch from '../views/SongSearch.vue'
import SongSearchArrangements from '../views/SongSearchArrangements.vue'
import SongSearchArrangementsDetail from '../views/SongSearchArrangementsDetail.vue'
import About from '../views/About.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/my-services',
    name: 'MyServices',
    component: MyServices
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },

  {
    path: '/service/:service_id',
    name: 'Service',
    component: Service,
    props: true

    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    //component: () => import(/* webpackChunkName: "about" */ '../views/Sesrvice.vue')
  },

  {
    path: '/service/:service_id/:item_id',
    name: 'ServiceItem',
    component: ServiceItem,
    props: true
  },

  {
    path: '/service/:service_id/:item_id/edit',
    name: 'ServiceItemEdit',
    component: ServiceItemEdit,
    props: true
  },

  {
    path: '/service/:service_id/:item_id/review',
    name: 'ServiceItemReview',
    component: ServiceItemReview,
    props: true
  },

  {
    path: '/songs',
    name: 'SongSearch',
    component: SongSearch
  },

  {
    path: '/songs/arrangements',
    name: 'SongSearchArrangements',
    component: SongSearchArrangements
  },

  {
    path: '/songs/arrangements/detail',
    name: 'SongSearchArrangementsDetail',
    component: SongSearchArrangementsDetail
  },

  {
    path: '/login',
    name: 'Login',
    component: Login
  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  // Set default page title each time navigation occurs
  // Override this in the mounted() callback on individual pages
  document.title = 'MCBC Music System';

  next();
});

export default router
