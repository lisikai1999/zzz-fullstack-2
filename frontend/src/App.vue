<template>
  <div class="min-h-screen flex flex-col">
    <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-100 dark:border-gray-700 sticky top-0 z-50">
      <div class="max-w-5xl mx-auto px-4 sm:px-6">
        <div class="flex justify-between items-center h-16">
          <router-link to="/" class="text-xl font-bold text-primary-600">
            CreatorBlog
          </router-link>

          <div class="hidden md:flex items-center space-x-6">
            <router-link to="/" class="text-gray-600 dark:text-gray-300 hover:text-primary-600 transition">首页</router-link>
            <router-link to="/leaderboard" class="text-gray-600 dark:text-gray-300 hover:text-primary-600 transition">排行榜</router-link>
            <router-link v-if="auth.isAuthenticated" to="/editor" class="text-gray-600 dark:text-gray-300 hover:text-primary-600 transition">写文章</router-link>
            <router-link v-if="auth.isAuthenticated" to="/drafts" class="text-gray-600 dark:text-gray-300 hover:text-primary-600 transition">草稿箱</router-link>
            <router-link v-if="auth.isAuthenticated" to="/shared" class="text-gray-600 dark:text-gray-300 hover:text-primary-600 transition">协作</router-link>
          </div>

          <div class="flex items-center space-x-4">
            <button @click="theme.toggle()" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition" title="切换主题">
              <svg v-if="theme.isDark" class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/>
              </svg>
              <svg v-else class="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
              </svg>
            </button>

            <template v-if="auth.isAuthenticated">
              <router-link :to="`/profile/${auth.user?.username}`" class="text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 transition">
                {{ auth.user?.username }}
              </router-link>
              <button @click="auth.logout()" class="text-sm text-gray-500 dark:text-gray-400 hover:text-red-500 transition">退出</button>
            </template>
            <template v-else>
              <router-link to="/login" class="text-sm text-gray-600 dark:text-gray-300 hover:text-primary-600">登录</router-link>
              <router-link to="/register" class="bg-primary-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-600 transition">注册</router-link>
            </template>
          </div>

          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2">
            <svg class="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        </div>

        <div v-if="mobileMenuOpen" class="md:hidden pb-4 space-y-2">
          <router-link to="/" class="block py-2 text-gray-600 dark:text-gray-300" @click="mobileMenuOpen = false">首页</router-link>
          <router-link to="/leaderboard" class="block py-2 text-gray-600 dark:text-gray-300" @click="mobileMenuOpen = false">排行榜</router-link>
          <router-link v-if="auth.isAuthenticated" to="/editor" class="block py-2 text-gray-600 dark:text-gray-300" @click="mobileMenuOpen = false">写文章</router-link>
          <router-link v-if="auth.isAuthenticated" to="/drafts" class="block py-2 text-gray-600 dark:text-gray-300" @click="mobileMenuOpen = false">草稿箱</router-link>
          <router-link v-if="auth.isAuthenticated" to="/shared" class="block py-2 text-gray-600 dark:text-gray-300" @click="mobileMenuOpen = false">协作</router-link>
        </div>
      </div>
    </nav>

    <main class="flex-1">
      <router-view />
    </main>

    <footer class="bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 py-8 mt-12">
      <div class="max-w-5xl mx-auto px-4 text-center text-sm text-gray-400">
        <p>&copy; 2024 CreatorBlog. Powered by Django & Vue 3.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'

const auth = useAuthStore()
const theme = useThemeStore()
const mobileMenuOpen = ref(false)
</script>
