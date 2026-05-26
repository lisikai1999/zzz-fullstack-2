<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
    </div>

    <article v-else-if="article" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div class="p-6 md:p-10">
        <div class="flex items-center gap-2 mb-4">
          <router-link
            v-for="tag in article.tags"
            :key="tag.id"
            :to="`/tag/${tag.slug}`"
            class="text-xs bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 px-2 py-1 rounded-full hover:bg-primary-100 dark:hover:bg-primary-900/50 transition"
          >
            {{ tag.name }}
          </router-link>
        </div>

        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">{{ article.title }}</h1>

        <div class="flex items-center text-sm text-gray-400 space-x-4 mb-8 pb-6 border-b border-gray-100 dark:border-gray-700">
          <span>{{ article.author_name }}</span>
          <span>{{ formatDate(article.published_at || article.created_at) }}</span>
          <span>{{ article.views_count }} 阅读</span>
        </div>

        <div
          class="prose prose-lg dark:prose-invert max-w-none prose-headings:text-gray-900 dark:prose-headings:text-white prose-a:text-primary-600"
          v-html="renderedContent"
        ></div>

        <!-- XP notification -->
        <div v-if="xpNotification" class="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <p class="text-green-700 dark:text-green-400 font-medium">
            {{ xpNotification.already_read ? '你已阅读过这篇文章' : `+${xpNotification.xp_earned} XP 获得经验值！` }}
          </p>
          <div v-if="xpNotification.new_achievements?.length" class="mt-2">
            <span v-for="ach in xpNotification.new_achievements" :key="ach.id" class="text-sm text-yellow-600 dark:text-yellow-400 mr-2">
              🏆 {{ ach.display_name }}
            </span>
          </div>
        </div>

        <div v-if="auth.isAuthenticated && auth.user?.id === article.author" class="mt-8 pt-6 border-t border-gray-100 dark:border-gray-700 flex items-center gap-3">
          <router-link
            :to="`/editor/${article.slug}`"
            class="inline-flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
          >
            编辑文章
          </router-link>
          <button
            @click="showShareModal = true"
            class="inline-flex items-center px-4 py-2 bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/50 transition"
          >
            分享协作
          </button>
        </div>
      </div>
    </article>

    <!-- Share Modal -->
    <div v-if="showShareModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showShareModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">分享文章给其他用户</h3>
        <input
          v-model="shareUsername"
          type="text"
          placeholder="输入用户名"
          class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white outline-none mb-3"
        />
        <select v-model="sharePermission" class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white outline-none mb-4">
          <option value="edit">可编辑</option>
          <option value="view">仅查看</option>
        </select>
        <p v-if="shareError" class="text-red-500 text-sm mb-3">{{ shareError }}</p>
        <p v-if="shareSuccess" class="text-green-500 text-sm mb-3">{{ shareSuccess }}</p>
        <div class="flex justify-end gap-3">
          <button @click="showShareModal = false" class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">取消</button>
          <button @click="shareArticle" class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">分享</button>
        </div>
      </div>
    </div>

    <section v-if="article" class="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 md:p-10">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">
        评论 ({{ comments.length }})
      </h3>

      <form @submit.prevent="submitComment" class="mb-8">
        <div v-if="!auth.isAuthenticated" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            v-model="commentForm.nickname"
            type="text"
            placeholder="昵称"
            required
            class="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
          <input
            v-model="commentForm.email"
            type="email"
            placeholder="邮箱 (选填)"
            class="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <textarea
          v-model="commentForm.content"
          placeholder="写下你的评论..."
          required
          rows="4"
          class="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none mb-4"
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
        <div v-for="comment in comments" :key="comment.id" class="border-b border-gray-50 dark:border-gray-700 pb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium text-gray-700 dark:text-gray-300">{{ comment.author_name }}</span>
            <span class="text-xs text-gray-400">{{ formatDate(comment.created_at) }}</span>
          </div>
          <p class="text-gray-600 dark:text-gray-400">{{ comment.content }}</p>
          <div v-if="comment.replies?.length" class="ml-6 mt-4 space-y-4">
            <div v-for="reply in comment.replies" :key="reply.id" class="border-l-2 border-primary-100 dark:border-primary-800 pl-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-medium text-sm text-gray-700 dark:text-gray-300">{{ reply.author_name }}</span>
                <span class="text-xs text-gray-400">{{ formatDate(reply.created_at) }}</span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ reply.content }}</p>
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
const xpNotification = ref(null)
const showShareModal = ref(false)
const shareUsername = ref('')
const sharePermission = ref('edit')
const shareError = ref('')
const shareSuccess = ref('')

const renderedContent = computed(() => {
  if (!article.value) return ''
  if (article.value.content_html) return DOMPurify.sanitize(article.value.content_html)
  return DOMPurify.sanitize(marked(article.value.content))
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function shareArticle() {
  shareError.value = ''
  shareSuccess.value = ''
  try {
    await api.post('/collaborations/', {
      article: article.value.id,
      username: shareUsername.value,
      permission: sharePermission.value,
    })
    shareSuccess.value = '已发送协作邀请'
    shareUsername.value = ''
  } catch (e) {
    shareError.value = e.response?.data?.error || '分享失败'
  }
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

    if (auth.isAuthenticated) {
      try {
        const xpRes = await api.post(`/gamification/read/${data.id}/`)
        xpNotification.value = xpRes.data
      } catch (e) {}
    }
  } finally {
    loading.value = false
  }
})
</script>
