<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div class="p-6 md:p-10">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          {{ isEditing ? '编辑文章' : '写新文章' }}
        </h1>

        <div class="space-y-6">
          <div>
            <input
              v-model="form.title"
              type="text"
              placeholder="文章标题"
              class="w-full text-2xl font-bold px-0 py-2 border-0 border-b-2 border-gray-100 dark:border-gray-700 focus:border-primary-500 outline-none bg-transparent text-gray-900 dark:text-white"
            />
          </div>

          <div class="flex items-center gap-4">
            <select v-model="form.status" class="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg outline-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option value="draft">草稿</option>
              <option value="published">发布</option>
            </select>

            <div class="flex-1">
              <input
                v-model="tagInput"
                @keydown.enter.prevent="addTag"
                type="text"
                placeholder="输入标签后回车添加"
                class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg outline-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          <div v-if="selectedTags.length" class="flex flex-wrap gap-2">
            <span
              v-for="tag in selectedTags"
              :key="tag.id"
              class="inline-flex items-center gap-1 text-sm bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 px-3 py-1 rounded-full"
            >
              {{ tag.name }}
              <button @click="removeTag(tag)" class="hover:text-red-500">&times;</button>
            </span>
          </div>

          <div class="flex border-b border-gray-200 dark:border-gray-700 mb-4">
            <button
              @click="editorMode = 'rich'"
              :class="['px-4 py-2 text-sm font-medium transition', editorMode === 'rich' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-gray-500 dark:text-gray-400']"
            >
              富文本
            </button>
            <button
              @click="editorMode = 'markdown'"
              :class="['px-4 py-2 text-sm font-medium transition', editorMode === 'markdown' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-gray-500 dark:text-gray-400']"
            >
              Markdown
            </button>
          </div>

          <div v-if="editorMode === 'rich'" class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <div v-if="editor" class="flex flex-wrap gap-1 p-2 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
              <button @click="editor.chain().focus().toggleBold().run()" :class="toolbarBtn(editor.isActive('bold'))">B</button>
              <button @click="editor.chain().focus().toggleItalic().run()" :class="toolbarBtn(editor.isActive('italic'))"><em>I</em></button>
              <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="toolbarBtn(editor.isActive('heading'))">H2</button>
              <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="toolbarBtn(editor.isActive('heading', { level: 3 }))">H3</button>
              <button @click="editor.chain().focus().toggleBulletList().run()" :class="toolbarBtn(editor.isActive('bulletList'))">列表</button>
              <button @click="editor.chain().focus().toggleCodeBlock().run()" :class="toolbarBtn(editor.isActive('codeBlock'))">代码</button>
              <button @click="editor.chain().focus().toggleBlockquote().run()" :class="toolbarBtn(editor.isActive('blockquote'))">引用</button>
              <button @click="insertImage" class="px-3 py-1 text-sm rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300">图片</button>
            </div>
            <editor-content :editor="editor" class="min-h-[400px] dark:text-white" />
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <textarea
              v-model="form.content"
              placeholder="使用 Markdown 格式书写..."
              class="w-full min-h-[400px] px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-lg font-mono text-sm outline-none resize-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            ></textarea>
            <div
              class="prose prose-sm dark:prose-invert max-w-none p-4 border border-gray-200 dark:border-gray-600 rounded-lg overflow-auto bg-gray-50 dark:bg-gray-700"
              v-html="markdownPreview"
            ></div>
          </div>

          <div>
            <input
              v-model="form.meta_description"
              type="text"
              placeholder="SEO 描述 (可选，160字以内)"
              maxlength="160"
              class="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg outline-none text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          <div class="flex items-center gap-4">
            <button
              @click="saveArticle"
              :disabled="saving"
              class="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition disabled:opacity-50"
            >
              {{ saving ? '保存中...' : (form.status === 'published' ? '发布文章' : '保存草稿') }}
            </button>
            <span v-if="savedAt" class="text-sm text-green-500">已保存于 {{ savedAt }}</span>
            <span v-if="autoSaveStatus" class="text-sm text-gray-400 dark:text-gray-500">{{ autoSaveStatus }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import api from '../api'

const route = useRoute()
const router = useRouter()
const isEditing = computed(() => !!route.params.slug)
const editorMode = ref('rich')
const saving = ref(false)
const savedAt = ref('')
const autoSaveStatus = ref('')
const tagInput = ref('')
const selectedTags = ref([])
const allTags = ref([])

const form = ref({
  title: '',
  content: '',
  status: 'draft',
  meta_description: '',
  meta_keywords: '',
})

const DRAFT_KEY = computed(() => `draft_${route.params.slug || 'new'}`)

const editor = useEditor({
  extensions: [
    StarterKit,
    Image,
    Link.configure({ openOnClick: false }),
    Placeholder.configure({ placeholder: '开始写作...' }),
  ],
  content: '',
  onUpdate: ({ editor: e }) => {
    form.value.content = e.getHTML()
    scheduleDraftSave()
  },
})

const markdownPreview = computed(() => {
  return DOMPurify.sanitize(marked(form.value.content || ''))
})

function toolbarBtn(active) {
  return ['px-3 py-1 text-sm rounded transition', active ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400' : 'hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300']
}

let draftSaveTimeout = null
function scheduleDraftSave() {
  if (draftSaveTimeout) clearTimeout(draftSaveTimeout)
  draftSaveTimeout = setTimeout(() => {
    saveDraftToLocal()
  }, 2000)
}

function saveDraftToLocal() {
  const draftData = {
    title: form.value.title,
    content: form.value.content,
    status: form.value.status,
    meta_description: form.value.meta_description,
    tags: selectedTags.value,
    savedAt: new Date().toISOString(),
  }
  localStorage.setItem(DRAFT_KEY.value, JSON.stringify(draftData))
  autoSaveStatus.value = '草稿已本地缓存'
  setTimeout(() => { autoSaveStatus.value = '' }, 3000)
}

function loadDraftFromLocal() {
  const saved = localStorage.getItem(DRAFT_KEY.value)
  if (!saved) return false
  try {
    const data = JSON.parse(saved)
    form.value.title = data.title || ''
    form.value.content = data.content || ''
    form.value.status = data.status || 'draft'
    form.value.meta_description = data.meta_description || ''
    if (data.tags) selectedTags.value = data.tags
    if (editor.value) {
      editor.value.commands.setContent(data.content || '')
    }
    return true
  } catch (e) {
    return false
  }
}

function clearLocalDraft() {
  localStorage.removeItem(DRAFT_KEY.value)
}

watch(() => form.value.title, scheduleDraftSave)
watch(() => form.value.meta_description, scheduleDraftSave)

async function addTag() {
  const name = tagInput.value.trim()
  if (!name) return
  let tag = allTags.value.find(t => t.name === name)
  if (!tag) {
    const { data } = await api.post('/tags/', { name })
    tag = data
    allTags.value.push(tag)
  }
  if (!selectedTags.value.find(t => t.id === tag.id)) {
    selectedTags.value.push(tag)
  }
  tagInput.value = ''
}

function removeTag(tag) {
  selectedTags.value = selectedTags.value.filter(t => t.id !== tag.id)
}

async function insertImage() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('image', file)
    const { data } = await api.post('/images/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    editor.value.chain().focus().setImage({ src: data.url }).run()
  }
  input.click()
}

async function saveArticle() {
  saving.value = true
  try {
    const payload = {
      title: form.value.title,
      content: editorMode.value === 'rich' ? editor.value.getHTML() : form.value.content,
      status: form.value.status,
      meta_description: form.value.meta_description,
      tag_ids: selectedTags.value.map(t => t.id),
    }

    let response
    if (isEditing.value) {
      response = await api.put(`/articles/${route.params.slug}/`, payload)
    } else {
      response = await api.post('/articles/', payload)
    }

    savedAt.value = new Date().toLocaleTimeString('zh-CN')
    clearLocalDraft()
    if (!isEditing.value) {
      router.replace(`/editor/${response.data.slug}`)
    }
  } finally {
    saving.value = false
  }
}

let autoSaveInterval
onMounted(async () => {
  const tagsRes = await api.get('/tags/')
  allTags.value = tagsRes.data.results || tagsRes.data

  if (isEditing.value) {
    const { data } = await api.get(`/articles/${route.params.slug}/`)
    form.value.title = data.title
    form.value.content = data.content
    form.value.status = data.status
    form.value.meta_description = data.meta_description || ''
    selectedTags.value = data.tags || []
    if (editor.value) {
      editor.value.commands.setContent(data.content)
    }
  } else {
    loadDraftFromLocal()
  }

  autoSaveInterval = setInterval(() => {
    if (form.value.title && form.value.status === 'draft' && isEditing.value) {
      saveArticle()
    }
  }, 30000)
})

onBeforeUnmount(() => {
  clearInterval(autoSaveInterval)
  if (draftSaveTimeout) clearTimeout(draftSaveTimeout)
  if (form.value.title || form.value.content) {
    saveDraftToLocal()
  }
  if (editor.value) editor.value.destroy()
})
</script>
