<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
    </div>

    <article v-else-if="article" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-6 md:p-10">
        <div class="flex items-center gap-2 mb-4">
          <router-link
            v-for="tag in article.tags"
            :key="tag.id"
            :to="`/tag/${tag.slug}`"
            class="text-xs bg-primary-50 text-primary-600 px-2 py-1 rounded-full hover:bg-primary-100 transition"
          >
            {{ tag.name }}
          </router-link>
        </div>

        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">{{ article.title }}</h1>

        <div class="flex items-center text-sm text-gray-400 space-x-4 mb-8 pb-6 border-b border-gray-100">
          <span>{{ article.author_name }}</span>
          <span>{{ formatDate(article.published_at || article.created_at) }}</span>
          <span>{{ article.views_count }} 阅读</span>
        </div>

        <div
          class="prose prose-lg max-w-none prose-headings:text-gray-900 prose-a:text-primary-600"
          v-html="renderedContent"
        ></div>

        <div v-if="auth.isAuthenticated && auth.user?.id === article.author" class="mt-8 pt-6 border-t border-gray-100">
          <router-link
            :to="`/editor/${article.slug}`"
            class="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
          >
            编辑文章
          </router-link>
        </div>
      </div>
    </article>

    <section v-if="article" class="mt-8 bg-white rounded-xl shadow-sm border border-gray-100 p-6 md:p-10">
      <h3 class="text-xl font-semibold text-gray-900 mb-6">
        评论 ({{ comments.length }})
      </h3>

      <form @submit.prevent="submitComment" class="mb-8">
        <div v-if="!auth.isAuthenticated" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            v-model="commentForm.nickname"
            type="text"
            placeholder="昵称"
            required
            class="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
          <input
            v-model="commentForm.email"
            type="email"
            placeholder="邮箱 (选填)"
            class="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <textarea
          v-model="commentForm.content"
          placeholder="写下你的评论..."
          required
          rows="4"
          class="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none mb-4"
        ></textarea>
        <button
          type="submit"
          :disabled="submitting"
          class="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition disabled:opacity-50"
        >
          {{ submitting ? '提交中...' : '发表评论' }}
        </button>
      </form>

      <div class="space-y-6">
        <div v-for="comment in comments" :key="comment.id" class="border-b border-gray-50 pb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium text-gray-700">{{ comment.author_name }}</span>
            <span class="text-xs text-gray-400">{{ formatDate(comment.created_at) }}</span>
          </div>
          <p class="text-gray-600">{{ comment.content }}</p>
          <div v-if="comment.replies?.length" class="ml-6 mt-4 space-y-4">
            <div v-for="reply in comment.replies" :key="reply.id" class="border-l-2 border-primary-100 pl-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-medium text-sm text-gray-700">{{ reply.author_name }}</span>
                <span class="text-xs text-gray-400">{{ formatDate(reply.created_at) }}</span>
              </div>
              <p class="text-sm text-gray-600">{{ reply.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import { useAuthStore } from '../stores/auth'
import api from '../api'

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

const route = useRoute()
const auth = useAuthStore()
const article = ref(null)
const comments = ref([])
const loading = ref(true)
const submitting = ref(false)
const commentForm = ref({ nickname: '', email: '', content: '' })

const renderedContent = computed(() => {
  if (!article.value) return ''
  if (article.value.content_html) return DOMPurify.sanitize(article.value.content_html)
  return DOMPurify.sanitize(marked(article.value.content))
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function submitComment() {
  submitting.value = true
  try {
    await api.post('/comments/', {
      article: article.value.id,
      content: commentForm.value.content,
      nickname: commentForm.value.nickname,
      email: commentForm.value.email,
    })
    commentForm.value.content = ''
    const { data } = await api.get('/comments/', { params: { article: article.value.id } })
    comments.value = (data.results || data).filter(c => !c.parent)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/articles/${route.params.slug}/`)
    article.value = data
    api.post(`/articles/${route.params.slug}/record_view/`)
    const commentsRes = await api.get('/comments/', { params: { article: data.id } })
    comments.value = (commentsRes.data.results || commentsRes.data).filter(c => !c.parent)
  } finally {
    loading.value = false
  }
})
</script>
