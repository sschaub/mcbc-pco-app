// myapi.js
// - Exposes ApiService class instance to all components in this application via the property this.$api

import axios from "axios"

// From https://medium.com/@danielalvidrez/vue-plugin-blueprint-api-service-47ea5f3258d4
class ApiService {

    /** Vue $api Prototype **/
    constructor(options = OPTIONS){
       this.$http = axios.create({
          baseURL: options.baseUrl,
          timeout: 5000,
          headers: {
             'Accept': 'application/json',
             'Content-Type': 'application/json',
             //'X-Requested-With': 'XMLHttpRequest', 
          }
       })
       this.options = options
       this.bindInterceptors()
    //    this.mapRoutes()
    }

    bindInterceptors(){
        // Include API authorization with request header
        this.$http.interceptors.request.use((request) => {
            if(localStorage.api_auth){
                request.headers = {
                    Authorization: 'Bearer ' + localStorage.api_auth,
                }
            }
            return request
          })
        // this.$http.interceptors.response.use(
        //     (response) => response, 
        //     (error) => this.httpError(error)
        // )
    }     

    log(msg) {
        if (this.options.log) {
            console.log(msg)
        }
    }

    /**
     * Send get request
     **/
    async get(url){
        this.log(`Requesting ${url}...`)
        const response = await this.$http.get(url)
        this.log("Received response:")
        this.log(response)
        return response.data
    }

    /**
     * Send update request
     **/
     async post(url, data) {
        this.log(`Sending post ${url}...`)
        const response = await this.$http.post(url, data)
        this.log("Received response:")
        this.log(response)
        return response.data
    }

    login(username, password) {
        return this.post(`/login`, { 'username': username, 'password': password })
    }

    getServices() {
        return this.get(`/services`)
    }    

    getService(service_id) {
        return this.get(`/service/${service_id}`)
    }

    /**
     * returns {
     *   item: { 
     *      id: int
     *      item_seq: int
     *      description: str
     *      title: str
     *      arrangement: str
     *      arrangement_id: int
     *      person: str
     *      system: str - json string stored in PCO service item under the "System" note category
     *      system_id: int - id of "System" note
     *   }
     *   service: { 
     *      name: str
     *      theme: str 
     *   }
     *   sched_item: SchedSpecial
     * } 
     */
    getServiceItem(service_id, item_id) {
        return this.get(`/service/${service_id}/${item_id}`)
    }

    /**
     * returns: See getServiceItem()
     */
    beginEditServiceItem(service_id, item_id) {
        return this.post(`/service/${service_id}/${item_id}/edit`)
    }

    updateServiceItem(service_id, item_id, itemData) {
        return this.post(`/service/${service_id}/${item_id}`, itemData)
    }

    approveServiceItem(service_id, item_id) {
        return this.post(`/service/${service_id}/${item_id}/approve`)
    }


    searchSongs(title) {
        return this.get(`/song_search?title=${title}`)
    }

    getArrangements(songId) {
        return this.get(`/song/${songId}/arrangements`)
    }
 }
 

export default {
    install: (app, options) => {
        // Expose ApiService to components as this.$api
        app.config.globalProperties.$api = new ApiService(options)
    }
}
