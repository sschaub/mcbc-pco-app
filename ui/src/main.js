import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import myapi from './plugins/myapi'
import { loadFonts } from './plugins/webfontloader'
import mixins from './mixins.js'

loadFonts()

console.log(`API URL: ${import.meta.env.VITE_APP_API_URL}`)

let app = createApp(App)
  .use(router)  
  .use(vuetify)
  // Register myapi plugin and expose
  // to all components as this.$api
  .use(myapi, {
    log: true,
    baseUrl: import.meta.env.VITE_APP_API_URL
  })

app.mixin(mixins)
app.mount('#app')

  