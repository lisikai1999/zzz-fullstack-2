import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/article/:slug',
    name: 'ArticleDetail',
    component: () => import('../views/ArticleDetail.vue'),
  },
  {
    path: '/editor',
    name: 'NewArticle',
    component: () => import('../views/Editor.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/editor/:slug',
    name: 'EditArticle',
    component: () => import('../views/Editor.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tag/:slug',
    name: 'TagArticles',
    component: () => import('../views/TagArticles.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/drafts',
    name: 'Drafts',
    component: () => import('../views/Drafts.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/leaderboard',
    name: 'Leaderboard',
    component: () => import('../views/Leaderboard.vue'),
  },
  {
    path: '/profile/:username?',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
  },
  {
    path: '/shared',
    name: 'SharedArticles',
    component: () => import('../views/SharedArticles.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
