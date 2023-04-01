<template>

    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate  />
    </div>
    <div v-if="service.name" class="report">
      <h2>{{ service.name }} - CCLI Report</h2>

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
