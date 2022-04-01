<template>
  <div>
    <h3 class="newsection">Song Details</h3>
    <div>Words by {{sched_item.author}}  <span class="missing" v-if="!sched_item.author">Missing info</span></div>
    <div v-if="sched_item.translator">
      Translated by {{sched_item.translator}}
      </div>
    <div>Music by {{sched_item.composer}} <span class="missing" v-if="!sched_item.composer">Missing info</span></div>
    <div v-if="sched_item.arranger">Arranged by {{sched_item.arranger}}</div>
    <div v-if="sched_item.copyright_year && copyrightHolder() || sched_item.copyright">
      <span v-if="sched_item.copyright">{{sched_item.copyright.replace('Copyright', '©')}}
        <span v-if="sched_item.ccli_num">CCLI #{{sched_item.ccli_num}}.</span>
      </span>
      <span v-else>© {{sched_item.copyright_year}} {{copyrightHolder()}}</span>
      <span v-if="show_copyright_status">
        <span v-if="isCopyrightOk(sched_item)">
          <img src="/pass.png">
        </span>
        <span v-else>
          <img src="/fail.png">
          <v-btn v-if="isAdmin()" @click="approveCopyrightClicked()">Mark Ok</v-btn>
        </span>
      </span>
    </div>
    <div v-else>
      <span class="missing">Missing copyright info</span>
    </div>
    <div>
      Keys: 
      <span v-if="sched_item.start_key && sched_item.end_key">{{sched_item.start_key}} - {{sched_item.end_key}}</span>
      <span v-else><span class="missing">Missing info</span></span>
    </div>

    <h3 class="newsection">Instrumentation / Personnel</h3>
    <table class="table-center">
      <tr>
        <th>Special type:</th>
        <td>{{sched_item.genre_note}} <span class="missing" v-if="!sched_item.genre_note">Missing info</span></td>
      </tr>
      <tr>
        <th>Accompaniment:</th>
        <td>
          {{sched_item.accomp_instruments}} <span v-if="!sched_item.accomp_instruments">(Unaccompanied)</span>
        </td>
      </tr>
      <tr>
        <th>Other musician(s):</th>
        <td>
          {{sched_item.other_performers}} <span v-if="!sched_item.other_performers">None</span>
        </td>
      </tr>
    </table>

    <h3 class="newsection">Other Details</h3>
    
    <div>
      <h4>Staging Notes</h4>
      <div>Location: {{sched_item.ministry_location}}</div>
      {{sched_item.staging_notes}}
    </div>
  </div>
</template>

<style scoped>
.newsection { margin-top: 30px; }
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
    },

    copyrightHolder() {
      if (this.sched_item.copyright_holder == 'Other')
        return this.sched_item.copyright_holder_other
      else
        return this.sched_item.copyright_holder
    }
  },

  mounted() {
    
  },  
  
}
</script>

