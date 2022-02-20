<template>
  <div v-if="!siStore.service.name" class="text-center">
    <v-progress-circular indeterminate />
  </div>
  <v-container v-else fluid>
    <v-row class="text-center">
      <v-col cols="12">

        <h3>{{ siStore.service.name }}</h3>
        <h2>{{ siStore.item.description}}</h2>
        <div v-if="siStore.item.title">
          Scheduled Title: {{ siStore.item.title }}
        </div>
        <div>
          Proposed Title: {{ siStore.sched_item.title }}
          <v-btn @click="changeSong()">Change</v-btn>
        </div>
        <p v-if="siStore.sched_item.arrangement_name">Arrangement: {{ siStore.sched_item.arrangement_name }}</p>
                  
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <h3 class="subhead">Instrumentation / Personnel</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.genre_note" label="Type of Number (Vocal solo, violin duet, etc.)" />
      </v-col>
      <v-col cols="12" sm="6" md="6">    
        <v-text-field v-model="siStore.sched_item.solo_instruments" label="Solo instrument(s)" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.accomp_instruments" label="Accompanimental instrument(s)" />
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.other_performers" label="Other musicians (name of accompanist, other musicians)" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <div class="notice" >Please supply as much of the following as you are able.
          If it is early and you are proposing a title, all you need to do is
          provide the starting and ending key.
          You can come back and provide more details after the title is approved.</div>

        <h3 class="subhead">Song Details</h3>

      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.start_key" label="Starting Key (ex. A / Ab (A-flat major) / ab [a-flat minor])" />
        <!-- <v-select :items="keys" v-model="siStore.sched_item.start_key" label="Starting Key"  /> -->
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.end_key" label="Ending Key" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.author" label="Text Author (ex. Fanny Crosby)" />
        <v-text-field v-model="siStore.sched_item.translator" label="Text Translator (ex. Fred Jones)" />
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.composer" label="Composer (ex. Joseph Haydn)" />
        <v-text-field v-model="siStore.sched_item.arranger" label="Arranger (ex. Craig Courtney)" />
      </v-col>
    </v-row>
    <v-row class="text-center">
      <v-col cols="12">
          Tip: To fill in the following, look for a copyright notice (ex. "Copyright 2004 Soundforth") on the bottom of the first page of the music.<br>
          If it's not there, look at the title page of the book.
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.copyright_year" label="Copyright Year (ex. 1995)" />
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.copyright_holder" label="Copyright Holder (ex. Soundforth, Lorenz, Majesty Music)" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h3 class="subhead">Other Details</h3>
        <h4>Song Text</h4>
        <p>Enter the text of the song, along with indications of lengths of introductions and interludes, and any
          scripture texts you might want displayed during long interludes.
        </p>
        <v-textarea v-model="siStore.sched_item.song_text" label="Song Text" :auto-grow="true" max-rows="10" />
        <h4>Ministry Location</h4>
        <v-radio-group v-model="siStore.sched_item.ministry_location" 
          density="compact"
          hide-details="true"
          v-for="location in possible_locations">
          <v-radio :label="location" :value="location"></v-radio>
        </v-radio-group>
        <v-textarea v-model="siStore.sched_item.staging_notes" label="Staging Notes" />
        <v-btn @click="continueClicked()">Continue</v-btn> &nbsp;
        <v-btn @click="$router.go(-1)">Cancel</v-btn>

      </v-col>

    </v-row>
  </v-container>
</template>

<style scoped>
  .notice {
    border: 1px solid black;
    background-color: lightblue;
    padding: 10px;
    text-align: center;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
  }

</style>

<script>

// import SongSearch from './SongSearch.vue'
import { siStore } from './ServiceItemState.js'
import { ssStore } from './SongSearchState.js'

export default {
  name: 'ServiceItemEdit',

  props: {
    service_id: String,
    item_id: String
  },

  data: () => ({
    siStore: siStore,
    keys: ['A', 'C', 'Bb'],
    possible_locations: ['Pulpit', 'Piano well', 'Brass well', 'Orchestra pit', 'Choir loft', 'Bell loft', 'Other']
  }),  

  methods: {

    continueClicked() {
      this.$router.push({
        name: 'ServiceItemReview'
      })
    },

    changeSong() {
      ssStore.init()
      this.$router.push({ name: 'SongSearch' });
    },

  },
  
  async mounted() {
    try {
      let initialEntry = !siStore.item.description; // true if entering from ServiceItem screen
      if (!siStore.sched_item.id) {
        let res = await this.$api.beginEditServiceItem(this.service_id, this.item_id)
        siStore.sched_item = res.sched_item
        siStore.service = res.service
        siStore.item = res.item
      }

      document.title = siStore.service.name + ' ' + siStore.item.description

      if (!siStore.sched_item.title) {
        if (initialEntry) {
          // no title assigned yet; display search UI
          this.$router.push({ name: 'SongSearch' })
        } else {
          // Search was cancelled; exit edit
          this.$router.go(-1)
        }
      }
      scrollTo(0,0)
    } catch (err) {
      console.log(err);      
      if (err.response && err.response.status == 401) {
        this.$router.push({ path:'/login' })
      }
    }
  }
}
</script>
