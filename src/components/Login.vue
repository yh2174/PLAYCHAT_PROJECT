<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>로그인</v-card-title>
          <v-card-text>
            <v-alert
              v-if="errorMessage"
              type="error"
              variant="tonal"
              closable
              class="mb-4"
              @click:close="errorMessage = ''"
            >
              {{ errorMessage }}
            </v-alert>
            <v-form @submit.prevent="login" ref="form">
              <v-text-field
                v-model="username"
                label="사용자명"
                :rules="[v => !!v || '사용자명을 입력해주세요.']"
                required
                autocomplete="username"
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="비밀번호"
                :type="showPassword ? 'text' : 'password'"
                :rules="[v => !!v || '비밀번호를 입력해주세요.']"
                required
                autocomplete="current-password"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
              ></v-text-field>
              <v-btn 
                type="submit" 
                color="primary" 
                :loading="isLoading"
                :disabled="!username || !password"
                block
                class="mt-2"
              >
                로그인
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              variant="text"
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
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      isLoading: false,
      errorMessage: '',
    };
  },
  methods: {
    async login() {
      if (!this.username || !this.password) {
        this.errorMessage = '사용자명과 비밀번호를 입력해주세요.';
        return;
      }
      
      this.isLoading = true;
      this.errorMessage = '';
      
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
        if (error.response?.status === 429) {
          this.errorMessage = '너무 많은 로그인 시도가 있었습니다. 잠시 후 다시 시도해주세요.';
        } else {
          this.errorMessage = error.response?.data?.message || '로그인 중 오류가 발생했습니다.';
        }
        // 보안: 비밀번호 필드 초기화
        this.password = '';
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
