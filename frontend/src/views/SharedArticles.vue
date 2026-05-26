<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">协作文章</h1>
      <p class="text-gray-500 dark:text-gray-400">管理分享给你的文章和待处理的邀请</p>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
    </div>

    <template v-else>
      <!-- Pending Invitations -->
      <div v-if="invitations.length" class="mb-8">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">待处理的邀请</h2>
        <div class="space-y-3">
          <div
            v-for="inv in invitations"
            :key="inv.id"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5 flex items-center justify-between"
          >
            <div>
              <h3 class="font-medium text-gray-900 dark:text-white">{{ inv.article_title }}</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {{ inv.invited_by_name }} 邀请你
                <span class="font-medium">{{ inv.permission === 'edit' ? '编辑' : '查看' }}</span>
              </p>
            </div>
            <div class="flex gap-2">
              <button
                @click="acceptInvitation(inv)"
                class="px-4 py-2 text-sm bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition"
              >
                接受
              </button>
              <button
                @click="rejectInvitation(inv)"
                class="px-4 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
              >
                拒绝
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Shared Articles -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">协作文章</h2>
        <div v-if="sharedArticles.length === 0" class="text-center py-12 text-gray-400">
          暂无协作文章
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="article in sharedArticles"
            :key="article.id"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5 flex items-center justify-between"
          >
            <div class="flex-1">
              <h3 class="font-medium text-gray-900 dark:text-white">{{ article.title }}</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {{ article.author_name }} · {{ formatDate(article.created_at) }}
                <span :class="['ml-2 px-2 py-0.5 rounded text-xs', article.status === 'published' ? 'bg-green-100 dark:bg-green-900/20 text-green-600' : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-600']">
                  {{ article.status === 'published' ? '已发布' : '草稿' }}
                </span>
              </p>
            </div>
            <router-link
              :to="`/editor/${article.slug}`"
              class="px-4 py-2 text-sm bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/50 transition"
            >
              编辑
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const loading = ref(true)
const invitations = ref([])
const sharedArticles = ref([])

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function fetchData() {
  loading.value = true
  try {
    const [invRes, articlesRes] = await Promise.all([
      api.get('/collaborations/invitations/'),
      api.get('/articles/', { params: { shared: '1' } }),
    ])
    invitations.value = invRes.data
    sharedArticles.value = articlesRes.data.results || articlesRes.data
  } finally {
    loading.value = false
  }
}

async function acceptInvitation(inv) {
  await api.post(`/collaborations/${inv.id}/accept/`)
  invitations.value = invitations.value.filter(i => i.id !== inv.id)
  fetchData()
}

async function rejectInvitation(inv) {
  await api.post(`/collaborations/${inv.id}/reject/`)
  invitations.value = invitations.value.filter(i => i.id !== inv.id)
}

onMounted(fetchData)
</script>
