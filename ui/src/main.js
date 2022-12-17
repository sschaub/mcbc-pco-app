/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

import { createApp } from 'vue'
import App from './App.vue'
import mixins from './mixins.js'
import { registerPlugins } from '@/plugins'

console.log(`API URL: ${import.meta.env.VITE_APP_API_URL}`)

let app = createApp(App)
  
registerPlugins(app)

app.mixin(mixins)
app.mount('#app')

  