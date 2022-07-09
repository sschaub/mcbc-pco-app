<template>

    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate  />
    </div>
    <div v-if="service.name" class="report">
      <h2>{{ service.name }} - A/V Music Details</h2>

      
      <div v-for="item in items">
        <h3>{{ item.description }}: {{ item.title }} ({{ item.genre_note }})</h3>
        <table>
          <tr>
            <td>Personnel:</td>
            <td>{{ item.assigned_to.map( at => at.name ).join(', ') }}</td>
          </tr>
          <tr v-if="item.solo_instruments">
            <td>Solo instruments:</td>
            <td>{{ item.solo_instruments }}</td>
          </tr>
          <tr v-if="item.accomp_instruments">
            <td>Accompaniment:</td>
            <td>{{ item.accomp_instruments }}</td>
          </tr>
          <tr>
            <td>Location:</td>
            <td>{{ item.ministry_location }}</td>
          </tr>
          <tr>
            <td>A/V notes:</td>
            <td>{{ item.staging_notes }}</td>
          </tr>
        </table>
      </div>  

    </div>


</template>

<style scoped>
h2, h3 { margin-top: 10px; }
tr, td { vertical-align: top; }
.report { margin: 10px; }
</style>

<script>

import {ITEM_STATUS_PENDING, ITEM_STATUS_APPROVED, ITEM_STATUS_NOT_SUBMITTED, COPYRIGHT_STATUS_APPROVED, DETAILS_NO, DETAILS_YES } from '../constants.js';

export default {
  name: 'ServiceAVReport',

  props: {
    service_id: String
  },

  data: () => ({
    loading: true,
    items: [],
    service: {},
    positions: [
      { id: 'songleader', title: 'Songleader'}, 
      { id: 'organ', title: 'Organ' },
      { id: 'piano', title: 'Piano' },
      { id: 'piano 2', title: 'Piano 2' }
      ],
  }),  

  methods: {
    
  },

  computed: {
    songs() {
      let item_descrs = this.items.map( item => item.description )
      return this.service.songs.filter( song => song.title && !item_descrs.includes(song.description) )
    }
  },
  
  async mounted() {
    try {
      this.service = {}
      this.loading = true
      let res = await this.$api.getService(this.service_id);
      this.items = res.items
      this.service = res.service
      console.log(this.items)
    } finally {
      this.loading = false
    }
    
  }
}
</script>
