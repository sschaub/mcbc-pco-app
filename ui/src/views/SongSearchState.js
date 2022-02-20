import { reactive } from 'vue'

export const ssStore = reactive({
    keywords: "",
    songList: [],
    song: {},
    arrangement: {},
    arrList: [],

    init() {
        this.songList = []
        this.keywords = ''
        this.arrList = ''
    },

    finishEntry(api, siStore) {
        siStore.sched_item.song_id = this.song.id
        siStore.sched_item.title = this.song.title
        siStore.sched_item.author = this.song.author
        siStore.sched_item.arrangement_id = this.arrangement.id
        siStore.sched_item.arrangement_name = this.arrangement.name        
        if (this.arrangement.id) {
            siStore.sched_item.author = this.arrangement.author
            siStore.sched_item.copyright_holder = this.arrangement.copyright_holder
            siStore.sched_item.copyright_year = this.arrangement.copyright_year
            siStore.sched_item.start_key = this.arrangement.start_key
            siStore.sched_item.end_key = this.arrangement.end_key
            siStore.sched_item.song_text = this.arrangement.lyrics
            siStore.sched_item.composer = this.arrangement.composer
            siStore.sched_item.arranger = this.arrangement.arranger        
            siStore.sched_item.translator = this.arrangement.translator
        } else if (this.song.id) {
            siStore.sched_item.title = this.song.title
            siStore.sched_item.author = this.song.author
            siStore.sched_item.composer = this.song.composer
            siStore.sched_item.song_text = this.song.lyrics
            siStore.sched_item.copyright_holder = this.song.copyright_holder
            siStore.sched_item.copyright_year = this.song.copyright_year
        }
    },
})
