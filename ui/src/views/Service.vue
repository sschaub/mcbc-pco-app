<template>
    <v-breadcrumbs density="compact">
      <v-list density="compact">
        <v-list-item to="/">All Services</v-list-item>
      </v-list>
    </v-breadcrumbs>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <div v-if="!service.name">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="service.name">
          <h2>{{ service.name }} Service</h2>
          <h3 v-if="service.theme" >{{ service.theme }}</h3>
          <div v-for="item in items" :key="item.id">
            <h4>{{ item.description}}</h4>
            <div v-if="item.title != item.description">Title: {{ item.title}}</div>
            <div v-if="item.arrangement">Arrangement: {{ item.arrangement}}</div>            
            <div v-if="item.assigned_to.length">Assigned to: {{ itemPeople(item.assigned_to) }}</div>
            <v-btn :href="toPath(item.id)" text="Details"/>
            
          </div>

          <div v-if="service.songs.length">
            <h3>Congregational Songs</h3>
            <div v-for="song in service.songs" :key="song.id">
                  <p v-if="song.description.includes('Song')">{{ song.title }} <span v-if="song.arrangement">- {{ song.arrangement }}</span></p>
            </div>
          </div>

        </div>
      </v-col>

    </v-row>
  </v-container>
</template>

<style scoped>
  .v-breadcrumbs { padding: 0px !important; }
</style>

<script>

export default {
  name: 'Service',

  props: {
    service_id: String
  },

  data: () => ({
    items: [],
    service: {}, 
  }),  

  methods: {
    toPath(item_id) { return `/service/${this.service_id}/${item_id}` }
  },
  
  async mounted() {
    let res = await this.$api.getService(this.service_id);
    this.items = res.items
    this.service = res.service
  }
}
</script>
