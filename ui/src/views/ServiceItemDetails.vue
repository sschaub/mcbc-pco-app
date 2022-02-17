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
      <span v-if="show_copyright_status">
        <span v-if="isCopyrightOk()">
          <img src="/public/pass.png">
        </span>
        <span v-else>
          <img src="/public/fail.png">
          <v-btn v-if="isAdmin()" @click="approveCopyrightClicked()">Mark Ok</v-btn>
        </span>
      </span>
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

import {COPYRIGHT_STATUS_APPROVED} from '../constants.js';

export default {
  name: 'ServiceItemDetails',

  props: {
    sched_item: {},
    show_copyright_status: {
      type: Boolean,
      default: true
    }
  },

  methods: {
    async approveCopyrightClicked() {
      let result = await this.$api.approveCopyright(this.sched_item.service_type_id, this.sched_item.plan_id, this.sched_item.item_id)
      if (result == 'OK') {
        this.sched_item.copyright_license_status = COPYRIGHT_STATUS_APPROVED
      }

    }
  },

  mounted() {
    
  },  
  
}
</script>

