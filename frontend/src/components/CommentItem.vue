<template>
  <div :class="['pb-4', depth > 0 ? 'ml-4 md:ml-6 pl-4 border-l-2 border-primary-100 dark:border-primary-800' : 'border-b border-gray-50 dark:border-gray-700']">
    <div class="flex items-center justify-between mb-2">
      <span class="font-medium text-gray-700 dark:text-gray-300 text-sm">{{ comment.author_name }}</span>
      <span class="text-xs text-gray-400">{{ formatDate(comment.created_at) }}</span>
    </div>
    <p class="text-gray-600 dark:text-gray-400 text-sm mb-2">{{ comment.content }}</p>
    <button
      @click="showReplyForm = !showReplyForm"
      class="text-xs text-primary-500 hover:text-primary-700 transition"
    >
      {{ showReplyForm ? '取消回复' : '回复' }}
    </button>

    <!-- Inline reply form -->
    <div v-if="showReplyForm" class="mt-3">
      <div v-if="!isAuthenticated" class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
        <input
          v-model="replyForm.nickname"
          type="text"
          placeholder="昵称"
          required
          class="px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
        />
        <input
          v-model="replyForm.email"
          type="email"
          placeholder="邮箱 (选填)"
          class="px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
        />
      </div>
      <textarea
        v-model="replyForm.content"
        :placeholder="`回复 ${comment.author_name}...`"
        required
        rows="3"
        class="w-full px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none mb-3"
      ></textarea>
      <button
        @click="submitReply"
        :disabled="submitting || !replyForm.content"
        class="px-4 py-1.5 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition disabled:opacity-50"
      >
        {{ submitting ? '提交中...' : '发表回复' }}
      </button>
    </div>

    <!-- Nested replies (recursive) -->
    <div v-if="comment.replies?.length" class="mt-4 space-y-4">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :depth="depth + 1"
        :is-authenticated="isAuthenticated"
        :submitting="submitting"
        @reply="(parentId, data) => $emit('reply', parentId, data)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  comment: { type: Object, required: true },
  depth: { type: Number, default: 0 },
  isAuthenticated: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['reply'])

const showReplyForm = ref(false)
const replyForm = ref({ nickname: '', email: '', content: '' })

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function submitReply() {
  if (!replyForm.value.content) return
  emit('reply', props.comment.id, { ...replyForm.value })
  replyForm.value.content = ''
  showReplyForm.value = false
}
</script>
