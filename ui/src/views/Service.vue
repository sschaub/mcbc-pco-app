<template>
  <!-- <v-breadcrumbs>
    <v-list>
      <v-list-item to="/">All Services</v-list-item>
    </v-list>
  </v-breadcrumbs> -->
  <v-container>
    <v-row class="text-center">
      <div class="ssbreadcrumb"><a href="/">Services</a></div>
      <v-col cols="12">
        <div v-if="!service.name">
          <v-progress-circular indeterminate />
        </div>
        <div v-if="service.name">
          <h2>{{ service.name }} Service</h2>
          <h3 v-if="service.theme" >Theme: {{ service.theme }}</h3>

          <div v-for="position in positions">
            <div v-if="service.personnel[position.id]">{{position.title}}: {{ service.personnel[position.id] }}</div>
          </div>

          <div v-for="item in items" :key="item.id">
            <h4>{{ item.description}}</h4>
            <div v-if="item.title != item.description">{{ item.title}}</div>
            <div v-if="item.assigned_to.length">{{ itemPeople(item.assigned_to) }}</div>
            <v-btn :href="toPath(item.id)" text="Details"/>
            
          </div>

          <div v-if="service.songs.length">
            <br>
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
    positions: [
      { id: 'songleader', title: 'Songleader'}, 
      { id: 'organ', title: 'Organ' },
      { id: 'piano', title: 'Piano' },
      { id: 'piano 2', title: 'Piano 2' }
      ]
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
