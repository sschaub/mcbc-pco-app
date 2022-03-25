<template>
  <div v-if="loading" class="text-center">
    <v-progress-circular indeterminate />
  </div>
  <v-container v-if="siStore.service.name && mode == 'review'" fluid>
    <v-row class="text-center">
      <v-col cols="12">
        <h2>Please Review Your Entries</h2>
        <p>Review the information below and click Submit, or click Edit to change.</p>
        <p>Note: You can submit even if you are missing information.</p>
      </v-col>
    </v-row>
    <v-row class="text-center">
      <v-col cols="12" sm="6" md="6">
        <div>
          <h3>{{ siStore.service.name }} {{ siStore.item.description }}</h3>
          <h2>{{ siStore.sched_item.title }}</h2>
          <p v-if="siStore.sched_item.arrangement_name">Arrangement: {{ siStore.sched_item.arrangement_name }}</p>

          <!-- <v-btn @click="cancelClicked()">Cancel</v-btn> -->

          <service-item-details :sched_item="siStore.sched_item" :show_copyright_status="false" /> 
          <br>
          <v-btn @click="editClicked()">Edit</v-btn> &nbsp;
          <v-btn :disabled="loading" @click="submitClicked()">Submit</v-btn> &nbsp;
          <v-btn v-if="isAdmin()" :disabled="loading" @click="saveClicked()">Save</v-btn> &nbsp;          
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <song-lyrics :lyrics="siStore.sched_item.song_text" missingClass="missing" />
      </v-col>

    </v-row>
  </v-container>

  <div v-if="mode == 'finished'" class="text-center">
    <h3>Thank you for your submission!</h3>
    <p>An email has been sent to the appropriate personnel, and you have been copied.</p>
    <br>
    <v-btn @click="cancelClicked()">Finish</v-btn>
  </div>

</template>

<style scoped>
  h3 { margin-top: 30px }
</style>

<script>

import ServiceItemDetails from './ServiceItemDetails.vue'
import SongLyrics from './SongLyrics.vue'
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
    ServiceItemDetails,
    SongLyrics
  }
  
  
}
</script>

