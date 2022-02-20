import {ITEM_STATUS_PENDING, ITEM_STATUS_APPROVED, COPYRIGHT_STATUS_APPROVED} from './constants.js';


export default {
    methods: {

        // view helpers
        itemPeople(people) {
            if (people)
                return people.map(p => p.name).join(", ")
        },

        isPending(sched_item) {
            return sched_item.status == ITEM_STATUS_PENDING && sched_item.title
        },
        isCopyrightOk(sched_item) {
            return sched_item.copyright_license_status == COPYRIGHT_STATUS_APPROVED
        },

        // authentication utilities

        setUser(user) {
            localStorage.user = JSON.stringify(user)
        },

        getUser() {
            if (localStorage.user) {
                return JSON.parse(localStorage.user)
            }
        },

        isAdmin() {
            let user = this.getUser()
            return user && user.user_type == 1
        },
    }
}