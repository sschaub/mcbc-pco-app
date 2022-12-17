/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    themes: {
      light: {
        colors: {
          primary: '#2196f3',
          secondary: '#3f51b5',
          accent: '#673ab7',
          error: '#f44336',
          warning: '#ffc107',
          info: '#00bcd4',
          success: '#009688'
        },
      },
    },
  },
})
