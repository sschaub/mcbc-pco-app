<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="!loading">
          <h2>Services</h2>
          <ul v-for="service in serviceList" :key="service.id">
            <v-btn :href="toPath(service.id)">
              {{ service.name }}
            </v-btn>
          </ul>
        </div>
      </v-col>

    </v-row>
  </v-container>
</template>

<style>
  ul { margin: 15px }
</style>

<script>

export default {
  name: 'Home',

  data: () => ({
    serviceList: [],
    loading: true
  }),

  methods: {
    toPath: (service_id) => `/service/${service_id}`
  },

  async mounted() {
    try {
      this.serviceList = await this.$api.getServices()
    } finally {
      this.loading = false
    }
    
  }
}
</script>
