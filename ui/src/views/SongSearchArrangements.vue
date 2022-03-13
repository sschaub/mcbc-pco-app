<template>
  <v-container fluid>
    <v-row class="text-center">
      <v-col cols="12">
        <h2 class="subhead">{{ ssStore.song.title }} </h2>
        
        <div v-if="ssStore.song.author">{{ ssStore.song.author }}</div>

      </v-col>
      <v-col cols="12" sm="6" md="6">
        <div v-if="ssStore.isPicker" class="help">
          <h3>Step Two: Review Song Usage and Select Your Arrangement</h3>
          <p>Look at the song usage report below to see how recently this song has been used (and if it is scheduled
            to be used in the near future). Then, select your arrangement from our list, or pick "Use another arrangement"
            if yours isn't listed.
          </p>
        </div>
        <h3 class="subhead">Song Usage</h3>
        <v-list v-for="sh in ssStore.song.history" :key="sh.id" class="text-left mx-auto app-list">
          <v-list-item two-line class="text-left">
            <v-list-item-header>
              <v-list-item-title>{{ sh.service_name }}<span v-if="sh.is_future">*</span></v-list-item-title>
              <v-list-item-subtitle>                
                {{ sh.event }} - {{ sh.arrangement }} <span v-if="sh.person_names != 'Sam Arnold'">[{{ sh.person_names }}]</span></v-list-item-subtitle>
            </v-list-item-header>
          </v-list-item>
        </v-list>
        <div v-if="ssStore.song.history && ssStore.song.history.length"><br>* indicates planned future use</div>
        <div v-else>This song has not been used.</div>
      </v-col>
    
      <v-col cols="12" sm="6" md="6">
        <h3 class="subhead">Select Arrangement</h3>
        <p>Here are the arrangements in our database:</p>

        <v-list v-for="arr in ssStore.arrList" :key="arr.id" class="text-left mx-auto app-list">
          <v-list-item @click="arrangementSelected(arr)" class="text-left">
            <v-list-item-header>
              <v-list-item-title>{{ arr.name }}</v-list-item-title>
            </v-list-item-header>
            <v-icon color="indigo">
              mdi-chevron-right
            </v-icon>
          </v-list-item>
        </v-list> 

        <br><br>
        <v-btn v-if="ssStore.isPicker" @click="arrangementSelected()">
              Use another arrangement
        </v-btn>

        
      </v-col>

    </v-row>
  </v-container>

</template>

<style scoped>
  .v-list, .v-list-item { padding: 0px !important; }  
  .help { max-width: 600px; margin: 0 auto; text-align: left; }
</style>

<script>

import { ssStore } from './SongSearchState.js'
import { siStore } from './ServiceItemState.js'

export default {
  name: 'SongSearchArrangements',

  data: () => ({
    // loading: false,
    ssStore: ssStore
  }),

  methods: {

    async arrangementSelected(arrangement) {
      if (arrangement) {
        console.log(arrangement, 'selected')
        ssStore.arrangement = arrangement
        // this.loading = true
        try {
          ssStore.arrangement = await this.$api.getArrangement(ssStore.song.id, ssStore.arrangement.id)      

        } finally {
          // this.loading = false
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
