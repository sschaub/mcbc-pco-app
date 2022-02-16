<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <h2>Song Search</h2>
        <div v-if="mode == 'song'">
          <v-container>
            <v-row>
              <v-col>
                <v-text-field v-model="keywords" label="Title"  />
              </v-col>
              <v-col cols="2">
                <v-btn @click="doSongSearch()">Search</v-btn>
              </v-col>
            </v-row>
          </v-container>

          <v-progress-circular indeterminate v-if="loading" />

          <div v-if="songList.length &gt; 0">

            <div v-for="song in songList" :key="song.id">
                <h4>{{ song.title }}</h4>
                <div v-if="song.author">{{ song.author }}</div>
                <v-btn @click="songSelected(song.id)" :disabled="keywords.length < 3">
                  Select
                </v-btn>
            </div>

              <br><br>
              <v-btn @click="mode = 'newsong'">
                    Other Song
              </v-btn>              
          </div>

          <div v-if="notFound">
            <br>
            <p>No songs found. You can try another search, or</p>
            <v-btn @click="mode = 'newsong'">Continue with New Song</v-btn>
          </div>
          <br>
          <v-btn @click="searchCancelled()">Cancel</v-btn>
        </div>

        <div v-if="mode == 'newsong'">
          <p>Confirm new song title:</p>
          <v-text-field v-model="keywords" label="Title"  />
          <v-btn @click="confirmNewTitle()">Continue</v-btn>
          <v-btn @click="mode = 'song'">Cancel</v-btn>
        </div>

        <div v-if="mode == 'arrangement'">
          <div>
            Selected Song: {{ song.title }} 
            <v-btn @click="mode = 'song'">Change</v-btn>
          </div>
          <div v-if="song.author">{{ song.author }}</div>

          <h3>Select Arrangement</h3>
          <p>Here are the arrangements we have on file:</p>

          <v-progress-circular indeterminate v-if="loading" />

          <div v-for="arr in arrList" :key="arr.id">
              <h4>{{ arr.name }}</h4>
              <div v-if="arr.last_used">Last used: {{ arr.last_used }}</div>
              <v-btn @click="arrangementSelected(arr)">
                Select
              </v-btn>
          </div>

          <br><br>
          <v-btn @click="arrangementSelected()">
                Other Arrangement
          </v-btn>

        </div>
      </v-col>

    </v-row>
  </v-container>

</template>

<style>
  h4 { margin-top: 20px }
</style>

<script>

import { siStore } from './ServiceItemState.js'

export default {
  name: 'SongSearch',

  data: () => ({
    keywords: "",
    loading: false,
    notFound: false,
    songList: [],
    mode: 'song',
    song: {},
    arrangement: {},
    arrList: []
  }),

  methods: {
    async doSongSearch() {
      if (this.keywords.length < 3)
        return
      this.notFound = false
      this.loading = true
      this.songList = []
      try {
        this.songList = await this.$api.searchSongs(this.keywords)
        if (this.songList.length == 0) {
          this.notFound = true
        }
      } catch (e) {
        console.log(e)
      }
      this.loading = false
    },

    async songSelected(songId) {
      this.song = this.songList.find( song => song.id == songId )
      this.mode = 'arrangement'
      this.loading = true
      try {
        this.arrList = [] // clear arrangement list from UI
        this.arrList = await this.$api.getArrangements(songId)
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
      
    },

    arrangementSelected(arrangement) {
      this.arrangement = arrangement
      console.log(arrangement)
      this.finishEntry()
    },

    confirmNewTitle() {
      this.song = { title: this.keywords }
      this.arrangement = {}
      this.finishEntry()
    },

    finishEntry() {
      siStore.sched_item.song_id = this.song.id
      siStore.sched_item.title = this.song.title
      siStore.sched_item.author = this.song.author
      siStore.sched_item.copyright = this.song.copyright
      if (this.arrangement) {
        siStore.sched_item.arrangement_id = this.arrangement.id
        siStore.sched_item.arrangement_name = this.arrangement.name        
        siStore.sched_item.author = this.arrangement.author
        siStore.sched_item.copyright = this.arrangement.copyright
        siStore.sched_item.composer = ''
        
        if (this.arrangement.lyrics) {
          siStore.sched_item.song_text = this.arrangement.lyrics
        }

        if (this.arrangement.copyright) {
          siStore.sched_item.copyright_holder = this.arrangement.copyright
        }
      }
      this.$router.go(-1)
    },

    searchCancelled() {
      siStore.searchCancelled = true
      this.$router.go(-1)
    }


  },
}
</script>
