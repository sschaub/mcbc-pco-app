<template>
  <div v-if="loading || !siStore.service.name" class="text-center">
    <v-progress-circular indeterminate />
  </div>
  <v-container v-else-if="mode=='askfordetails'">
    <v-row class="text-center">
      <v-col cols="12">
        <h2>{{ siStore.sched_item.title }}</h2>
        <p v-if="siStore.sched_item.arrangement_name">Arrangement: {{ siStore.sched_item.arrangement_name }}</p>
        <br>
        <v-btn @click="openSearch()">Change Song</v-btn>
        <br><br>
        <div>Do you wish to provide additional details at this time?</div>
        <div><v-btn @click="provideDetailsClicked()">Yes</v-btn>&nbsp;<v-btn @click="noDetailsNowClicked()">No</v-btn></div>
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else-if="mode=='requiresomedetails'">
    <v-row class="text-center">
      <v-col cols="12">
        <h2>{{ siStore.sched_item.title }}</h2>
        <br>
        <div>Since we do not have this song / arrangement in our database, please provide at least the
          composer and arranger information on the next screen.
        </div>
        <div><v-btn @click="provideDetailsClicked()">Continue</v-btn></div>
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else-if="mode=='asktoreplace'">
    <v-row class="text-center">
      <v-col cols="12">
        <h2>{{ ssStore.song.title }}</h2>
        <p v-if="ssStore.arrangement.name">Arrangement: {{ ssStore.arrangement.name }}</p>
        <br>
        <div>Do you wish to replace the details previously entered with what we have on file for this song?</div>
        <br><br>
        <v-btn @click="replaceDetails()">Yes</v-btn>&nbsp;<v-btn @click="mode = ''">No</v-btn>
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else-if="mode=='thankyou'">
    <v-row class="text-center">
      <v-col cols="12">
          <h2>Thank You</h2>
          <div>Your proposed title has been submitted. You will receive an email when it is confirmed.</div>
          <div><v-btn @click="this.$router.go(-1)">Ok</v-btn></div>
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else fluid>
    <v-row class="text-center">
      <v-col cols="12">

        <h4>{{ siStore.service.name }}</h4>
        <h3>{{ siStore.item.description}}</h3>
        <h2>{{ siStore.sched_item.title }}</h2>
        <p v-if="siStore.sched_item.arrangement_name">Arrangement: {{ siStore.sched_item.arrangement_name }}</p>
        <br>
        <v-btn @click="openSearch()">Change Song</v-btn>        
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <!-- <div class="notice" >Please supply as much of the following as you are able.
          If it is early and you are proposing a title, all you need to do is
          provide the starting and ending key.
          You can come back and provide more details after the title is approved.</div> -->

        <h3 class="subhead">Song Details</h3>
        <p style="color: red">Due Wednesday p.m.</p>

      </v-col>
    </v-row>
    <v-row>      
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.author" label="Text (ex. Fanny Crosby)" />
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.composer" label="Tune (ex. Joseph Haydn)"  />
      </v-col>
    </v-row>
    <v-row>      
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.arranger" label="Arranger (ex. Craig Courtney)"  />
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-if="isAdmin()" v-model="siStore.sched_item.translator" label="Text Translator (ex. Fred Jones)"  />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <!-- <v-text-field v-model="siStore.sched_item.start_key" label="Starting Key (ex. A / Ab (A-flat major) / ab [a-flat minor])" /> -->
        <!-- <v-select :items="keys" v-model="siStore.sched_item.start_key" label="Starting Key"  /> -->
        <div class="gray">
          <v-select label="Starting Key" v-model="siStore.sched_item.start_key" :items="keys" item-title="name" item-value="val">          
          </v-select>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <!-- <v-text-field v-model="siStore.sched_item.end_key" label="Ending Key" /> -->
        <div style="margin-bottom: 30px">
          <v-select label="Ending Key" v-model="siStore.sched_item.end_key" :items="keys" item-title="name" item-value="val">          
          </v-select>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-radio-group v-model="copyrightType" inline>
          <v-radio label="Copyrighted Work" value="C" />
          <v-radio label="Improvised" value="Improvised" />
          <v-radio v-if="isAdmin()" label="Public Domain" value="Public Domain" />
        </v-radio-group>
      </v-col>
    </v-row>    
    <v-row class="text-center">
      <v-col v-if="isNewCopyrightEntry()" cols="12">
          Tip: To fill in the following, look for a copyright notice (ex. "Copyright 2004 Soundforth") on the bottom of the first page of the music.<br>
          If it's not there, look at the title page of the book.
      </v-col>
    </v-row>
    <v-row v-if="isNewCopyrightEntry()">
      <v-col cols="12" sm="6" md="6">
        <v-combobox label="Copyright Holder" v-model="siStore.sched_item.copyright_holder" :items="copyrightHolders()"> 
        </v-combobox>
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-if="siStore.sched_item.copyright_holder == 'Other'" v-model="siStore.sched_item.copyright_holder_other" label="Copyright Holder (ex. Soundforth)" />
      </v-col>
    </v-row>
    <v-row v-if="isNewCopyrightEntry() && !isPublicDomain()">
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.copyright_year" label="Copyright Year (ex. 1995)" type="number" />
      </v-col>
    </v-row>    
    <v-row v-if="siStore.sched_item.copyright && !isPublicDomain()">
      <v-col cols="12">
        <v-text-field v-model="siStore.sched_item.copyright" label="Copyright Info" />
      </v-col>
    </v-row>    
    <v-row v-if="isAdmin()">
      <v-col cols="6" v-if="isAdmin()">
        <v-text-field v-model="siStore.sched_item.ccli_num" label="CCLI Number" type="number" />
      </v-col>
    </v-row>    
    <v-row>
      <v-col>
        <h3 class="subhead">Instrumentation / Personnel</h3>
        <p style="color: red">Due Wednesday p.m.</p>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.genre_note" label="Type of Number (Vocal solo, violin duet, etc.)" />
      </v-col>
      <v-col v-if="isAdmin()" cols="12" sm="6" md="6">    
        <v-text-field v-model="siStore.sched_item.solo_instruments" label="Service order note (ex. Violin)" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.accomp_instruments" label="Accompanimental instrument(s)"  />
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <v-text-field v-model="siStore.sched_item.other_performers" label="Other musicians" />
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <h3 class="subhead">Other Details</h3>
        <h4>Song Text</h4>
        <p style="color: red">Due Wednesday p.m.</p>
        <p>Enter the text of the song, along with indications of lengths of introductions and interludes, and any
          scripture texts you might want displayed during long interludes.
        </p>
        <v-textarea v-model="siStore.sched_item.song_text" label="Song Text" rows="10"  />
        <h4>Ministry Location</h4>
        <v-radio-group v-model="siStore.sched_item.ministry_location" 
          density="compact"
          hide-details="true"
          v-for="location in possible_locations">
          <v-radio :label="location" :value="location"></v-radio>
        </v-radio-group>
        <v-textarea v-model="siStore.sched_item.staging_notes" label="Staging Notes" />
        <v-btn @click="continueClicked()">Review</v-btn> &nbsp;
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

import {ITEM_STATUS_PENDING, DETAILS_YES, DETAILS_NO} from '../constants.js';

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
    ssStore: ssStore,
    loading: false,
    songChanged: false,
    mode: '',
    copyrightType: 'C',
    keys: [{ val: "", name: "Unknown" },
          { val: "A", name: "A major" },
          { val: "a", name: "A minor" },
          { val: "Ab", name: "A-flat major" },
          { val: "ab", name: "A-flat minor" },
          { val: "A#", name: "A-sharp major" },
          { val: "a#", name: "A-sharp minor" },
          { val: "B", name: "B major" },
          { val: "b", name: "b minor" },
          { val: "Bb", name: "B-flat major" },
          { val: "bb", name: "B-flat minor" },
          { val: "C", name: "C major" },
          { val: "c", name: "C minor" },
          { val: "C#", name: "C-sharp major" },
          { val: "c#", name: "C-sharp minor" },
          { val: "D", name: "D major" },
          { val: "d", name: "D minor" },
          { val: "Db", name: "D-flat major" },
          { val: "db", name: "D-flat minor" },
          { val: "D#", name: "D-sharp major" },
          { val: "d#", name: "D-sharp minor" },
          { val: "E", name: "E major" },
          { val: "Eb", name: "E-flat major" },
          { val: "eb", name: "E-flat minor" },
          { val: "e", name: "E minor" },
          { val: "F", name: "F major" },
          { val: "f", name: "F minor" },
          { val: "F#", name: "F-sharp major" },
          { val: "f#", name: "F-sharp minor" },
          { val: "G", name: "G major" },
          { val: "g", name: "G minor" },
          { val: "Gb", name: "G-flat major" },
          { val: "gb", name: "G-flat minor" },
          { val: "G#", name: "G-sharp major" },
          { val: "g#", name: "G-sharp minor" }],
    possible_locations: ['Pulpit', 'Piano well', 'Brass well', 'Orchestra pit', 'Choir loft', 'Bell loft', 'Other'],
    improvised: false
  }),  

  methods: {

    copyrightHolders() {
      return ['', ...siStore.copyright_holders, 'Other'] 
    },

    isPublicDomain() {
      return this.isNonCopyright(siStore.sched_item.copyright) 
    },

    isNewCopyrightEntry() {
      return this.copyrightType == 'C' && !siStore.sched_item.copyright
    },

    continueClicked() {
      siStore.sched_item.song_text = siStore.sched_item.song_text ? siStore.sched_item.song_text.trim() : ''
      siStore.sched_item.composer = siStore.sched_item.composer ? siStore.sched_item.composer.trim() : ''
      siStore.sched_item.arranger = siStore.sched_item.arranger ? siStore.sched_item.arranger.trim() : ''
      siStore.sched_item.translator = siStore.sched_item.translator ? siStore.sched_item.translator.trim() : ''
      this.$router.push({
        name: 'ServiceItemReview'
      })
    },

    async noDetailsNowClicked() {
      if (!this.songChanged) {
        this.$router.go(-1)
        return
      }
      try {
        this.loading = true
        await this.$api.updateServiceItem(this.service_id, this.item_id, siStore.sched_item, 2)
        this.mode = 'thankyou'
      } finally {
        this.loading = false
      }
    },

    provideDetailsClicked() {
      siStore.sched_item.details_provided = DETAILS_YES;
      this.mode='';
    },

    replaceDetails() {
      siStore.sched_item.author = ssStore.song.author
      siStore.sched_item.arranger = ''
      siStore.sched_item.translator = ''
      siStore.sched_item.start_key = ''
      siStore.sched_item.end_key = ''
      if (ssStore.arrangement.id) {
          siStore.sched_item.author = ssStore.arrangement.author
          siStore.sched_item.copyright = ssStore.arrangement.copyright
          siStore.sched_item.start_key = ssStore.arrangement.start_key
          siStore.sched_item.end_key = ssStore.arrangement.end_key
          siStore.sched_item.song_text = ssStore.arrangement.lyrics
          siStore.sched_item.composer = ssStore.arrangement.composer
          siStore.sched_item.arranger = ssStore.arrangement.arranger        
          siStore.sched_item.translator = ssStore.arrangement.translator
          siStore.sched_item.ccli_num = ssStore.arrangement.ccli_num
      } else if (ssStore.song.id) {
          siStore.sched_item.title = ssStore.song.title
          siStore.sched_item.author = ssStore.song.author
          siStore.sched_item.composer = ssStore.song.composer
          siStore.sched_item.song_text = ssStore.song.lyrics
          siStore.sched_item.copyright = ssStore.arrangement.copyright
      }

      if (siStore.sched_item.details_provided != DETAILS_YES) {
          // ask if user wishes to enter details
        this.mode = "askfordetails"
      } else {
        this.mode = ""
        this.initCopyrightType()
      }

    },

    initCopyrightType() {
      if (this.isNonCopyright(siStore.sched_item.copyright)) {
        this.copyrightType = siStore.sched_item.copyright
      } else {
        this.copyrightType = 'C'
      }
      console.log(`copyright: ${siStore.sched_item.copyright}, copyrightType = ${this.copyrightType}`)
    },

    openSearch() {
      ssStore.init(true)
      this.$router.push({ name: 'SongSearch' })
    }

  },

  watch: {
    copyrightType(newValue) {
      if (this.isNonCopyright(newValue)) {
        // public domain or improvised
        siStore.sched_item.copyright = newValue
      } else {
        siStore.sched_item.copyright_holder = ''
        siStore.sched_item.copyright_year = ''
        siStore.sched_item.copyright = ''
      }
    }
  },
  
  async mounted() {
    scrollTo(0,0)
    try {
      let cameFromServiceItemScreen = !siStore.item.description; // true if entering from ServiceItem screen
      if (cameFromServiceItemScreen) {
        ssStore.init(true)
        try {
          this.loading = true
          let res = await this.$api.beginEditServiceItem(this.service_id, this.item_id)
          siStore.sched_item = res.sched_item
          siStore.service = res.service
          siStore.item = res.item
          siStore.copyright_holders = res.copyright_holders          
        } finally {
          this.loading = false
        }
      }

      document.title = siStore.service.name + ' ' + siStore.item.description

      if (ssStore.selectionOccurred) {
        // Coming from song picker
        siStore.sched_item.title = ssStore.song.title
        siStore.sched_item.song_id = ssStore.song.id
        siStore.sched_item.arrangement_id = ssStore.arrangement.id
        siStore.sched_item.arrangement_name = ssStore.arrangement.name
        this.songChanged = true
        if (siStore.sched_item.song_id) {
          // A song was selected from the PCO database
          if (siStore.sched_item.details_provided == DETAILS_YES) {
            // Details previously entered; prompt user whether to replace
            this.mode = 'asktoreplace'
            return
          } else {
            // No details previously entered; just record the details
            this.replaceDetails()          
          }
        }
      }
      ssStore.selectionOccurred = false      

      this.initCopyrightType()

      if (siStore.sched_item.title) {
        if (siStore.sched_item.details_provided == DETAILS_NO) {
          if (siStore.sched_item.song_id && siStore.sched_item.arrangement_id) {
            // ask if user wishes to enter details
            this.mode = "askfordetails"
          } else {
            this.mode = "requiresomedetails"
          }
          return
        }
      } else {
        // No title 
        if (cameFromServiceItemScreen) {
          // no title assigned yet; display search UI
          this.openSearch()
        } else {
          // Search was cancelled; exit edit
          this.$router.go(-1)
        }
      }
      
    } catch (err) {
      if (err.response && err.response.status == 401) {
        this.$router.push({ path:'/login' })
      } else {
        console.log(err);
      }
    }
  }
}
</script>
