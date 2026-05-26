<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row gap-8">
      <div class="flex-1">
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">最新文章</h1>
          <p class="text-gray-500 dark:text-gray-400">探索创意与技术的交汇点</p>
        </div>

        <div class="relative mb-6">
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="搜索文章..."
            class="w-full px-4 py-3 pl-10 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          <svg class="absolute left-3 top-3.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>

        <div v-if="loading" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>

        <div v-else-if="articles.length === 0" class="text-center py-12 text-gray-400">
          暂无文章
        </div>

        <div v-else class="space-y-6">
          <article
            v-for="article in articles"
            :key="article.id"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition group"
          >
            <router-link :to="`/article/${article.slug}`" class="block p-6">
              <div class="flex items-center gap-2 mb-3">
                <span
                  v-for="tag in article.tags"
                  :key="tag.id"
                  class="text-xs bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 px-2 py-1 rounded-full"
                >
                  {{ tag.name }}
                </span>
              </div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 transition mb-2">
                {{ article.title }}
              </h2>
              <p class="text-gray-500 dark:text-gray-400 text-sm line-clamp-2 mb-4">{{ article.excerpt }}</p>
              <div class="flex items-center text-xs text-gray-400 space-x-4">
                <span>{{ article.author_name }}</span>
                <span>{{ formatDate(article.created_at) }}</span>
                <span>{{ article.views_count }} 阅读</span>
                <span>{{ article.comment_count }} 评论</span>
              </div>
            </router-link>
          </article>
        </div>

        <div v-if="hasMore" class="text-center mt-8">
          <button
            @click="loadMore"
            class="px-6 py-2 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
          >
            加载更多
          </button>
        </div>
      </div>

      <aside class="w-full md:w-72 space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">站点统计</h3>
          <div class="grid grid-cols-2 gap-3 text-center">
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
              <div class="text-xl font-bold text-primary-600">{{ stats.total_articles }}</div>
              <div class="text-xs text-gray-400">文章</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
              <div class="text-xl font-bold text-primary-600">{{ stats.total_views }}</div>
              <div class="text-xs text-gray-400">阅读</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
              <div class="text-xl font-bold text-primary-600">{{ stats.total_comments }}</div>
              <div class="text-xs text-gray-400">评论</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
              <div class="text-xl font-bold text-primary-600">{{ stats.total_tags }}</div>
              <div class="text-xs text-gray-400">标签</div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">标签</h3>
          <div class="flex flex-wrap gap-2">
            <router-link
              v-for="tag in tags"
              :key="tag.id"
              :to="`/tag/${tag.slug}`"
              class="text-sm bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-3 py-1 rounded-full hover:bg-primary-50 dark:hover:bg-primary-900/30 hover:text-primary-600 dark:hover:text-primary-400 transition"
            >
              {{ tag.name }} ({{ tag.article_count }})
            </router-link>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const articles = ref([])
const tags = ref([])
const stats = ref({ total_articles: 0, total_views: 0, total_comments: 0, total_tags: 0 })
const loading = ref(true)
const searchQuery = ref('')
const page = ref(1)
const hasMore = ref(false)

let searchTimeout = null

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function fetchArticles(reset = true) {
  if (reset) {
    page.value = 1
    loading.value = true
  }
  const params = { page: page.value }
  if (searchQuery.value) params.search = searchQuery.value
  const { data } = await api.get('/articles/', { params })
  if (reset) {
    articles.value = data.results
  } else {
    articles.value.push(...data.results)
  }
  hasMore.value = !!data.next
  loading.value = false
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchArticles(), 300)
}

function loadMore() {
  page.value++
  fetchArticles(false)
}

onMounted(async () => {
  await fetchArticles()
  const [tagsRes, statsRes] = await Promise.all([
    api.get('/tags/'),
    api.get('/stats/'),
  ])
  tags.value = tagsRes.data.results || tagsRes.data
  stats.value = statsRes.data
})
</script>
