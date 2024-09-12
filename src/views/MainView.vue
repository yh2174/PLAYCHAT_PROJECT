<template>
  <div class="main-container">
    <VideoPlayer :key="componentKey" class="video-player" />
    <ChatView :key="componentKey" class="chat-view" />
  </div>
</template>

<script>
import VideoPlayer from '@/components/VideoPlayer.vue';
import ChatView from '@/components/ChatView.vue';

export default {
  name: 'MainView',
  components: {
    VideoPlayer,
    ChatView
  },
  data() {
    return {
      componentKey: 0,
    };
  },
  created() {
    if (!sessionStorage.getItem('username')) {
      this.$router.push('/login');
    } else {
      // 컴포넌트 키를 변경하여 강제 리렌더링
      this.componentKey += 1;
    }
  }
};
</script>

<style scoped>
.main-container {
  display: flex;
  height: 100vh;
}

.video-player {
  flex: 7; /* VideoPlayer가 7 비율 차지 */
}

.chat-view {
  flex: 3; /* ChatView가 3 비율 차지 */
}
</style>
