<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div>
          <span class="title">{{ ssStore.song.title }}</span>
            <span v-if="isAdmin()" style="margin-left: 10px">              
              <a :href="`https://services.planningcenteronline.com/songs/${ssStore.song.id}`" target="_blank">[pco]</a>
           </span>
        </div>
        
        <div><span class="subhead">Arrangement: {{ ssStore.arrangement.name }}</span>  
          <a v-if="isAdmin()" style="margin-left: 10px" 
             :href="`https://services.planningcenteronline.com/songs/${ssStore.song.id}/arrangements/${ssStore.arrangement.id}`" target="_blank">[pco]</a></div>
        <div v-if="ssStore.arrangement.composer">Composer: {{ ssStore.arrangement.composer }}</div>
        <div v-if="ssStore.arrangement.arranger">Arranger: {{ ssStore.arrangement.arranger }}</div>
        <br>
        <v-btn v-if="ssStore.isPicker" @click="confirmArrangement()">
          Choose Arrangement
        </v-btn>
      </v-col>
      <v-col cols="12" sm="6" md="6">

        <h3 class="subhead">Arrangement Usage</h3>
        <v-list v-for="sh in ssStore.arrangement.history" :key="sh.id" class="text-left mx-auto app-list">
          <v-list-item class="text-left">
            <v-list-item-title>{{ sh.service_name }}<span v-if="sh.is_future">*</span></v-list-item-title>
            <v-list-item-subtitle>                
              {{ sh.event }} <span v-if="sh.person_names != 'Sam Arnold'">[{{ sh.person_names }}]</span>
            </v-list-item-subtitle>
          </v-list-item>                       
        </v-list>
        <div v-if="ssStore.arrangement.history && ssStore.arrangement.history.length"><br>* indicates planned future use</div>
        <div v-else>This arrangement has not been used.</div>


      </v-col>
      <v-col cols="12" sm="6" md="6">
        <song-lyrics :lyrics="ssStore.arrangement.lyrics" />
      </v-col>

    </v-row>
  </v-container>

</template>

<style>
  h4 { margin-top: 20px }
  .title { font-size: 24px; font-weight: bold;}
  .subhead { font-size: 16px; font-weight: bold;}
</style>

<script>

import SongLyrics from './SongLyrics.vue'
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
    scrollTo(0,0)
  },

  
  components: {
    SongLyrics
  }  
}
</script>
