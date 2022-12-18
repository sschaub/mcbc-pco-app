<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="!loading">
          <h2>Upcoming Services</h2>
          <v-list v-for="service in serviceList" :key="service.id" class="text-left mx-auto app-list" density="compact">
            <v-list-item  @click="toPath(service.id)" :title="service.name" :subtitle="service.plan_theme" append-icon="mdi-chevron-right">
            </v-list-item>
          </v-list>
        </div>
      </v-col>

    </v-row>
  </v-container>
</template>



<script>

export default {
  name: 'Home',

  data: () => ({
    serviceList: [],
    loading: true
  }),

  methods: {
    toPath(service_id) {
      this.$router.push({ path: `/service/${service_id}` })
    }
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
