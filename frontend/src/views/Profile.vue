<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
    </div>

    <template v-else-if="profileData">
      <!-- User Info Card -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 md:p-8 mb-6">
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-3xl font-bold text-primary-600">
            {{ profileData.user.username.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ profileData.user.username }}</h1>
            <p v-if="profileData.user.profile?.bio" class="text-gray-500 dark:text-gray-400 mt-1">{{ profileData.user.profile.bio }}</p>
            <p v-if="profileData.user.profile?.website" class="text-sm text-primary-600 mt-1">
              <a :href="profileData.user.profile.website" target="_blank">{{ profileData.user.profile.website }}</a>
            </p>
          </div>
        </div>
      </div>

      <!-- XP / Level Card -->
      <div v-if="profileData.xp_profile" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">阅读等级</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-primary-600">Lv.{{ profileData.xp_profile.level }}</div>
            <div class="text-xs text-gray-400">等级</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-primary-600">{{ profileData.xp_profile.total_xp }}</div>
            <div class="text-xs text-gray-400">总经验值</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-orange-500">{{ profileData.xp_profile.current_streak }}</div>
            <div class="text-xs text-gray-400">当前连续天数</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-orange-500">{{ profileData.xp_profile.longest_streak }}</div>
            <div class="text-xs text-gray-400">最长连续天数</div>
          </div>
        </div>
        <!-- Progress bar -->
        <div class="mt-4">
          <div class="flex justify-between text-xs text-gray-400 mb-1">
            <span>Lv.{{ profileData.xp_profile.level }}</span>
            <span>Lv.{{ profileData.xp_profile.level + 1 }}</span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div class="bg-primary-500 h-3 rounded-full transition-all" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <p class="text-xs text-gray-400 mt-1 text-right">还需 {{ profileData.xp_profile.xp_to_next_level }} XP 升级</p>
        </div>
      </div>

      <!-- Achievements -->
      <div v-if="profileData.achievements.length" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">成就</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div
            v-for="ach in allAchievements"
            :key="ach.type"
            :class="['rounded-lg p-4 text-center border', isEarned(ach.type) ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-700' : 'bg-gray-50 dark:bg-gray-700 border-gray-100 dark:border-gray-600 opacity-50']"
          >
            <div class="text-2xl mb-1">{{ ach.icon }}</div>
            <div class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ ach.name }}</div>
          </div>
        </div>
      </div>

      <!-- Published Articles -->
      <div v-if="profileData.articles.length" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">发布的文章</h2>
        <div class="space-y-3">
          <router-link
            v-for="article in profileData.articles"
            :key="article.id"
            :to="`/article/${article.slug}`"
            class="block py-3 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:text-primary-600 transition"
          >
            <div class="flex justify-between items-center">
              <span class="text-gray-800 dark:text-gray-200 font-medium">{{ article.title }}</span>
              <span class="text-xs text-gray-400">{{ formatDate(article.created_at) }}</span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Reading History (own profile only) -->
      <div v-if="isOwnProfile && readingHistory.length" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">阅读记录</h2>
        <div class="space-y-3">
          <router-link
            v-for="log in readingHistory"
            :key="log.id"
            :to="`/article/${log.article_slug}`"
            class="block py-2 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:text-primary-600 transition"
          >
            <div class="flex justify-between items-center">
              <span class="text-gray-800 dark:text-gray-200">{{ log.article_title }}</span>
              <span class="text-xs text-gray-400">+{{ log.xp_earned }} XP</span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Reading Statistics (own profile, author only) -->
      <div v-if="isOwnProfile && readingStatsData" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 mt-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">文章阅读统计</h2>

        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="text-2xl font-bold text-primary-600">{{ readingStatsData.total_views }}</div>
            <div class="text-xs text-gray-400">总阅读量</div>
          </div>
          <div class="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="text-2xl font-bold text-primary-600">{{ readingStatsData.total_articles }}</div>
            <div class="text-xs text-gray-400">文章总数</div>
          </div>
        </div>

        <!-- Daily Views Chart -->
        <div v-if="readingStatsData.daily_views.length" class="mb-6">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">近30天每日阅读趋势</h3>
          <div class="flex items-end gap-1 h-24">
            <div
              v-for="day in readingStatsData.daily_views.slice().reverse()"
              :key="day.date"
              :title="`${day.date}: ${day.count} 次阅读`"
              class="flex-1 bg-primary-400 dark:bg-primary-500 rounded-t min-h-[4px] hover:bg-primary-600 transition cursor-pointer"
              :style="{ height: getBarHeight(day.count) + '%' }"
            ></div>
          </div>
          <div class="flex justify-between text-xs text-gray-400 mt-1">
            <span>{{ readingStatsData.daily_views[readingStatsData.daily_views.length - 1]?.date }}</span>
            <span>{{ readingStatsData.daily_views[0]?.date }}</span>
          </div>
        </div>

        <!-- Per-article Stats -->
        <div v-if="readingStatsData.articles.length">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">各文章阅读量</h3>
          <div class="space-y-2">
            <div
              v-for="art in readingStatsData.articles"
              :key="art.id"
              class="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700 last:border-0"
            >
              <router-link :to="`/article/${art.slug}`" class="text-gray-800 dark:text-gray-200 hover:text-primary-600 transition truncate flex-1 mr-4">
                {{ art.title }}
              </router-link>
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-primary-600">{{ art.views_count }}</span>
                <button
                  @click="showArticleDetail(art.id)"
                  class="text-xs text-gray-400 hover:text-primary-600 transition underline"
                >详情</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Article Detail Stats Modal -->
        <div v-if="articleDetailStats" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="articleDetailStats = null">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-lg mx-4 max-h-[80vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ articleDetailStats.article_title }}</h3>
              <button @click="articleDetailStats = null" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
            </div>
            <p class="text-sm text-gray-500 mb-4">总阅读量: <span class="font-bold text-primary-600">{{ articleDetailStats.views_count }}</span></p>

            <div v-if="articleDetailStats.daily_views.length" class="mb-4">
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">每日趋势</h4>
              <div class="flex items-end gap-1 h-16">
                <div
                  v-for="day in articleDetailStats.daily_views.slice().reverse()"
                  :key="day.date"
                  :title="`${day.date}: ${day.count} 次`"
                  class="flex-1 bg-primary-400 rounded-t min-h-[2px]"
                  :style="{ height: getDetailBarHeight(day.count) + '%' }"
                ></div>
              </div>
            </div>

            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">最近访问记录</h4>
            <div class="space-y-2 text-xs">
              <div
                v-for="visit in articleDetailStats.recent_visits"
                :key="visit.id"
                class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div class="flex justify-between mb-1">
                  <span class="font-mono text-gray-600 dark:text-gray-400">{{ visit.ip_address }}</span>
                  <span class="text-gray-400">{{ formatDateTime(visit.created_at) }}</span>
                </div>
                <div class="text-gray-400 truncate" :title="visit.user_agent">UA: {{ visit.user_agent?.substring(0, 80) }}{{ visit.user_agent?.length > 80 ? '...' : '' }}</div>
                <div v-if="visit.referer" class="text-gray-400 truncate">来源: {{ visit.referer }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-12 text-gray-400">用户不存在</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const route = useRoute()
const auth = useAuthStore()
const loading = ref(true)
const profileData = ref(null)
const readingHistory = ref([])
const readingStatsData = ref(null)
const articleDetailStats = ref(null)

const allAchievements = [
  { type: 'streak_7', name: '连续阅读7天', icon: '🔥' },
  { type: 'streak_30', name: '连续阅读30天', icon: '💪' },
  { type: 'streak_100', name: '连续阅读100天', icon: '🏆' },
  { type: 'articles_10', name: '阅读10篇', icon: '📖' },
  { type: 'articles_50', name: '阅读50篇', icon: '📚' },
  { type: 'articles_100', name: '阅读100篇', icon: '🎓' },
  { type: 'level_5', name: '达到5级', icon: '⭐' },
  { type: 'level_10', name: '达到10级', icon: '👑' },
]

const isOwnProfile = computed(() => {
  if (!auth.isAuthenticated) return false
  const username = route.params.username
  return !username || username === auth.user?.username
})

const progressPercent = computed(() => {
  if (!profileData.value?.xp_profile) return 0
  const xp = profileData.value.xp_profile
  const currentLevelXP = xp.xp_for_current_level
  const nextLevelXP = xp.xp_for_next_level
  const range = nextLevelXP - currentLevelXP
  const progress = xp.total_xp - currentLevelXP
  return Math.min(100, Math.round((progress / range) * 100))
})

function isEarned(type) {
  return profileData.value?.achievements?.some(a => a.achievement_type === type)
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function formatDateTime(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getBarHeight(count) {
  if (!readingStatsData.value?.daily_views.length) return 0
  const max = Math.max(...readingStatsData.value.daily_views.map(d => d.count))
  return max > 0 ? Math.max(5, (count / max) * 100) : 5
}

function getDetailBarHeight(count) {
  if (!articleDetailStats.value?.daily_views.length) return 0
  const max = Math.max(...articleDetailStats.value.daily_views.map(d => d.count))
  return max > 0 ? Math.max(5, (count / max) * 100) : 5
}

async function showArticleDetail(articleId) {
  try {
    const { data } = await api.get(`/reading-stats/${articleId}/`)
    articleDetailStats.value = data
  } catch (e) {
    articleDetailStats.value = null
  }
}

async function fetchProfile() {
  loading.value = true
  try {
    const username = route.params.username || auth.user?.username
    if (!username) { loading.value = false; return }
    const { data } = await api.get(`/auth/profile/${username}/`)
    profileData.value = data

    if (isOwnProfile.value) {
      try {
        const histRes = await api.get('/gamification/history/')
        readingHistory.value = (histRes.data.results || histRes.data).slice(0, 20)
      } catch (e) {}

      try {
        const statsRes = await api.get('/reading-stats/')
        readingStatsData.value = statsRes.data
      } catch (e) {}
    }
  } catch (e) {
    profileData.value = null
  } finally {
    loading.value = false
  }
}

onMounted(fetchProfile)
watch(() => route.params.username, fetchProfile)
</script>
