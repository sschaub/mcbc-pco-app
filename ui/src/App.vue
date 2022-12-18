<template>
  <v-app>
          <v-app-bar class="no-print"
            color="blue">
            <v-icon v-if="$route.name != 'Home'" @click="$router.go(-1)" class="back-arrow">mdi-chevron-left</v-icon>
            <v-app-bar-title>MCBC Music</v-app-bar-title>
            <v-spacer></v-spacer>
            <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
          </v-app-bar>

          <v-navigation-drawer
            v-model="drawer"
            location="right"
            temporary>
            <v-list>
              <v-list-item @click="navToPage('/')">
                Home
              </v-list-item>
              <v-list-item @click="navToPage('/my-services')">
                My Services
              </v-list-item>
              <v-list-item @click="toSongSearch()">
                Song Search
              </v-list-item>
              <v-list-item @click="navigateTo(`${schedule_prefix}/history`)">
                History
              </v-list-item>
              <v-list-item @click="navigateTo(`${schedule_prefix}/pdf`)">
                View Schedule
              </v-list-item>
              <v-list-item @click="navigateTo('https://www.mcbcmusic.org/')">
                Music Website
              </v-list-item>
              <v-list-item v-if="isAdmin()" @click="navToPage('/admin')">
                Admin
              </v-list-item>
              <v-list-item @click="navigateTo('https://www.mcbcmusic.org/home/lyrics-app-help')">
                Help
              </v-list-item>
              <v-list-item v-if="getUser()" @click="logout()">
                Logout
              </v-list-item>
              <!-- TODO: Add Song Search Here -->
            </v-list>
          </v-navigation-drawer>
          <v-main>
            <v-sheet border>
              <router-view/>    
            </v-sheet>
          </v-main>
  </v-app>
</template>

<style scoped>
.back-arrow { cursor: pointer }
</style>

<style>
.app-list { max-width: 400px; }
.subhead { margin-top: 20px; margin-bottom: 10px;  }
.error { color: red } /* color: var(--v-error-base) */
.ssbreadcrumb { margin-top: 10px; }
.ssbreadcrumb a { color: black;  }
.ssdropdown {
  appearance: auto; 
  border: 2px solid black; 
}

.search-help { 
  max-width: 600px; 
  margin: 0 auto;
  margin-top: 10px; 
  text-align: left; 
  font-style: italic; 
  background-color: lightblue; 
  border-color: black; 
  padding: 20px; 
}

@media print {
  .no-print {
    display: none !important
  }
}

</style>

<script>

import {SCHEDULE_PREFIX} from './constants.js';

import { ssStore } from './views/SongSearchState.js'

export default {
  name: 'App',

  // components: {

  //   About
  // },

  data: () => ({
    drawer: false,
    schedule_prefix: SCHEDULE_PREFIX,
    items: [
      { title: 'Hi', value: 'bye' }
    ]
    // global state goes here
  }),

  methods: {
    navigateTo(url) {
      window.open(url)
      this.drawer = false
    },
    navToPage(path) {
      this.$router.push(path)
      this.drawer = false
    },
    toSongSearch() {
      ssStore.init(false)
      this.$router.push('/songs')
      this.drawer = false
    },
    logout() {
      localStorage.removeItem('api_auth')
      localStorage.removeItem('user')
      this.drawer = false
      this.$router.replace('/login')
    }
  },

  mounted() {
    
  }

}
</script>
