<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>로그인</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="login">
              <v-text-field
                v-model="username"
                label="사용자명"
                required
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="비밀번호"
                type="password"
                required
              ></v-text-field>
              <v-btn type="submit" color="primary">로그인</v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              text
              color="primary"
              @click="$router.push('/register')"
            >
              계정이 없다면 회원가입
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('/api/login', {
          username: this.username,
          password: this.password,
        });
        if (response.data.success) {
          sessionStorage.setItem('username', response.data.username);
          this.$router.push('/main');
        }
      } catch (error) {
        alert(error.response.data.message);
      }
    },
  },
};
</script>
