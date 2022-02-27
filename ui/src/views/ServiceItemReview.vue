<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="siStore.service.name && mode == 'review'">
          <h2>Please Review Your Entries</h2>
          <p>Review the information below and click Submit, or click Edit to change.</p>
          <h3>{{ siStore.service.name }} {{ siStore.item.description }}</h3>
          <h2>{{ siStore.sched_item.title }}</h2>
          <p v-if="siStore.sched_item.arrangement_name">Arrangement: {{ siStore.sched_item.arrangement_name }}</p>
          <service-item-details :sched_item="siStore.sched_item" :show_copyright_status="false" /> 
          <br>
          <v-btn @click="editClicked()">Edit</v-btn> &nbsp;
          <v-btn :disabled="loading" @click="submitClicked()">Submit</v-btn> &nbsp;
          <v-btn v-if="isAdmin()" :disabled="loading" @click="saveClicked()">Save</v-btn> &nbsp;
          <v-btn @click="cancelClicked()">Cancel</v-btn>
        </div>

        <div v-if="mode == 'finished'">
        <h3>Thank you for your submission!</h3>
        <p>An email has been sent to the appropriate personnel, and you have been copied.</p>
        <br>
        <v-btn @click="cancelClicked()">Finish</v-btn>
        </div>

        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>

      </v-col>

    </v-row>
  </v-container>
</template>

<style scoped>
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
    siStore: siStore,
    mode: 'review'
  }),  

  methods: {
    saveClicked() {
      this.updateItem(0)
    },

    submitClicked() {
      this.updateItem(1)
    },

    // emailType: 0 = none, 1 = standard
    async updateItem(emailType) {
      console.log(`Version: ${siStore.sched_item.version_no}`)
      try {
        this.loading = true
        siStore.sched_item.details_provided = 1
        let response = await this.$api.updateServiceItem(this.service_id, this.item_id, siStore.sched_item, emailType)
        if (response.result == 'OK') {
          if (emailType)
            this.mode = 'finished'
          else
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
    //console.log(`Version: ${this.sched_item.version_no}`)
    if (!siStore.item.id) {
      this.$router.go(-1)
    }
    scrollTo(0,0)
  },
  
  components: {
    ServiceItemDetails
  }
  
  
}
</script>

