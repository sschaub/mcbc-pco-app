<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <h2>Admin</h2>
        <h2>&nbsp;</h2>
        <v-btn @click="schedule()" :disabled="loading">Current Schedule</v-btn><br><br>
        <v-btn @click="loadServices()">Service Order Generator</v-btn>

        <h3 v-if="serviceList.length">Select services for service order</h3>
        <v-checkbox v-for="plan in serviceList"
          v-model="selectedServices"
          :hide-details="true"
          :key="plan.plan_id"
          :value="plan.plan_id"
          :label="plan.name"/>

        <v-btn v-if="serviceList.length" @click="genServiceOrder()" :disabled="selectedServices.length == 0">Generate Service Order</v-btn>
        
        
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
        this.serviceList = await this.$api.getServices()
      } finally {
        this.loading = false
      }
    },

    genServiceOrder() {
      console.log(this.selectedServices)
      let planIdStr = this.selectedServices.map( plan => `${plan}_plan=true` ).join('&')
      planIdStr += `&plan_id=${this.selectedServices[0]}`
      let url = `https://services.planningcenteronline.com/reports/${REPORT_ID_SERVICE_ORDER}.html?${planIdStr}`
      open(url)
    }
  }
}
</script>
