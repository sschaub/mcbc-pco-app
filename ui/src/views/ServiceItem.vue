<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="service.name">
          <h2>{{ service.name }} Service</h2>
          <h3 v-if="service.theme" >{{ service.theme }}</h3>
          <h4>{{ item.description}}</h4>
          <div v-if="item.assigned_to.length">Assigned to: {{ itemPeople(item.assigned_to) }}</div>
          <div v-if="scheduledTitle(item, sched_item)">
            Scheduled Title: {{ scheduledTitle(item, sched_item) }}
          </div>
          <div v-if="proposedTitle(item, sched_item)">
            Proposed Title: {{ proposedTitle(item, sched_item) }}
          </div>
          <p v-if="sched_item.arrangement_name">Arrangement: {{ sched_item.arrangement_name }}</p>
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
</style>

<script>

import ServiceItemDetails from './ServiceItemDetails.vue'
import {ITEM_STATUS_PENDING, ITEM_STATUS_APPROVED, COPYRIGHT_STATUS_APPROVED} from '../constants.js';

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

    scheduledTitle(item, sched_item) {
        if (item.title) { // } && (!sched_item.title || item.title != sched_item.title)) {
            return item.title
        }
    },

    proposedTitle(item, sched_item) {
        if (sched_item.title && item.title != sched_item.title) {
            return sched_item.title
        }
    },
        
    editClicked() {
      console.log('Navigating...')
      this.$router.push({ path: `/service/${this.service_id}/${this.item_id}/edit` })
    },
    emailClicked() {
      let toList = this.item.assigned_to.map(p => p.email).join(',')
      let body = location.href
      let subject = this.service.name + " " + this.item.description
      // launch email client
      location = "mailto:" + toList + "?subject=" + encodeURI(subject) +
        "&body=" + body
    },
    
    async approveClicked() {
      try {
        this.loading = true
        let response = await this.$api.approveServiceItem(this.service_id, this.item_id)
        if (response.result == 'OK') {
          this.sched_item.status = ITEM_STATUS_APPROVED
          this.item.title = this.sched_item.title
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
    } finally {
      this.loading = false
    }
  },

  components: {
    ServiceItemDetails
  }  
  
}
</script>

