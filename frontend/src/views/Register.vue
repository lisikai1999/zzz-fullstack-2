<template>
  <div class="max-w-md mx-auto px-4 py-16">
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6 text-center">注册</h1>

      <div v-if="error" class="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">
        {{ error }}
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="6"
            class="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
          <input
            v-model="form.password_confirm"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition disabled:opacity-50"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-6">
        已有账号?
        <router-link to="/login" class="text-primary-600 hover:underline">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const form = ref({ username: '', email: '', password: '', password_confirm: '' })

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(form.value.username, form.value.email, form.value.password, form.value.password_confirm)
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    if (data) {
      error.value = Object.values(data).flat().join('; ')
    } else {
      error.value = '注册失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>
