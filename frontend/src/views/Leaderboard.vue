<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">阅读排行榜</h1>
      <p class="text-gray-500 dark:text-gray-400">阅读最多的用户</p>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
    </div>

    <div v-else class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">排名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">用户</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">等级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">经验值</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">连续天数</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr
            v-for="(user, index) in leaderboard"
            :key="user.id"
            :class="['hover:bg-gray-50 dark:hover:bg-gray-700 transition', isCurrentUser(user) ? 'bg-primary-50/50 dark:bg-primary-900/10' : '']"
          >
            <td class="px-6 py-4">
              <span :class="['font-bold', index < 3 ? 'text-xl' : 'text-gray-500 dark:text-gray-400']">
                {{ index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : (index + 1) }}
              </span>
            </td>
            <td class="px-6 py-4">
              <router-link :to="`/profile/${user.username}`" class="flex items-center gap-3 hover:text-primary-600 transition">
                <div class="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-sm font-bold text-primary-600">
                  {{ user.username.charAt(0).toUpperCase() }}
                </div>
                <span class="font-medium text-gray-800 dark:text-gray-200">{{ user.username }}</span>
              </router-link>
            </td>
            <td class="px-6 py-4">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400">
                Lv.{{ user.level }}
              </span>
            </td>
            <td class="px-6 py-4 text-gray-700 dark:text-gray-300 font-medium">{{ user.total_xp }} XP</td>
            <td class="px-6 py-4 text-gray-500 dark:text-gray-400">{{ user.current_streak }} 天</td>
          </tr>
        </tbody>
      </table>

      <div v-if="leaderboard.length === 0" class="text-center py-12 text-gray-400">
        暂无排行数据
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const auth = useAuthStore()
const leaderboard = ref([])
const loading = ref(true)

function isCurrentUser(user) {
  return auth.isAuthenticated && auth.user?.username === user.username
}

onMounted(async () => {
  try {
    const { data } = await api.get('/gamification/leaderboard/')
    leaderboard.value = data.results || data
  } finally {
    loading.value = false
  }
})
</script>
