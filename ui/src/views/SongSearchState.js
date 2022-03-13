import { reactive } from 'vue'

export const ssStore = reactive({
    isPicker: false,
    showHelp: true,
    keywords: "",
    searchType: "T",  // T - Title, L - Lyrics
    songList: [],
    song: {},
    arrangement: {},
    arrList: [],
    selectionOccurred: false,

    init(isPicker) {
        this.isPicker = isPicker
        this.showHelp = isPicker
        this.songList = []
        this.keywords = ''
        this.arrList = ''
        this.searchType = 'T'
        this.selectionOccurred = false
    },

    finishEntry() {
        this.selectionOccurred = true        
    },
})
