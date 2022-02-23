<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <!-- <v-progress-circular indeterminate v-if="loading" /> -->

        <h2 class="subhead">{{ ssStore.song.title }} </h2>
        
        <h3>Arrangement: {{ ssStore.arrangement.name }}</h3>
        <div v-if="ssStore.arrangement.composer">Composer: {{ ssStore.arrangement.composer }}</div>
        <div v-if="ssStore.arrangement.arranger">Arranger: {{ ssStore.arrangement.arranger }}</div>
        <h3 class="subhead">Recent Usage</h3>
        <v-list v-for="sh in ssStore.arrangement.history" :key="sh.id" class="text-left mx-auto app-list">
          <v-list-item two-line class="text-left">
            <v-list-item-header>
              <v-list-item-title>{{ sh.service_date }} {{ sh.service_time.substring(0, 5) }}</v-list-item-title>
              <v-list-item-subtitle>{{ sh.event }} [{{ sh.person_names }}]</v-list-item-subtitle>
            </v-list-item-header>
          </v-list-item>                       
        </v-list>
        <div v-if="ssStore.arrangement.history && !ssStore.arrangement.history.length">This arrangement has not been used.</div>

        <br><br>
        <v-btn v-if="ssStore.isPicker" @click="confirmArrangement()">
          Choose Arrangement
        </v-btn>
        <br><br>
        <div v-html="ssStore.arrangement.lyrics.replace(/\n/g, '<br>')">
        
        </div>

        
      </v-col>

    </v-row>
  </v-container>

</template>

<style>
  h4 { margin-top: 20px }
</style>

<script>

import { ssStore } from './SongSearchState.js'
import { siStore } from './ServiceItemState.js'

export default {
  name: 'SongSearchArrangementsDetail',

  data: () => ({
    // loading: false,
    ssStore: ssStore
  }),

  methods: {

    async confirmArrangement() {
      ssStore.finishEntry(this.$api, siStore)
      this.$router.go(-3)
    },


  },

  async mounted() {

  }
}
</script>
