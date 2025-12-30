<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>회원가입</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="register" ref="form">
              <v-text-field
                v-model="username"
                label="사용자명"
                :rules="usernameRules"
                :error-messages="usernameError"
                required
                counter="30"
                hint="3~30자, 영문/숫자/밑줄(_)만 사용 가능"
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="비밀번호"
                :type="showPassword ? 'text' : 'password'"
                :rules="passwordRules"
                required
                counter
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
              ></v-text-field>
              
              <!-- 비밀번호 강도 표시 -->
              <div class="password-strength mb-2">
                <v-progress-linear
                  :model-value="passwordStrength"
                  :color="passwordStrengthColor"
                  height="4"
                ></v-progress-linear>
                <span class="text-caption" :class="passwordStrengthColor + '--text'">
                  {{ passwordStrengthText }}
                </span>
              </div>
              
              <!-- 비밀번호 정책 체크리스트 -->
              <div class="password-policy mb-3">
                <div :class="{ 'text-success': hasMinLength, 'text-grey': !hasMinLength }">
                  <v-icon size="small">{{ hasMinLength ? 'mdi-check-circle' : 'mdi-circle-outline' }}</v-icon>
                  최소 8자 이상
                </div>
                <div :class="{ 'text-success': hasLetter, 'text-grey': !hasLetter }">
                  <v-icon size="small">{{ hasLetter ? 'mdi-check-circle' : 'mdi-circle-outline' }}</v-icon>
                  영문자 포함
                </div>
                <div :class="{ 'text-success': hasNumber, 'text-grey': !hasNumber }">
                  <v-icon size="small">{{ hasNumber ? 'mdi-check-circle' : 'mdi-circle-outline' }}</v-icon>
                  숫자 포함
                </div>
              </div>

              <v-text-field
                v-model="passwordConfirm"
                label="비밀번호 확인"
                :type="showPasswordConfirm ? 'text' : 'password'"
                required
                :rules="passwordConfirmRules"
                :append-inner-icon="showPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
              ></v-text-field>
              <v-btn 
                type="submit" 
                color="primary" 
                :disabled="!isFormValid"
                :loading="isLoading"
                block
                class="mt-2"
              >
                회원가입
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              variant="text"
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
      showPassword: false,
      showPasswordConfirm: false,
      isLoading: false,
      usernameError: '',
      usernameRules: [
        v => !!v || '사용자명을 입력해주세요.',
        v => (v && v.length >= 3) || '최소 3자 이상이어야 합니다.',
        v => (v && v.length <= 30) || '최대 30자까지 가능합니다.',
        v => /^[a-zA-Z0-9_]+$/.test(v) || '영문, 숫자, 밑줄(_)만 사용 가능합니다.',
      ],
      passwordRules: [
        v => !!v || '비밀번호를 입력해주세요.',
        v => (v && v.length >= 8) || '최소 8자 이상이어야 합니다.',
        v => (v && v.length <= 128) || '최대 128자까지 가능합니다.',
        v => /[A-Za-z]/.test(v) || '영문자를 포함해야 합니다.',
        v => /\d/.test(v) || '숫자를 포함해야 합니다.',
      ],
      passwordConfirmRules: [
        v => !!v || '비밀번호 확인을 입력해주세요.',
        v => v === this.password || '비밀번호가 일치하지 않습니다.',
      ],
    };
  },
  computed: {
    hasMinLength() {
      return this.password.length >= 8;
    },
    hasLetter() {
      return /[A-Za-z]/.test(this.password);
    },
    hasNumber() {
      return /\d/.test(this.password);
    },
    hasSpecialChar() {
      return /[!@#$%^&*(),.?":{}|<>]/.test(this.password);
    },
    passwordStrength() {
      let strength = 0;
      if (this.hasMinLength) strength += 25;
      if (this.hasLetter) strength += 25;
      if (this.hasNumber) strength += 25;
      if (this.hasSpecialChar) strength += 25;
      return strength;
    },
    passwordStrengthColor() {
      if (this.passwordStrength <= 25) return 'error';
      if (this.passwordStrength <= 50) return 'warning';
      if (this.passwordStrength <= 75) return 'info';
      return 'success';
    },
    passwordStrengthText() {
      if (!this.password) return '';
      if (this.passwordStrength <= 25) return '약함';
      if (this.passwordStrength <= 50) return '보통';
      if (this.passwordStrength <= 75) return '강함';
      return '매우 강함';
    },
    isFormValid() {
      return this.username 
        && this.username.length >= 3
        && /^[a-zA-Z0-9_]+$/.test(this.username)
        && this.hasMinLength 
        && this.hasLetter 
        && this.hasNumber 
        && this.password === this.passwordConfirm;
    },
  },
  methods: {
    async register() {
      if (!this.isFormValid) {
        return;
      }
      this.isLoading = true;
      this.usernameError = '';
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
        const message = error.response?.data?.message || '회원가입 중 오류가 발생했습니다.';
        if (message.includes('사용자명')) {
          this.usernameError = message;
        } else {
          alert(message);
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.password-policy {
  font-size: 0.85rem;
}
.password-policy > div {
  display: flex;
  align-items: center;
  gap: 4px;
}
.password-strength {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
</style>
