<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        标签: {{ tagName }}
      </h1>
      <router-link to="/" class="text-sm text-primary-600 hover:underline">&larr; 返回首页</router-link>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
    </div>

    <div v-else-if="articles.length === 0" class="text-center py-12 text-gray-400">
      该标签下暂无文章
    </div>

    <div v-else class="space-y-6">
      <article
        v-for="article in articles"
        :key="article.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition"
      >
        <router-link :to="`/article/${article.slug}`" class="block">
          <h2 class="text-xl font-semibold text-gray-900 hover:text-primary-600 transition mb-2">
            {{ article.title }}
          </h2>
          <p class="text-gray-500 text-sm line-clamp-2 mb-3">{{ article.excerpt }}</p>
          <div class="flex items-center text-xs text-gray-400 space-x-4">
            <span>{{ article.author_name }}</span>
            <span>{{ formatDate(article.created_at) }}</span>
            <span>{{ article.views_count }} 阅读</span>
          </div>
        </router-link>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const articles = ref([])
const loading = ref(true)
const tagName = ref('')

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function fetchArticles() {
  loading.value = true
  tagName.value = route.params.slug
  const { data } = await api.get('/articles/', { params: { tag: route.params.slug } })
  articles.value = data.results || data
  loading.value = false
}

onMounted(fetchArticles)
watch(() => route.params.slug, fetchArticles)
</script>
