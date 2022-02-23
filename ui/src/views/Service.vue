<template>
  <!-- <v-breadcrumbs>
    <v-list>
      <v-list-item to="/">All Services</v-list-item>
    </v-list>
  </v-breadcrumbs> -->
  <v-container fluid>
    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate  />
    </div>
    <v-row class="text-center">
      <!-- <div class="ssbreadcrumb"><a href="/">Services</a></div> -->
      <v-col cols="12">
        <div v-if="service.name">
          <h2>{{ service.name }}</h2>
          <h3 v-if="service.theme" >{{ service.theme }}</h3>
          <div v-for="position in positions">
            <div v-if="service.personnel[position.id]">{{position.title}}: {{ service.personnel[position.id] }}</div>
          </div>
        </div>

      </v-col>
      <v-col cols="12"  sm="6" md="6">
        <div v-if="service.name">

          <div v-if="items.length">
            <h3 class="subhead">Specials</h3>
            <v-list lines="three" v-for="item in items" :key="item.id" density="compact" class="mx-auto app-list">
              <v-list-item two-line @click="toPath(item.id)" density="compact" class="text-left" >
                <v-list-item-header>
                  <v-list-item-title>{{ item.description }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <div v-if="item.assigned_to.length">{{ itemPeople(item.assigned_to) }}</div>
                    {{ item.title }}
                  </v-list-item-subtitle>
                  </v-list-item-header>
                
                  <v-icon color="indigo">
                    mdi-chevron-right
                  </v-icon>
                
                </v-list-item>
                <v-divider></v-divider>
            </v-list>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="6">
        <div v-if="service.name">
          <div v-if="songs.length">
            <h3 class="subhead">Congregational Songs</h3>
            <v-list v-for="song in songs" :key="song.id" class="mx-auto app-list">
              <v-list-item two-line density="compact" class="text-left">
                <v-list-item-header>
                  <v-list-item-title>{{ song.title }}</v-list-item-title>
                  <v-list-item-subtitle v-if="song.arrangement">{{ song.arrangement }}</v-list-item-subtitle>
                </v-list-item-header>
              </v-list-item>
            </v-list>
          </div>

          <h3 class="subhead" v-if="selected_tags.length">Song Themes</h3>
          <v-list v-for="tag in service.tags" :key="tag.id" class="mx-auto app-list">
              <v-list-item two-line density="compact" class="text-left">
                <v-list-item-header>
                  <v-list-item-title>{{ tag.tag_name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ tag.tag_group_name }}</v-list-item-subtitle>
                </v-list-item-header>
              </v-list-item>
            </v-list>          

        </div>

        <div v-if="isAdmin()">
          <v-btn v-if="!assignTags" @click="assignTagsClicked()">Assign Song Tags</v-btn>

          <div v-else>
            <h2>Assign Tags</h2>
            <p>Select the tags to assign to this service, then choose Save:</p>
            <div v-for="tag in tags" :key="tag.id">
              <v-checkbox v-model="selected_tags" :label="`${tag.tag_group_name} - ${tag.tag_name}`" :value="tag.id" density="compact"  hide-details="true" />
            </div>

            <v-btn @click="saveClicked()">Save</v-btn> &nbsp;
            <v-btn @click="assignTags = false">Cancel</v-btn>
          </div>
        </div>
        

      </v-col>

    </v-row>
  </v-container>
</template>

<style scoped>  
  .v-breadcrumbs { padding: 0px !important; }
  .v-list, .v-list-item { padding: 0px !important; }
  
</style>

<script>

export default {
  name: 'Service',

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
    assignTags: false,
    tags: [],
    selected_tags: []
  }),  

  methods: {
    toPath(item_id) { 
      this.$router.push( { path: `/service/${this.service_id}/${item_id}` }  )
    },

    async assignTagsClicked() {
      this.loading = true
      try {
        this.tags = await this.$api.getTags()
        this.assignTags = true
      } finally {
        this.loading = false
      }      
    },

    async saveClicked() {
      this.loading = true
      try {
        let response = await this.$api.updateServiceTags(this.service_id, this.selected_tags)
        if (response.result == 'OK') {
          let res = await this.$api.getService(this.service_id);
          this.service = res.service
          this.selected_tags = res.service.tags.map( tag => tag.tag_id )
          this.assignTags = false
        }
          
      } finally {
        this.loading = false
      }      
    }
  },

  computed: {
    songs() {
      return this.service.songs.filter( song => song.description.includes('Song') && song.title )
    }
  },
  
  async mounted() {
    try {
      this.service = {}
      this.loading = true
      let res = await this.$api.getService(this.service_id);
      this.items = res.items
      this.service = res.service
      this.selected_tags = res.service.tags.map( tag => tag.id )
      console.log(this.selected_tags[0])
    } finally {
      this.loading = false
    }
    
  }
}
</script>
