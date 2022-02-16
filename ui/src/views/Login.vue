<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">      
        <h2>Login</h2>

        <v-text-field v-model="username" label="Email address or Phone number" />
        <v-text-field v-model="password" label="Password" />
        <div v-if="errmsg">{{ errmsg }}</div>
        <v-btn @click="login()">Login</v-btn>

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
    loading: false
  }),

  methods: {
    async login() {
        this.loading = true
        this.errmsg = ''
        try {
          if (this.username.trim().length == 0 || this.password.trim().length == 0)
            return

          let response = await this.$api.login(this.username.trim(), this.password.trim())
          if (response.token) {
            localStorage.api_auth = response.token
            this.setUser(response.user)
            this.$router.go(-1)        
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
  }
}
</script>
