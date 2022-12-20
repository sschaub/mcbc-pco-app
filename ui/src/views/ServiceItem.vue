<template>
  <v-container fluid>
    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate  />
    </div>
    <v-row>
      <v-dialog v-model="showImport">
        <v-card>
          <v-card-title>
            <span class="text-h5">Import Arrangement</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="importArrangementName" label="Arrangement Name (ex. SATB - Forrest)" />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="importServiceOrderNote" label="Service Order Note" />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue-darken-1"
              variant="text"
              @click="showImport = false"
            >
              Cancel
            </v-btn>
            <v-btn
              color="blue-darken-1"
              variant="text"
              :disabled="!importArrangementName" @click="doImport()"
            >
              Import
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>

    <v-row class="text-center">
      <!-- <div class="ssbreadcrumb"><a href="/">Services</a> &gt; <a :href="`/service/${service_id}`">{{service.name}}</a></div> -->
      <v-col cols="12" sm="6" md="6">
        <div v-if="siStore.service.name">
          <h3><a @click="toService()" style="text-decoration: underline">{{siStore.service.name}}</a></h3>
          <h3>{{ siStore.item.description}}</h3>
          <div v-if="siStore.item.assigned_to.length">{{ itemPeople(siStore.item.assigned_to) }}</div>
          <br>
          <div v-if="title()">
            <span class="title">{{ title() }}</span>
            <span v-if="isAdmin()" style="margin-left: 10px">              
              <a v-if="songUrl()" :href="songUrl()" target="_blank">[pco]</a>
              <span v-else>(new song)</span>
            </span>
            <p v-if="arrangementName()">Arrangement: {{ arrangementName() }} <a v-if="isAdmin()" :href="arrangementUrl()" target="_blank">[pco]</a></p>
            <div v-if="isPending(siStore.sched_item)" class="pending">(Approval Pending)</div>
          </div>
          <br>
          <v-btn @click="editClicked()">Edit</v-btn>
          <span v-if="isAdmin()">
            &nbsp;
            <v-btn v-if="siStore.item.assigned_to.length" @click="emailClicked('init')">Initial Email</v-btn>
            &nbsp;
            <v-btn v-if="siStore.item.assigned_to.length" @click="emailClicked('followup')">Followup Email</v-btn>
            &nbsp;
            <v-btn v-if="isPending(siStore.sched_item)" @click="approveClicked()">Approve 
              <v-icon dark right>
                mdi-checkbox-marked-circle
              </v-icon>
            </v-btn>
            <v-btn v-if="!isPending(siStore.sched_item) && siStore.sched_item.title" @click="showImport = true">Import To PCO</v-btn>            
            <span v-if="siStore.sched_item.title">&nbsp;
              <v-btn @click="resetClicked()">Reset</v-btn>
            </span>
          </span>

          <br>
          <service-item-details v-if="siStore.sched_item.details_provided" :sched_item="siStore.sched_item"  /> 
          <song-lyrics v-if="siStore.sched_item.details_provided" :lyrics="siStore.sched_item.song_text" />
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="6">          
          <div v-if="siStore.service.theme">
            <h3>Service Theme</h3>
            <h2>{{ siStore.service.theme }}</h2>
          </div>
          <div v-if="songs.length">
            <h3>Other Songs In This Service</h3>
            <v-list v-for="song in songs" :key="song.id" class="mx-auto app-list">
              <v-list-item :title="song.title" :subtitle="`${song.description} - ${song.arrangement}`" class="text-left">
              </v-list-item>
            </v-list>            
          </div>

      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
h3 { margin-top: 20px }
.title { font-size: 24px; font-weight: bold;}
.pending { color: red }
.v-list, .v-list-item { padding: 4px !important; }  
</style>

<script>

import ServiceItemDetails from './ServiceItemDetails.vue'
import SongLyrics from './SongLyrics.vue'
import {ITEM_STATUS_PENDING, ITEM_STATUS_APPROVED, COPYRIGHT_STATUS_APPROVED} from '../constants.js';
import { siStore } from './ServiceItemState.js'

export default {
  name: 'ServiceItem',

  props: {
    service_id: String,
    item_id: String
  },

  data: () => ({
    siStore: siStore,
    loading: true,
    showImport: false,
    importArrangementName: ''
  }),  

  computed: {
    songs() {
      if (!siStore.service.songs) {
        return []
      }
      return siStore.service.songs.filter( song => song.title && (song.description != siStore.item.description) )
    }
  },

  methods: {
    toService() {
      this.$router.push( { path: `/service/${this.service_id}` })
    },

    title() {
      return siStore.sched_item.title || siStore.item.title
    },

    songUrl() {
      let song_id = siStore.sched_item.item_id ? siStore.sched_item.song_id : siStore.item.song_id
      if (song_id)
        return `https://services.planningcenteronline.com/songs/${song_id}`
    },

    arrangementUrl() {
      let arr_id = ''
      let song_id = ''
      if (siStore.sched_item.item_id) {
        song_id = siStore.sched_item.song_id
        arr_id = siStore.sched_item.arrangement_id
      } else {
        song_id = siStore.item.song_id
        arr_id = siStore.item.arrangement_id
      }
      if (arr_id) 
        return `https://services.planningcenteronline.com/songs/${song_id}/arrangements/${arr_id}`
    },

    arrangementName() {
      return (siStore.sched_item.item_id) ? siStore.sched_item.arrangement_name : siStore.item.arrangement
    },
        
    editClicked() {
      siStore.init()
      this.$router.push({ path: `/service/${this.service_id}/${this.item_id}/edit` })
    },

    emailClicked(emailType) {
      let toList = siStore.item.assigned_to.map(p => p.email).join(',')
      let toListNames = siStore.item.assigned_to.map(p => p.name.split(' ')[0]).join(', ')
      let user = this.getUser()
      let body
      let serviceName = siStore.service.name.split(' - ')[0]
      if (emailType == 'init') {      
        body = `Good morning ${toListNames},\n
I hope you're well this morning.

Thank you for preparing to minister the ${siStore.item.description} for this coming ${serviceName}.

We would like to have all the lyrics/info for your ministry by this Wed PM at the latest, but if you could submit the title today that would be a great help.

Please use this link to submit your title: ${location.href}

If you need a reminder about how to submit the information, here's some info that should help: https://www.mcbcmusic.org/home/lyrics-app-help

Thank you so much!

SA
https://schedule.mcbcmusic.org/pdf
`
      } else {
        body = `Good afternoon ${toListNames},\n
Just a quick reminder to submit your information for your ministry sometime today.

Submit your info here: ${location.href}

Thank you!

SA
https://schedule.mcbcmusic.org/pdf
`
      }
      let subject = siStore.service.name + " " + siStore.item.description
      // launch email client
      location = "mailto:" + toList + "?subject=" + encodeURI(subject) + "&body=" + encodeURI(body)
    },

    async resetClicked() {
      if (confirm("Are you sure you wish to reset this entry?")) {
        try {
          this.loading = true
          await this.$api.resetServiceItem(this.service_id, this.item_id)
          siStore.sched_item = {}
          siStore.item.title = ''
        } finally {
          this.loading = false
        }
      }
    },
    
    async approveClicked() {
      try {
        this.loading = true
        let response = await this.$api.approveServiceItem(this.service_id, this.item_id)
        if (response.result == 'OK') {
          siStore.sched_item.status = ITEM_STATUS_APPROVED
          siStore.item.title = siStore.sched_item.title
          let toList = siStore.item.assigned_to.map(p => p.email).join(',')
          let body = `Thank you for submitting the title: ${siStore.item.title}\n\nThis is fine with me.\n\n`
          body += `If you haven't already done so, please submit the additional details by Wednesday night using the website:\n\n${location.href}\n\n`
          body += `Gratefully,\nSam`
          let subject = siStore.service.name + " " + siStore.item.description
          location = "mailto:" + toList + "?subject=" + encodeURI(subject) + "&body=" + encodeURI(body)
        }
      } finally {
        this.loading = false
      }
    },

    async doImport() {
      try {
        this.loading = true
        let response = await this.$api.importServiceItem(this.service_id, this.item_id, this.importArrangementName, this.importServiceOrderNote)
        siStore.sched_item.arrangement_name = response.arrangement_name
        siStore.sched_item.arrangement_id = response.arrangement_id
        siStore.sched_item.song_id = response.song_id
        this.showImport = false
      } catch (err) {
        if (err.response) {
          console.log(err.response.data)
          if (err.response.data.error)
            alert(err.response.data.error)
          else
            alert(err.response.data)          
        }
          
      } finally {
        this.loading = false
      }
    }
  },
  
  async mounted() {
    try {
      siStore.init()
      let res = await this.$api.getServiceItem(this.service_id, this.item_id)
      siStore.item = res.item
      siStore.service = res.service
      siStore.sched_item = res.sched_item || {}
      this.importArrangementName = siStore.sched_item.arrangement_name
      this.importServiceOrderNote = siStore.sched_item.solo_instruments
      document.title = siStore.service.name + ' ' + siStore.item.description
    } finally {
      this.loading = false
    }
  },

  components: {
    ServiceItemDetails,
    SongLyrics
  }  
  
}
</script>

