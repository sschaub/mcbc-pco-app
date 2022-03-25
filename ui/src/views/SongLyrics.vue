<template> 
  <div>
    <h4>Song Text</h4>
    <div v-if="!lyrics" :class="missingClass" >Missing info</div>
    <table v-else class="table-center">
      <tr><td v-html="lyrics.replace(/\n/g, '<br>')"></td></tr>
    </table>
  </div>

</template>

<style scoped>
.missing { background-color: yellow; padding-left: 5px; padding-right: 5px; }
.table-center {
  margin-left: auto;
  margin-right: auto;
}
.table-center th {
  text-align: right;
  font-weight: normal;
}
.table-center td {
  text-align: left;
}

</style>

<script>

export default {
  name: 'SongLyrics',

  props: {
    lyrics: '',
    missingClass: ''
  },

  methods: {

  },

  mounted() {
    
  },  
  
}
</script>

