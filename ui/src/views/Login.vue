<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">      
        <h2>Login</h2>

        <v-text-field v-model="username" label="Email address" type="email" autocomplete="username" />
        <v-text-field v-model="password" label="Password" type="password" autocomplete="current-password" />
        <p><a href="javascript:" @click="passwordReminder">Password Reminder</a></p>

        <div v-if="errmsg">{{ errmsg }}</div>
        <v-btn @click="login()" :disabled="!username.length || !password.length">Login</v-btn>

        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>

      </v-col>

    </v-row>
  </v-container>
</template>

<script>


export default {
  name: 'Login',

  data: () => ({
    username: localStorage.username || '', 
    password: '',
    errmsg: '',
    loading: false,
    prevRoute: null
  }),

  methods: {
    async login() {
        this.loading = true
        this.errmsg = ''
        try {

          let response = await this.$api.login(this.username.trim(), this.password.trim())
          if (response.token) {
            localStorage.api_auth = response.token
            this.setUser(response.user)

            if (this.prevRoute.path == '/') {
              // User started on login page
              this.$router.replace({ name: 'Home' })
            } else {
              // Login triggered during use of app
              this.$router.go(-1)
            }
            
          } else {
            alert('Invalid username or password.')
          }
        } catch (err) {
          if (err.response && err.response.status == 401) {
            this.errmsg = 'Invalid username or password.'
          } else {
            this.errmsg = 'Problem processing login. Please try again later.'
            console.log(err)
          }          
        } finally {
          this.loading = false
        }
    },

    async passwordReminder() {
      if (this.username.trim().length == 0 || this.password.trim().length == 0)
        return

      this.errmsg = ''
      this.loading = true
      try {
          let response = await this.$api.passwordReminder(this.username.trim())
          this.errmsg = response
      } finally {
        this.loading = false
      }
    },

  },

    // capture previous route
  beforeRouteEnter(to, from, next) {
    next(vm => {
        vm.prevRoute = from
    })
  }

}
</script>
