// Styles
import '../styles/variables.scss'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Vuetify
import { createVuetify } from 'vuetify'


export default createVuetify({
  theme: {
    themes: {
      'light': {
        colors: 
        {
          primary: '#2196f3',
          secondary: '#3f51b5',
          accent: '#673ab7',
          error: '#f44336',
          warning: '#ffc107',
          info: '#00bcd4',
          success: '#009688'
        }
      }
    }
  }
})