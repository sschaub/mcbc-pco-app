<template>
  <div>
    <h3>Instrumentation / Personnel</h3>
    <div v-if="sched_item.genre_note">
      Special type: {{sched_item.genre_note}}
    </div>
    <div v-if="sched_item.solo_instruuments">
      Solo instruments: {{sched_item.solo_instruments}}
    </div>
    <div v-if="sched_item.accomp_instruments">
      Accompaniment instruments: {{sched_item.accomp_instruments}}
    </div>
    <div v-if="sched_item.other_performers">
      Other performers: {{sched_item.other_performers}}
    </div>

    <h3>Song Details</h3>
    <div v-if="sched_item.author">
      Author: {{sched_item.author}}
    </div>
    <div v-if="sched_item.translator">
      Translator: {{sched_item.translator}}
    </div>
    <div v-if="sched_item.composer">
      Composer: {{sched_item.composer}}
    </div>
    <div v-if="sched_item.arranger">
      Arranger: {{sched_item.arranger}}
    </div>
    <div v-if="sched_item.copyright_year || sched_item.copyright_holder">
      Copyright: {{sched_item.copyright_year}} {{sched_item.copyright_holder}}
        <span v-if="isCopyrightOk()">
          <img src="/public/pass.png">
        </span>
        <span v-if="!isCopyrightOk()">
          <img src="/public/fail.png">
        </span>
        <v-btn v-if="!isCopyrightOk()" @click="approveCopyrightClicked()">Mark Ok</v-btn>
    </div>
    <div v-if="sched_item.start_key">
      Starting Key: {{sched_item.start_key}}
    </div>
    <div v-if="sched_item.end_key">
      Ending Key: {{sched_item.end_key}}
    </div>

    <h3>Other Details</h3>
    <div v-if="sched_item.staging_notes">
      <h4>Staging Notes</h4>
      {{sched_item.staging_notes}}
    </div>
    <div v-if="sched_item.song_text">
      <h4>Song Text</h4>
      <div v-html="sched_item.song_text.replace(/\n/g, '<br>')"></div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'ServiceItemDetails',

  props: {
    sched_item: {}
  },

  methods: {

  },

  mounted() {
    
  },  
  
}
</script>

