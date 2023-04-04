<template>
  <v-container>
    <v-row>
      <v-dialog v-model="showGenerator" 
        scrollable
        transition="dialog-bottom-transition">
        <v-card>
          <v-card-title>
            <span class="text-h5">Service Order Generator</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12">
                  <h3>Select Services for Service Order</h3>
                  <v-checkbox v-for="plan in serviceList"
                    v-model="selectedServices"
                    :hide-details="true"
                    density="compact"
                    :key="plan.plan_id"
                    :value="plan.plan_id"
                    :label="plan.name"/>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue-darken-1"
              @click="showGenerator = false"              
            >
              Cancel
            </v-btn>
            <v-btn
              color="blue-darken-1"
              :disabled="selectedServices.length == 0"
               @click="genServiceOrder('html')"
            >
              View
            </v-btn>
            <v-btn
              color="blue-darken-1"
              :disabled="selectedServices.length == 0"
               @click="genServiceOrder('pdf')"
            >
              Save PDF
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
    <v-row class="text-center">
      <v-col cols="12">
        <h2>Admin</h2>
        <h2>&nbsp;</h2>
        <v-btn @click="schedule()" :disabled="loading">Current Schedule</v-btn><br><br>
        <v-btn @click="loadServices()" :disabled="loading">Service Order Generator</v-btn>    
        
      </v-col>

    </v-row>
  </v-container>
</template>

<script>

import {REPORT_ID_SERVICE_ORDER} from '../constants.js';

export default {
  name: 'Admin',

  data: () => ({
    loading: false,
    showGenerator: false,
    serviceList: [],
    selectedServices: [],
  }),  

  methods: {
    async schedule() {
      try {
        this.loading = true
        let url = await this.$api.getScheduleReportUrl()
        open(url)
      } finally {
        this.loading = false
      }
    },

    async loadServices() {
      try {
        this.loading = true
        this.serviceList = await this.$api.getServices('future')
        this.showGenerator = true
      } finally {
        this.loading = false
      }
    },

    genServiceOrder(format) {
      let planIdStr = this.selectedServices.map( plan => `${plan}_plan=true` ).join('&')
      planIdStr += `&plan_id=${this.selectedServices[0]}`
      let url = `https://services.planningcenteronline.com/reports/${REPORT_ID_SERVICE_ORDER}.${format}?${planIdStr}`
      open(url)
    }
  }
}
</script>
