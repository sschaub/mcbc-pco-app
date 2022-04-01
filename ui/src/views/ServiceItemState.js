import { reactive } from "vue";

export const siStore = reactive({
  item: {},
  sched_item: {},
  service: {},
  copyright_holders: [],

  init() {
    this.item = {}
    this.sched_item = {}
    this.service = {}
    this.copyright_holders = []
  },
});
