<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div><a href="/">Home</a> &gt; <a :href="`/service/${service_id}`">{{service.name}}</a> &gt; {{ item.description }}</div>
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="service.name">
          <h3 v-if="service.theme" >{{ service.theme }}</h3>
          <h4>{{ item.description}}</h4>
          <div v-if="item.assigned_to.length">Assigned to: {{ itemPeople(item.assigned_to) }}</div>
          <div v-if="scheduledTitle()">
            Scheduled Title: {{ scheduledTitle() }}
          </div>
          <div v-if="proposedTitle()">
            Proposed Title:
            <span v-if="songUrl()">
              <a :href="songUrl()" target="_blank">{{ proposedTitle() }}</a>
            </span>
            <span v-if="!songUrl()">
              {{ proposedTitle() }}
            </span>
            <span class="pending"> (Approval Pending)</span>
          </div>
          <p v-if="sched_item.arrangement_name">Arrangement: <a :href="arrangementUrl()" target="_blank">{{ sched_item.arrangement_name }}</a></p>
          <v-btn @click="editClicked()">Edit</v-btn>
          <span v-if="isAdmin()">
            <v-btn @click="emailClicked()">Send Email</v-btn>
            <v-btn v-if="isPending()" @click="approveClicked()">Approve</v-btn>
          </span>
          <br><br>
          <service-item-details v-if="sched_item.title" :sched_item="sched_item"  /> 
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

