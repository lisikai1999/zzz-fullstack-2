<template>
  <div class="min-h-screen flex flex-col">
    <nav class="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div class="max-w-5xl mx-auto px-4 sm:px-6">
        <div class="flex justify-between items-center h-16">
          <router-link to="/" class="text-xl font-bold text-primary-600">
            CreatorBlog
          </router-link>

          <div class="hidden md:flex items-center space-x-6">
            <router-link to="/" class="text-gray-600 hover:text-primary-600 transition">首页</router-link>
            <router-link v-if="auth.isAuthenticated" to="/editor" class="text-gray-600 hover:text-primary-600 transition">写文章</router-link>
            <router-link v-if="auth.isAuthenticated" to="/drafts" class="text-gray-600 hover:text-primary-600 transition">草稿箱</router-link>
          </div>

          <div class="flex items-center space-x-4">
            <template v-if="auth.isAuthenticated">
              <span class="text-sm text-gray-500">{{ auth.user?.username }}</span>
              <button @click="auth.logout()" class="text-sm text-gray-500 hover:text-red-500 transition">退出</button>
            </template>
            <template v-else>
              <router-link to="/login" class="text-sm text-gray-600 hover:text-primary-600">登录</router-link>
              <router-link to="/register" class="bg-primary-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-600 transition">注册</router-link>
            </template>
          </div>

          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        </div>

        <div v-if="mobileMenuOpen" class="md:hidden pb-4 space-y-2">
          <router-link to="/" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">首页</router-link>
          <router-link v-if="auth.isAuthenticated" to="/editor" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">写文章</router-link>
          <router-link v-if="auth.isAuthenticated" to="/drafts" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">草稿箱</router-link>
        </div>
      </div>
    </nav>

    <main class="flex-1">
      <router-view />
    </main>

    <footer class="bg-white border-t border-gray-100 py-8 mt-12">
      <div class="max-w-5xl mx-auto px-4 text-center text-sm text-gray-400">
        <p>&copy; 2024 CreatorBlog. Powered by Django & Vue 3.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const mobileMenuOpen = ref(false)
</script>
