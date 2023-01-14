import { reactive } from "vue";

import {SISTATE_INITIAL} from '../constants.js';

export const siStore = reactive({
  item: {},
  sched_item: {},
  service: {},
  copyright_holders: [],
  state: SISTATE_INITIAL,

  init() {
    this.item = {}
    this.sched_item = {}
    this.service = {}
    this.copyright_holders = []
    this.state = SISTATE_INITIAL
  },
});
