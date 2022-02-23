<template>
  <v-app>
          <v-app-bar
            color="blue">
            <v-icon v-if="$route.name != 'Home'" @click="$router.go(-1)" class="back-arrow">mdi-chevron-left</v-icon>
            <v-spacer></v-spacer>
            <v-app-bar-title>MCBC Music</v-app-bar-title>
            <v-spacer></v-spacer>
            <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
          </v-app-bar>

          <v-navigation-drawer
            v-model="drawer"
            position="right"
            temporary>
            <v-list>
              <v-list-item @click="navToPage('/')">
                <v-list-item-header>Home</v-list-item-header>
              </v-list-item>
              <v-list-item @click="toSongSearch()">
                <v-list-item-header>Song Search</v-list-item-header>
              </v-list-item>
              <v-list-item @click="navigateTo('https://schedule.mcbcmusic.org/history')">
                <v-list-item-header>History</v-list-item-header>
              </v-list-item>
              <v-list-item @click="navigateTo('https://schedule.mcbcmusic.org/pdf')">
                <v-list-item-header>View Schedule</v-list-item-header>
              </v-list-item>
              <v-list-item @click="navigateTo('https://www.mcbcmusic.org/')">
                <v-list-item-header>Music Website</v-list-item-header>
              </v-list-item>
              <v-list-item v-if="isAdmin()" @click="navigateTo('https://schedule.mcbcmusic.org/menu')">
                <v-list-item-header>Admin</v-list-item-header>
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
</style>

<script>

import { ssStore } from './views/SongSearchState.js'

export default {
  name: 'App',

  // components: {

  //   About
  // },

  data: () => ({
    drawer: false,
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
    }
  },

  mounted() {
    
  }

}
</script>
