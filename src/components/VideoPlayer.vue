<template>
  <div class="video-container">
    <div class="search-bar">
      <v-text-field
        v-model="hashtag"
        label="해시태그 입력"
        prepend-icon="mdi-pound"
        @keyup.enter="searchVideos"
        outlined
        dense
      ></v-text-field>
      <v-btn color="primary" @click="searchVideos" height="40">
        검색
      </v-btn>
    </div>

    <div v-if="videos.length" class="video-content">
      <div :class="['video-list', { 'full-width': !selectedVideo }]">
        <v-list dense>
          <v-list-item
            v-for="video in videos"
            :key="video.id.videoId"
            @click="selectVideo(video.id.videoId)"
            :class="{ 'selected-video': selectedVideo && selectedVideo.id === video.id.videoId }"
          >
            <v-list-item-avatar>
              <v-img :src="video.snippet.thumbnails.default.url"></v-img>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title class="text-truncate">{{ video.snippet.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </div>
      <div v-if="selectedVideo" class="video-player">
        <v-card class="video-card">
          <v-card-title class="text-h6">{{ selectedVideo.snippet.title }}</v-card-title>
          <v-card-text class="video-wrapper">
            <iframe
              v-if="selectedVideo"
              :src="`https://www.youtube.com/embed/${selectedVideo.id}?enablejsapi=1`"
              frameborder="0"
              allow="autoplay; encrypted-media"
              allowfullscreen
              id="youtube-player"
            ></iframe>
          </v-card-text>
        </v-card>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { io } from 'socket.io-client';

export default {
  data() {
    return {
      hashtag: '',
      videos: [],
      selectedVideo: null,
      socket: null,
      isVideoSyncing: false,
      player: null,
    };
  },
  mounted() {
    this.initializeComponent();
  },
  methods: {
    async searchVideos() {
      if (!this.hashtag) return;
      try {
        const response = await axios.get('/api/search', {
          params: { q: this.hashtag },
        });
        this.videos = response.data;
        this.selectedVideo = null;
      } catch (error) {
        console.error('비디오 검색 중 오류 발생:', error);
      }
    },
    async selectVideo(videoId) {
      try {
        const response = await axios.get(`/api/videos/${videoId}`);
        this.selectedVideo = response.data;
        this.socket.emit('video selected', this.selectedVideo);
        if (this.player) {
          this.player.loadVideoById(videoId);
        } else {
          this.initializeYouTubePlayer(videoId);
        }
      } catch (error) {
        console.error('비디오 상세 정보 가져오기 중 오류 발생:', error);
      }
    },
    initializeYouTubePlayer(videoId) {
      if (typeof YT !== 'undefined' && YT.Player) {
        this.player = new YT.Player('youtube-player', {
          events: {
            onReady: this.onPlayerReady,
            onStateChange: this.onPlayerStateChange,
          },
        });
      } else {
        setTimeout(() => this.initializeYouTubePlayer(videoId), 100);
      }
    },
    onPlayerReady(event) {
      console.log('YouTube 플레이어가 준비되었습니다.');
      this.socket.emit('request current state');
    },
    onPlayerStateChange(event) {
      if (!this.isVideoSyncing) {
        if (event.data === YT.PlayerState.PLAYING) {
          this.socket.emit('play');
          this.socket.emit('video time update', this.player.getCurrentTime());
        } else if (event.data === YT.PlayerState.PAUSED) {
          this.socket.emit('pause');
        }
      }
    },
    updateVideoTime() {
      if (this.player && !this.isVideoSyncing) {
        this.socket.emit('video time update', this.player.getCurrentTime());
      }
    },
    initializeComponent() {
      this.hashtag = '';
      this.videos = [];
      this.selectedVideo = null;
      this.isVideoSyncing = false;
      if (this.player) {
        this.player.destroy();
        this.player = null;
      }

      this.socket = io('http://localhost:3000', {
        transports: ['websocket'],
        cors: {
          origin: 'http://localhost:5173',
          methods: ["GET", "POST"]
        }
      });

      this.socket.on('connect', () => {
        this.socket.emit('join room', 'default_room');
      });

      this.socket.on('video selected', (videoData) => {
        this.selectedVideo = videoData;
        this.$nextTick(() => {
          if (this.player) {
            this.player.loadVideoById(videoData.id);
          } else {
            this.initializeYouTubePlayer(videoData.id);
          }
        });
      });

      this.socket.on('video time update', (time) => {
        if (this.player && !this.isVideoSyncing) {
          this.isVideoSyncing = true;
          this.player.seekTo(time, true);
          setTimeout(() => {
            this.isVideoSyncing = false;
          }, 1000);
        }
      });

      this.socket.on('current state', (state) => {
        if (state.video) {
          this.selectedVideo = state.video;
          this.videos = [state.video];
          this.$nextTick(() => {
            this.initializeYouTubePlayer(state.video.id);
            if (state.time) {
              this.player.seekTo(state.time, true);
            }
          });
        }
      });

      this.socket.on('play', () => {
        if (this.player) {
          this.player.playVideo();
        }
      });

      this.socket.on('pause', () => {
        if (this.player) {
          this.player.pauseVideo();
        }
      });
    },
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect();
    }
    if (this.player) {
      this.player.destroy();
    }
  },
};
</script>

<style scoped>
.video-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.search-bar {
  display: flex;
  padding: 10px;
}

.search-bar .v-text-field {
  flex-grow: 1;
  margin-right: 10px;
}

.video-content {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}

.video-list {
  width: 30%;
  overflow-y: auto;
}

.video-list.full-width {
  width: 100%;
}

.video-player {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.video-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.video-wrapper {
  flex-grow: 1;
  position: relative;
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.selected-video {
  background-color: rgba(0, 0, 0, 0.1);
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
