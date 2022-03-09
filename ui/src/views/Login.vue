<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">      
        <h2>Login</h2>

        <v-text-field ref="username" v-model="username" label="Email address" type="email" autocomplete="username" />
        <v-text-field v-model="password" label="Password" type="password" autocomplete="current-password" />

        <div v-if="errmsg" class="error">{{ errmsg }}</div>
        <div v-if="msg" >{{ msg }}</div>
        <v-btn @click="login()" :disabled="!username.length || !password.length">Login</v-btn>
        &nbsp;
        <v-btn @click="$router.go(-1)">Cancel</v-btn>

        <br><br>
        <p><a href="javascript:" @click="passwordReminder">Password Reminder</a></p>

        <div v-if="loading">
          <v-progress-circular indeterminate />
        </div>

        <br><br><h3>First time logging in?</h3>
        <div>Click the Password Reminder link above for help.</div>

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
    msg: '',
    loading: false,
    prevRoute: null
  }),

  methods: {
    async login() {
        this.loading = true
        this.errmsg = ''
        this.msg = ''
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
      this.errmsg = ''
      this.msg = ''
      if (this.username.trim().length == 0) {
        this.msg = 'Enter your email address, then click Password Reminder.'
        this.$refs.username.focus()
        return
      }

      this.loading = true
      try {
          let response = await this.$api.passwordReminder(this.username.trim())
          alert(response)
      } finally {
        this.loading = false
      }
    },

  },

  mounted() {
    this.$refs.username.focus()
  },

    // capture previous route
  beforeRouteEnter(to, from, next) {
    next(vm => {
        vm.prevRoute = from
    })
  }

}
</script>
