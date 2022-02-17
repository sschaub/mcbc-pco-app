<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="service.name">
          <h2>{{ service.name }} Service</h2>
          <h3 v-if="service.theme" >{{ service.theme }}</h3>
          <h4>{{ item.description}}</h4>
          <div v-if="item.assigned_to.length">Assigned to: {{ itemPeople(item.assigned_to) }}</div>
          <div>
            Title: {{ sched_item.title }}
          </div>
          <p v-if="sched_item.arrangement_name">Arrangement: {{ sched_item.arrangement_name }}</p>
          <br>
          <service-item-details :sched_item="sched_item" /> 
          <v-btn @click="editClicked()">Edit</v-btn>
          <v-btn :disabled="loading" @click="submitClicked()">Submit</v-btn>
          <v-btn @click="cancelClicked()">Cancel</v-btn>
        </div>
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>

      </v-col>

    </v-row>
  </v-container>
</template>

<style>
  h3 { margin-top: 30px }
</style>

<script>

import ServiceItemDetails from './ServiceItemDetails.vue'
import { siStore } from './ServiceItemState.js'

export default {
  name: 'ServiceItemReview',

  props: {
    service_id: String,
    item_id: String
  },

  data: () => ({
    loading: false,
    item: siStore.item,
    service: siStore.service, 
    sched_item: siStore.sched_item,
  }),  

  methods: {
    async submitClicked() {
      console.log(`Version: ${this.sched_item.version_no}`)
      try {
        this.loading = true
        let response = await this.$api.updateServiceItem(this.service_id, this.item_id, this.sched_item)
        if (response.result == 'OK') {
          this.$router.go(-2)        
        } else {
          alert('Someone else has changed this entry while you were editing it. Click Cancel, then try again.')
        }
      } finally {
        this.loading = false
      }
    },

    editClicked() {
      this.$router.go(-1)
    },

    cancelClicked() {
      this.$router.go(-2)
    },

  },

  mounted() {
    console.log(`Version: ${this.sched_item.version_no}`)
    if (!this.item.id) {
      this.$router.go(-1)
    }
  },
  
  components: {
    ServiceItemDetails
  }
  
  
}
</script>

