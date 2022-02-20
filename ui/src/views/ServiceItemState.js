import { reactive } from "vue";

export const siStore = reactive({
  item: {},
  sched_item: {},
  service: {},

  init() {
    this.item = {};
    this.sched_item = {};
    this.service = {};
  },
});
