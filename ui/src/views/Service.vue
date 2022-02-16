<template>
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
            <v-btn :href="toPath(service_id, item.id)" text="Details"/>
            
          </div>
        </div>
      </v-col>

    </v-row>
  </v-container>
</template>

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
    toPath: (service_id, item_id) => `/service/${service_id}/${item_id}`
  },
  
  async mounted() {
    let res = await this.$api.getService(this.service_id);
    this.items = res.items
    this.service = res.service
  }
}
</script>
