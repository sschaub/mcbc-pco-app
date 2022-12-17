/**
 * plugins/index.js
 *
 * Automatically included in `./src/main.js`
 */

// Plugins
import { loadFonts } from './webfontloader'
import vuetify from './vuetify'
import router from '@/router'
import myapi from './myapi'


export function registerPlugins (app) {
  loadFonts()
  app.use(router)
  app.use(vuetify)
  
  // Register myapi plugin and expose
  // to all components as this.$api
  app.use(myapi, {
    log: true,
    baseUrl: import.meta.env.VITE_APP_API_URL
  })
}
