<template>
  <v-container fluid>
    <v-row class="text-center">
      <v-col cols="12">
        <h2 class="subhead">{{ ssStore.song.title }} </h2>
        
        <div v-if="ssStore.song.author">{{ ssStore.song.author }}</div>

      </v-col>
      <v-col cols="12" sm="6" md="6">
        <h3 class="subhead">Song Usage</h3>
        <p>(Since August 2020)</p>
        <v-list v-for="sh in ssStore.song.history" :key="sh.id" class="text-left mx-auto app-list">
          <v-list-item class="text-left">
            <v-list-item-title>{{ sh.service_name }}<span v-if="sh.is_future">*</span></v-list-item-title>
            <v-list-item-subtitle>                
              {{ sh.event }} - {{ sh.arrangement }} <span v-if="sh.person_names != 'Sam Arnold'">[{{ sh.person_names }}]</span>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
        <div v-if="ssStore.song.history && ssStore.song.history.length"><br>* indicates planned future use</div>
        <div v-else>This song has not been used.</div>
        <div v-if="ssStore.isPicker" class="search-help">
          <h3>Step Three: Review Song Usage and Select Your Arrangement</h3>
          <ol>
            <li>Review Recent Usage - Check the “Song Usage” record (above) to see if the song has
            been used within the last few months (or if it is scheduled to be used in the near
            future).</li>
            <li>Select Arrangement - From the “Select Arrangement” list (on the right),
            choose the arrangement you would like to minister. Or if it is not listed choose "Use
            another arrangement."</li>
          </ol>
        </div>
      </v-col>
    
      <v-col cols="12" sm="6" md="6">
        <h3 class="subhead">Select Arrangement</h3>
        <p>Here are the arrangements in our database:</p>

        <v-list v-for="arr in arrangements" :key="arr.id" class="text-left mx-auto app-list">
          <v-list-item @click="arrangementSelected(arr)" :title="arr.name" class="text-left" append-icon="mdi-chevron-right">
          </v-list-item>
        </v-list> 

        <div class="mt-5"><v-progress-circular indeterminate v-if="loading" /></div>
        <!-- <v-btn v-if="ssStore.isPicker" @click="arrangementSelected()">
              Use another arrangement
        </v-btn> -->

      </v-col>

    </v-row>
  </v-container>

</template>

<style scoped>
  .v-list, .v-list-item { padding: 0px !important; }
  .search-help ol { margin-left: 20px; }
</style>

<script>

import { ssStore } from './SongSearchState.js'
import { siStore } from './ServiceItemState.js'

export default {
  name: 'SongSearchArrangements',

  data: () => ({
    loading: false,
    ssStore: ssStore
  }),

  computed: {
    arrangements() {
      if (ssStore.isPicker)
        return [...ssStore.arrList, {name: "Use another arrangement"}]
      else
        return ssStore.arrList
    }
  },

  methods: {

    async arrangementSelected(arrangement) {
      if (arrangement.id) {
        console.log(arrangement, 'selected')
        ssStore.arrangement = arrangement
        this.loading = true
        try {
          ssStore.arrangement = await this.$api.getArrangement(ssStore.song.id, ssStore.arrangement.id)      

        } finally {
          this.loading = false
        }        
        this.$router.push( { name: 'SongSearchArrangementsDetail' })
      } else {
        ssStore.arrangement = {}
        this.finishEntry()
      }

    },

    async finishEntry() {
      ssStore.finishEntry(this.$api, siStore)
      this.$router.go(-2)
    },

  },

  async mounted() {
    scrollTo(0,0)

  }
}
</script>
