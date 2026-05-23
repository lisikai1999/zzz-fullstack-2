<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">草稿箱</h1>
      <p class="text-gray-500">管理你的未发布文章</p>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
    </div>

    <div v-else-if="drafts.length === 0" class="text-center py-12">
      <p class="text-gray-400 mb-4">暂无草稿</p>
      <router-link to="/editor" class="text-primary-600 hover:underline">开始写作</router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="draft in drafts"
        :key="draft.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center justify-between"
      >
        <div class="flex-1">
          <h3 class="text-lg font-medium text-gray-900">{{ draft.title }}</h3>
          <p class="text-sm text-gray-400 mt-1">最后编辑于 {{ formatDate(draft.updated_at) }}</p>
        </div>
        <div class="flex gap-3">
          <router-link
            :to="`/editor/${draft.slug}`"
            class="px-4 py-2 text-sm bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition"
          >
            编辑
          </router-link>
          <button
            @click="deleteDraft(draft)"
            class="px-4 py-2 text-sm text-red-500 hover:bg-red-50 rounded-lg transition"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const drafts = ref([])
const loading = ref(true)

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function fetchDrafts() {
  loading.value = true
  const { data } = await api.get('/articles/', { params: { status: 'draft', mine: '1' } })
  drafts.value = data.results || data
  loading.value = false
}

async function deleteDraft(draft) {
  if (!confirm('确定要删除这篇草稿吗?')) return
  await api.delete(`/articles/${draft.slug}/`)
  drafts.value = drafts.value.filter(d => d.id !== draft.id)
}

onMounted(fetchDrafts)
</script>
