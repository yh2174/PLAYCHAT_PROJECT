<template>
  <div class="chat-container">
    <div class="user-info">
      <v-chip small>
        <v-avatar left size="small">
          <v-icon small>mdi-account</v-icon>
        </v-avatar>
        {{ username }}
      </v-chip>
      <h2>PlayChat</h2>
      <v-btn x-small color="error" @click="logout">로그아웃</v-btn>
    </div>
    <v-list ref="messageList" class="message-list">
      <v-list-item-group>
        <v-list-item v-for="(message, index) in messages" :key="index">
          <v-list-item-content>{{ message }}</v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
    <div class="scroll-button-container">
      <v-btn id="Scroll" @click="scrollToBottom" icon x-small>
        <v-icon small>mdi-chevron-down</v-icon>
      </v-btn>
    </div>
    <div class="input-container">
      <v-text-field
        v-model="newMessage"
        label="메시지 입력"
        @keyup.enter="sendMessage"
        dense
      />
      <v-btn small @click="sendMessage">전송</v-btn>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { io } from 'socket.io-client';

export default {
  name: 'ChatView',
  data() {
    return {
      newMessage: '',
      messages: [],
      socket: null,
      username: '',
    };
  },
  created() {
    this.username = sessionStorage.getItem('username');
    if (!this.username) {
      this.$router.push('/login');
    }
  },
  mounted() {
    this.socket = io();
    this.socket.on('chat message', (msg) => {
      this.messages.push(msg);
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    });
    this.socket.on('chat history', (messages) => {
      this.messages = messages;
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    });
    this.socket.on('connect_error', (err) => {
      console.error('소켓 연결 오류:', err);
    });
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim()) {
        const message = `${this.username}: ${this.newMessage}`;
        this.socket.emit('chat message', message);
        this.newMessage = '';
      }
    },
    scrollToBottom() {
      console.log("아래로");
      this.$nextTick(() => {
        const messageList = this.$refs.messageList.$el;
        messageList.scrollTop = messageList.scrollHeight;
      });
    },
    async logout() {
      try {
        await axios.post('/api/logout', {}, { withCredentials: true });
        sessionStorage.removeItem('username');
        if (this.socket) {
          this.socket.disconnect();
        }
        this.$router.push('/login');
      } catch (error) {
        console.error('로그아웃 중 오류 발생:', error);
        alert('로그아웃 중 오류가 발생했습니다.');
      }
    }
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px;
  position: relative;
}

.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.scroll-button-container {
  position: absolute;
  bottom: 60px; /* 입력란 높이에 따라 조정 */
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
}

#Scroll {
  border-radius: 50%;
  width: 32px;
  height: 32px;
  min-width: 0;
  padding: 0;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 60px; /* 스크롤 버튼과 입력란을 위한 여백 */
}

.input-container {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.input-container .v-text-field {
  margin-right: 8px;
}
</style>