<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="!loading">
          <h2>My Services</h2>
          <v-list v-if="serviceList.length" v-for="service in serviceList" :key="service.id" class="text-left mx-auto app-list" density="compact">
            <v-list-item lines="2" @click="toPath(service.id)" :title="service.name" :subtitle="service.plan_theme" append-icon="mdi-chevron-right">
            </v-list-item>
          </v-list>
          <div v-else>{{ msg }}</div>
        </div>
      </v-col>

    </v-row>
  </v-container>
</template>



<script>

export default {
  name: 'MyServices',

  data: () => ({
    serviceList: [],
    msg: "",
    loading: true
  }),

  methods: {
    toPath(service_id) {
      this.$router.push({ path: `/service/${service_id}` })
    }
  },

  async mounted() {
    try {
      this.serviceList = await this.$api.getMyServices()
      if (this.serviceList.length == 0) {
        this.msg = "You are not currently scheduled for any upcoming services."
      }
    } catch (err) {
      if (err.response && err.response.status == 401) {
        this.$router.push({ path:'/login' })
      } else {
        console.log(err);
        this.msg = "Problem loading information. Please try again."
      }
    } finally {
      this.loading = false
    }
    
  }
}
</script>
