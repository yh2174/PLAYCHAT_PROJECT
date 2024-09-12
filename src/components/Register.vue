<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>회원가입</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="register">
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
              <v-text-field
                v-model="passwordConfirm"
                label="비밀번호 확인"
                type="password"
                required
                :error-messages="passwordMatchError"
              ></v-text-field>
              <v-btn type="submit" color="primary" :disabled="!isFormValid">회원가입</v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              text
              color="primary"
              @click="$router.push('/login')"
            >
              계정이 있다면 로그인
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
  name: 'Register',
  data() {
    return {
      username: '',
      password: '',
      passwordConfirm: '',
    };
  },
  computed: {
    passwordMatchError() {
      return this.password !== this.passwordConfirm ? '비밀번호 확인' : '';
    },
    isFormValid() {
      return this.username && this.password && this.password === this.passwordConfirm;
    },
  },
  methods: {
    async register() {
      if (!this.isFormValid) {
        return;
      }
      try {
        const response = await axios.post('/api/register', {
          username: this.username,
          password: this.password,
        });
        if (response.data.success) {
          alert(response.data.message);
          this.$router.push('/login');
        }
      } catch (error) {
        alert(error.response.data.message);
      }
    },
  },
};
</script>

<style scoped>
/* 스타일 추가 가능 */
</style>
