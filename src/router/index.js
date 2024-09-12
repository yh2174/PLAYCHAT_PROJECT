import { createRouter, createWebHistory } from 'vue-router';
import Register from '../components/Register.vue';
import Login from '../components/Login.vue';
import MainView from '../views/MainView.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login, meta: { title: '로그인' } },
  { path: '/register', component: Register, meta: { title: '회원가입' } },
  { path: '/main', component: MainView, meta: { title: '메인', requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 페이지 제목 설정
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '기본 제목';
  
  if (to.meta.requiresAuth && !sessionStorage.getItem('username')) {
    next('/login');
  } else {
    next();
  }
});

export default router;
