<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="!service.name">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="service.name">
          <div>
            <h2>{{ service.name }} {{ item.description}}</h2>
            <div v-if="item.title">
              Scheduled Title: {{ item.title }}
            </div>
            <div>
              Proposed Title: {{ sched_item.title }}
              <v-btn @click="changeSong()">Change</v-btn>
            </div>
            <p v-if="sched_item.arrangement_name">Arrangement: {{ sched_item.arrangement_name }}</p>
              
            <h4>Instrumentation / Personnel</h4>
            <v-text-field v-model="sched_item.genre_note" label="Type of Number (Vocal solo, violin duet, etc.)" />
            <v-text-field v-model="sched_item.solo_instruments" label="Solo instrument(s)" />
            <v-text-field v-model="sched_item.accomp_instruments" label="Accompanimental instrument(s)" />
            <v-text-field v-model="sched_item.other_performers" label="Other performers (name of accompanist, other musicians)" />

            <div class="notice">Please supply as much of the following as you are able.
              <br>If it is early and you are proposing a title, all you need to do is
              provide the starting and ending key.<br>
              You can come back and provide more details after the title is approved.</div>

            <h4>Song Details</h4>
            
            <v-container>
              <v-row>
                <v-col>
                  <v-text-field v-model="sched_item.start_key" label="Starting Key (ex. A / Ab (A-flat major) / ab [a-flat minor])" />
                  <!-- <v-select :items="keys" v-model="sched_item.start_key" label="Starting Key"  /> -->
                </v-col>
                <v-col>
                  <v-text-field v-model="sched_item.end_key" label="Ending Key" />
                </v-col>
              </v-row>
            </v-container>
            <v-text-field v-model="sched_item.author" label="Text Author (ex. Fanny Crosby)" />
            <v-text-field v-model="sched_item.translator" label="Text Translator (ex. Fred Jones)" />
            <v-text-field v-model="sched_item.composer" label="Composer (ex. Joseph Haydn)" />
            <v-text-field v-model="sched_item.arranger" label="Arranger (ex. Craig Courtney)" />
            <div>
              Tip: To fill in the following, look for a copyright notice (ex. "Copyright 2004 Soundforth") on the bottom of the first page of the music.<br>
              If it's not there, look at the title page of the book.
            </div>
            <v-text-field v-model="sched_item.copyright_year" label="Copyright Year (ex. 1995)" />
            <v-text-field v-model="sched_item.copyright_holder" label="Copyright Holder (ex. Soundforth, Lorenz, Majesty Music)" />

            <h4>Other Details</h4>
            <v-textarea v-model="sched_item.song_text" label="Song Text" />
            <v-textarea v-model="sched_item.staging_notes" label="Staging Notes" />
            <v-btn @click="continueClicked()">Continue</v-btn>
            <v-btn @click="$router.go(-1)">Cancel</v-btn>
          </div>
        </div>

      </v-col>

    </v-row>
  </v-container>
</template>

<style>
  .notice {
    border: 1px solid black;
    background-color: lightblue;
    padding: 10px;
  }
</style>

<script>

import SongSearch from './SongSearch.vue'
import { siStore } from './ServiceItemState.js'

export default {
  name: 'ServiceItemEdit',

  props: {
    service_id: String,
    item_id: String
  },

  data: () => ({
    item: siStore.item,
    service: siStore.service, 
    sched_item: siStore.sched_item,
    keys: ['A', 'C', 'Bb']
  }),  

  methods: {

    continueClicked() {
      this.$router.push({
        name: 'ServiceItemReview'
      })
    },

    changeSong() {
      this.$router.push({ name: 'SongSearch' });
    },



  },
  
  async mounted() {
    try {
      if (!this.sched_item.id) {
        let res = await this.$api.beginEditServiceItem(this.service_id, this.item_id)
        this.sched_item = siStore.sched_item = res.sched_item
        this.service = siStore.service = res.service
        this.item = siStore.item = res.item
      }

      document.title = this.service.name + ' ' + this.item.description

      if (!this.sched_item.title) {
        if (siStore.searchCancelled) {
          // Search was cancelled; exit edit
          siStore.searchCancelled = false
          this.$router.go(-1)
        } else {
          // no title assigned yet; display search UI
          siStore.searchCancelled = false
          this.$router.push({ name: 'SongSearch' })
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
