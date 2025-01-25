<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <h2 v-if="mode == 'song'">Song Search</h2>
        <div v-if="mode == 'song'">
          <div v-if="ssStore.showHelp" class="search-help">
            <h3>Step One: Search For Song</h3>
            <p>Enter the title of your song to see if it is in our database of songs.</p>         
          </div>

          <v-container>
            <v-row>
              <v-col class="flex-grow-1 flex-shrink-0">              
                <v-text-field ref="keywords" v-model="ssStore.keywords" label="Search words" @keyup.enter="doSongSearch()" class="flex-grow" />
              </v-col>
              <v-col class="flex-grow-0 flex-shrink-1">
                  <v-btn @click="doSongSearch()" :disabled="ssStore.keywords.length < 3 || loading">Search</v-btn>
              </v-col>
            </v-row>
          </v-container>
          <div class="text-left">Search what?</div>
          <v-radio-group v-model="ssStore.searchType" direction="horizontal">
            <v-radio label="Title" value="T" />
            <v-radio label="Lyrics" value="L" />
          </v-radio-group> 

          <div><v-progress-circular indeterminate v-if="loading" /></div>

          <div v-if="ssStore.songList.length &gt; 0 || notFound">

            <div v-if="notFound">
              <br>
              <p>No songs found.</p>
            </div>

            <div v-else>
              <div v-if="ssStore.isPicker" class="search-help">
                <h3>Step Two: Select Song</h3>
                <p>Select one of these matching songs in our database:</p>
              </div>

              
              <v-list v-for="song in ssStore.songList" :key="song.id" class="text-left mx-auto app-list">
                <v-list-item @click="songSelected(song.id)" class="text-left" :title="song.title" :subtitle="song.author" prepend-icon="mdi-chevron-right">
                </v-list-item>
              </v-list>
              <p v-if="ssStore.isPicker"><br>Don't see your song in the list above?</p>
            </div>
          </div>

          <div v-if="ssStore.isPicker && hasSearched">
            <br>
            <v-btn  @click="newSongClicked()">
                Add New Song
            </v-btn>
            <br>
            (If not in the database)
          </div>

          <!-- <v-btn v-if="ssStore.isPicker" @click="showRecommended" style="margin-top: 10px">Suggested Titles</v-btn> -->
        </div>

        <div v-if="mode == 'newsong'">
          <h2>New Song Title</h2>
          <v-text-field ref="confirmTitle" v-model="ssStore.keywords" label="Title"  />
          <v-btn @click="confirmNewTitle()">Confirm Title</v-btn>
          <v-btn @click="mode = 'song'">Cancel</v-btn>
        </div>

      </v-col>

    </v-row>
  </v-container>

</template>

<style scoped>
  .v-list, .v-list-item { padding: 0px !important; }  
</style>

<script>

import { ssStore } from './SongSearchState.js'

export default {
  name: 'SongSearch',

  data: () => ({
    mode: 'song',
    loading: false,
    notFound: '',
    hasSearched: false,
    ssStore: ssStore
  }),

  methods: {

    async doSongSearch() {
      if (ssStore.keywords.length < 3)
        return;

      this.notFound = false
      this.loading = true
      ssStore.songList = []
      ssStore.showHelp = false
      try {
        // Remove everything except letters, spaces, and single quotes
        let cleaned = ssStore.keywords.replace(/[^a-zA-Z\s']/g, '');

        // Remove single quotes that are not part of a word
        let keywords = cleaned.replace(/(^|\s)'|'(\s|$)/g, '$1$2');
        ssStore.songList = await this.$api.searchSongs(ssStore.searchType, keywords)
        if (ssStore.songList.length == 0) {
          this.notFound = true
          this.$refs.keywords.focus()
        }
      } finally {
        this.loading = false
        this.hasSearched = true
      }
    },

    async showRecommended() {
      this.loading = true
      this.notFound = false
      ssStore.songList = []
      try {
        ssStore.songList = await this.$api.recommendedSongs(siStore.service.service_id)
      } finally {
        this.loading = false
      }
      if (ssStore.songList.length == 0) {
        alert('No recommended songs for this service.')
      }
    },

    async songSelected(songId) {
      ssStore.song = ssStore.songList.find( song => song.id == songId )
      ssStore.arrList = []
      this.loading = true
      try {
        let songDetails = await this.$api.getSong(ssStore.song.id)
        ssStore.arrList = await this.$api.getArrangements(ssStore.song.id)
        ssStore.song.history = songDetails.history
        ssStore.song.author = songDetails.author
        ssStore.song.composer = songDetails.composer
        ssStore.song.lyrics = songDetails.lyrics
      } finally {
        this.loading = false
      }      
      this.$router.push( { name: 'SongSearchArrangements' } )      
    },

    newSongClicked() {
      this.mode = 'newsong'
      var self = this
      setTimeout(1000, () => self.$refs.confirmTitle.focus() )
      
    },

    confirmNewTitle() {
      ssStore.song = { title: ssStore.keywords }
      ssStore.arrangement = {}
      this.finishEntry()
    },

    async finishEntry() {
      ssStore.finishEntry()
      this.$router.go(-1)
    }


  },

  mounted() {
    this.$refs.keywords.focus()
    scrollTo(0, 0)
  }
}
</script>
