<template>
  <!-- <v-breadcrumbs divider="-">
    <v-list>
      <v-list-item to="/">All Services</v-list-item>
      <v-list-item :to="`/service/${service_id}`">{{service.name}}</v-list-item>
    </v-list>
  </v-breadcrumbs> -->
  <v-container fluid>
    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate  />
    </div>
    <v-row class="text-center">
      <!-- <div class="ssbreadcrumb"><a href="/">Services</a> &gt; <a :href="`/service/${service_id}`">{{service.name}}</a></div> -->
      <v-col cols="12" sm="6" md="6">
        <div v-if="siStore.service.name">
          <h3><a @click="toService()" style="text-decoration: underline">{{siStore.service.name}}</a></h3>
          <h3>{{ siStore.item.description}}</h3>
          <div v-if="siStore.item.assigned_to.length">{{ itemPeople(siStore.item.assigned_to) }}</div>
          <br>
          <div v-if="title()">
            <span class="title">{{ title() }}</span> <a v-if="songUrl() && isAdmin()" :href="songUrl()" target="_blank">[pco]</a>
            <p v-if="siStore.sched_item.arrangement_name">Arrangement: {{ siStore.sched_item.arrangement_name }} <a v-if="isAdmin()" :href="arrangementUrl()" target="_blank">[pco]</a></p>
            <div v-if="isPending(siStore.sched_item)" class="pending">(Approval Pending)</div>
          </div>
          <br>
          <v-btn @click="editClicked()">Edit</v-btn>
          <span v-if="isAdmin()">
            &nbsp;
            <v-btn @click="emailClicked()">Send Email</v-btn>
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

          <div v-if="showImport">
            <v-container>
              <v-row>
                <v-col>
                  <v-text-field v-model="importArrangementName" label="Arrangement Name (ex. SATB - Forrest)" />
                </v-col>
                <v-col cols="4">
                  <v-btn :disabled="!importArrangementName" @click="doImport()">Import</v-btn>&nbsp;
                  <v-btn @click="showImport = false">Cancel</v-btn>
                </v-col>
              </v-row>
            </v-container>
          </div>

          <br>
          <service-item-details v-if="siStore.sched_item.details_provided" :sched_item="siStore.sched_item"  /> 
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
              <v-list-item two-line density="compact" class="text-left">
                <v-list-item-header>
                  <v-list-item-title>{{ song.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{song.description}} - {{ song.arrangement }}</v-list-item-subtitle>
                </v-list-item-header>
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
      if (siStore.sched_item.song_id)
        return `https://services.planningcenteronline.com/songs/${siStore.sched_item.song_id}`
    },

    arrangementUrl() {
      return `https://services.planningcenteronline.com/songs/${siStore.sched_item.song_id}/arrangements/${siStore.sched_item.arrangement_id}`
    },
        
    editClicked() {
      siStore.init()
      this.$router.push({ path: `/service/${this.service_id}/${this.item_id}/edit` })
    },

    emailClicked() {
      let toList = siStore.item.assigned_to.map(p => p.email).join(',')
      let toListNames = siStore.item.assigned_to.map(p => p.name.split(' ')[0]).join(', ')
      let body = `Dear ${toListNames},\n\n${location.href}`
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
        let response = await this.$api.importServiceItem(this.service_id, this.item_id, this.importArrangementName)
        if (response.result == 'OK') {
          siStore.sched_item.arrangement_name = response.arrangement_name
          siStore.sched_item.arrangement_id = response.arrangement_id
          siStore.sched_item.song_id = response.song_id
        }        
        this.showImport = false
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
      document.title = siStore.service.name + ' ' + siStore.item.description
    } finally {
      this.loading = false
    }
  },

  components: {
    ServiceItemDetails
  }  
  
}
</script>

