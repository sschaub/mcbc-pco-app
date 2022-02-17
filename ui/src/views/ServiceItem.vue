<template>
  <v-container>
    <v-row class="text-center">
      <div><a href="/">Home</a> &gt; <a :href="`/service/${service_id}`">{{service.name}}</a></div>
      <v-col cols="12">        
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="service.name">
          <h3>{{service.name}} {{ item.description}}</h3>
          <h4 v-if="service.theme" >Service Theme: {{ service.theme }}</h4>
          <div v-if="item.assigned_to.length">Assigned to: {{ itemPeople(item.assigned_to) }}</div>
          <div v-if="scheduledTitle()">
            Scheduled Title: {{ scheduledTitle() }}
          </div>
          <div v-if="proposedTitle()">
            Proposed Title: {{ proposedTitle() }} <a v-if="songUrl()" :href="songUrl()" target="_blank">[pco]</a>
            <span class="pending"> (Approval Pending)</span>
          </div>
          <p v-if="sched_item.arrangement_name">Arrangement: {{ sched_item.arrangement_name }} <a v-if="arrangementUrl()" :href="arrangementUrl()" target="_blank">[pco]</a></p>
          <v-btn @click="editClicked()">Edit</v-btn>
          <span v-if="isAdmin()">
            <v-btn @click="emailClicked()">Send Email</v-btn>
            <v-btn v-if="isPending()" @click="approveClicked()">Approve</v-btn>
          </span>
          <br><br>
          <service-item-details v-if="sched_item.title" :sched_item="sched_item"  /> 
          <div v-if="service.songs.length">
            <h3>Note Other Songs In This Service</h3>
            <div v-for="song in service.songs" :key="song.id">
                  <p>{{song.description}}: {{ song.title }} <span v-if="song.arrangement">- {{ song.arrangement }}</span></p>
            </div>
          </div>
        </div>
      </v-col>

    </v-row>
  </v-container>
</template>

<style>
  h3 { margin-top: 20px }
  .pending { color: red }
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
    item: {},
    service: {}, 
    sched_item: {},
    loading: true
  }),  

  methods: {

    scheduledTitle() {
        if (this.item.title) {
            return this.item.title
        }
    },

    proposedTitle() {
        if (this.sched_item.title && this.item.title != this.sched_item.title) {
            return this.sched_item.title
        }
    },

    songUrl() {
      if (this.sched_item.song_id)
        return `https://services.planningcenteronline.com/songs/${this.sched_item.song_id}`
    },

    arrangementUrl() {
      return `https://services.planningcenteronline.com/songs/${this.sched_item.song_id}/arrangements/${this.sched_item.arrangement_id}`
    },
        
    editClicked() {
      siStore.item = siStore.sched_item = siStore.service = {}
      this.$router.push({ path: `/service/${this.service_id}/${this.item_id}/edit` })
    },
    emailClicked() {
      let toList = this.item.assigned_to.map(p => p.email).join(',')
      let body = location.href
      let subject = this.service.name + " " + this.item.description
      // launch email client
      location = "mailto:" + toList + "?subject=" + encodeURI(subject) + "&body=" + body
    },
    
    async approveClicked() {
      try {
        this.loading = true
        let response = await this.$api.approveServiceItem(this.service_id, this.item_id)
        if (response.result == 'OK') {
          this.sched_item.status = ITEM_STATUS_APPROVED
          this.item.title = this.sched_item.title
          let toList = this.item.assigned_to.map(p => p.email).join(',')
          let body = `Thank you for submitting the title: ${this.item.title}\n\nThis is fine with me.\n\n`
          body += `If you haven't already done so, please submit the additional details by Wednesday night using the website:\n\n${location.href}\n\n`
          body += `Gratefully,\nSam`
          let subject = this.service.name + " " + this.item.description
          location = "mailto:" + toList + "?subject=" + encodeURI(subject) + "&body=" + encodeURI(body)
        }
      } finally {
        this.loading = false
      }
    }
  },
  
  async mounted() {
    try {
      let res = await this.$api.getServiceItem(this.service_id, this.item_id)
      this.item = res.item
      this.service = res.service
      this.sched_item = res.sched_item || {}
      document.title = this.service.name + ' ' + this.item.description
    } finally {
      this.loading = false
    }
  },

  components: {
    ServiceItemDetails
  }  
  
}
</script>

