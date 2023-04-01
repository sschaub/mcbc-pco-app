<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="!loading">
          <h2>{{ title }}</h2>
          <v-list v-for="service in serviceList" :key="service.id" class="text-left mx-auto app-list" density="compact">
            <v-list-item  @click="toPath(service.id)" :title="service.name" :subtitle="service.plan_theme" append-icon="mdi-chevron-right">
            </v-list-item>
          </v-list>
          <v-btn @click="switchServiceList()">{{  btnTitle }}</v-btn>
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
    loading: true,
    future: true,    
  }),

  computed: {
    title() {
      return this.future ? 'Upcoming Services' : 'Recent Services'
    },
    btnTitle() {
      return this.future ? 'Show Recent Services' : 'Show Upcoming Services'
    },
  },

  methods: {
    toPath(service_id) {
      this.$router.push({ path: `/service/${service_id}` })
    },
    switchServiceList() {
      this.future = !this.future
      this.showServices(this.future ? 'future' : 'past')
    },
    async showServices(when) {      
      this.loading = true
      try {
        this.serviceList = await this.$api.getServices(when)
      } finally {
        this.loading = false

      }
    }
  },

  async mounted() {
    this.showServices('future')
    
  }
}
</script>
