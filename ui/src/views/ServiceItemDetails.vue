<template>
  <div>
    <h3 class="newsection">Instrumentation / Personnel</h3>
    <div>
      Special type: {{sched_item.genre_note}} <span class="missing" v-if="!sched_item.genre_note">Missing info</span>
    </div>
    <div>
      Solo instrument(s): {{sched_item.solo_instruments}} <span class="missing" v-if="!sched_item.solo_instruments">Missing info</span>
    </div>
    <div>
      Accompaniment instrument(s): {{sched_item.accomp_instruments}} <span v-if="!sched_item.accomp_instruments">(Unaccompanied)</span>
    </div>
    <div>
      Other musician(s): {{sched_item.other_performers}} <span v-if="!sched_item.other_performers">None</span>
    </div>

    <h3 class="newsection">Song Details</h3>
    <div>
      Author: {{sched_item.author}}  <span class="missing" v-if="!sched_item.author">Missing info</span>
    </div>
    <div v-if="sched_item.translator">
      Translator: {{sched_item.translator}}
    </div>
    <div>
      Composer: {{sched_item.composer}} <span class="missing" v-if="!sched_item.composer">Missing info</span>
    </div>
    <div>
      Arranger: {{sched_item.arranger}} <span class="missing" v-if="!sched_item.arranger">None</span>
    </div>
    <div v-if="sched_item.copyright_year && sched_item.copyright_holder">
      Copyright: {{sched_item.copyright_year}} {{sched_item.copyright_holder}}
      <span v-if="show_copyright_status">
        <span v-if="isCopyrightOk(sched_item)">
          <img src="/public/pass.png">
        </span>
        <span v-else>
          <img src="/public/fail.png">
          <v-btn v-if="isAdmin()" @click="approveCopyrightClicked()">Mark Ok</v-btn>
        </span>
      </span>
    </div>
    <div v-else>
      Copyright: <span class="missing">Missing info</span>
    </div>
    <div>
      Keys: {{sched_item.start_key}} - {{sched_item.end_key}}  <span class="missing" v-if="!sched_item.start_key || !sched_item.end_key">Missing info</span>
    </div>

    <h3 class="newsection">Other Details</h3>
    
    <div>
      <h4>Staging Notes</h4>
      <div>Location: {{sched_item.ministry_location}}</div>
      {{sched_item.staging_notes}}
    </div>
    <div>
      <h4>Song Text</h4>
      <div v-html="sched_item.song_text.replace(/\n/g, '<br>')"></div>
      <div class="missing" v-if="!sched_item.song_text">Missing info</div>
    </div>
  </div>
</template>

<style scoped>
.newsection { margin-top: 30px; }
.missing { background-color: yellow; padding-left: 5px; padding-right: 5px; }
</style>

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

