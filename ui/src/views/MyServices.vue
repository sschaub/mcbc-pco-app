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
            <v-list-item lines="three" @click="toPath(service.id)">
              <v-list-item-header>
              <v-list-item-title>
                {{ service.name }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ service.plan_theme }}
              </v-list-item-subtitle>
              </v-list-item-header>
              
              <v-icon color="indigo">
                mdi-chevron-right
              </v-icon>
            
            </v-list-item>
          </v-list>
          <div v-else>You are not currently scheduled for any upcoming services.</div>
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
    } catch (err) {
      if (err.response && err.response.status == 401) {
        this.$router.push({ path:'/login' })
      } else {
        console.log(err);
      }
    } finally {
      this.loading = false
    }
    
  }
}
</script>
