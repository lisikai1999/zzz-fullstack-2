import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useGamificationStore = defineStore('gamification', () => {
  const xpProfile = ref(null)
  const achievements = ref([])
  const leaderboard = ref([])
  const readingHistory = ref([])

  async function fetchMyXP() {
    const { data } = await api.get('/gamification/me/')
    xpProfile.value = data.xp_profile
    achievements.value = data.achievements
    return data
  }

  async function recordRead(articleId) {
    const { data } = await api.post(`/gamification/read/${articleId}/`)
    if (data.xp_profile) {
      xpProfile.value = data.xp_profile
    }
    return data
  }

  async function fetchLeaderboard() {
    const { data } = await api.get('/gamification/leaderboard/')
    leaderboard.value = data.results || data
    return leaderboard.value
  }

  async function fetchHistory() {
    const { data } = await api.get('/gamification/history/')
    readingHistory.value = data.results || data
    return readingHistory.value
  }

  return { xpProfile, achievements, leaderboard, readingHistory, fetchMyXP, recordRead, fetchLeaderboard, fetchHistory }
})
