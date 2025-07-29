<template>
  <div id="instructor-chalkboard-view" class="container-large py-5">
    <h1 class="mb-5" v-if="quiz">
      Quiz {{ quiz?.order }}
    </h1>
    <v-row v-if="quiz">
      <v-col cols="12" sm="7">
        <v-card>
          <v-card-title>
            [Question]
          </v-card-title>
          <v-card-text>
            <div class="d-flex justify-center mb-3">
              <v-img
                v-if="quiz?.image_url"
                :src="quiz?.image_url"
                max-width="100%"
              />
            </div>
            <p class="mt-3">
              {{ quiz?.content }}
            </p>
          </v-card-text>
        </v-card>
        <v-card
          v-for="option in quiz?.options"
          :key="option.order"
          class="mt-3"
        >
          <v-card-text>
            <p>
              <b class="text-primary">[Option {{ option.order }}]</b>
              {{ option.content }}
            </p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="5">
        <div>
          <h2>Answer</h2>
          <div class="pt-3">
            <v-btn
              v-if="!showAnswer"
              color="primary"
              @click="showAnswer = true"
              :disabled="quiz?.state !== 3"
            >
              Reveal answer
            </v-btn>
            <h2
              v-if="showAnswer"
              class="text-primary"
            >
              {{ quiz?.answer }}
            </h2>
          </div>
        </div>
        <div class="mt-10">
          <h2>Results</h2>
          <div class="pt-3">
            <v-btn
              v-if="!showResult"
              color="info"
              @click="loadResults"
              :loading="isResultsLoading"
              :disabled="quiz?.state !== 3"
            >
              Reveal results
            </v-btn>
            <div v-if="showResult">
            <BarChart
              :labels="result.orders.map((order: number) => `Option ${order}`)"
              :data="result.ratios.map((ratio: number) => Number(ratio))"
            />
          </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <div v-else class="d-flex flex-column align-center justify-center py-10">
      <v-progress-circular
        indeterminate
        color="primary"
      />
      <p class="mt-5">Waiting for quiz...</p>
    </div>
    <v-snackbar
      :text="snackbar.message"
      location="top"
      variant="outlined"
      :color="snackbar.color"
      v-model="snackbar.isVisible"
    >
      <template #actions>
        <v-btn @click="snackbar.isVisible = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">

  import {
    ref,
    reactive,
    onMounted,
  } from 'vue'

  import http from '@/http'
  import BarChart from '@/comps/BarChart.vue'

  import type { QuizType } from '@/types'


  const quiz = ref<QuizType | null>(null)
  const showAnswer = ref(false)
  const showResult = ref(false)
  const isResultsLoading = ref(false)

  const result = reactive({
    orders: [] as number[],
    ratios: [] as number[]
  })
  const snackbar = reactive({
    message: '',
    color: '',
    isVisible: false
  })


  const getWebsocketTicket = async () => {
    try {
      const response = await http.post('/api/websocket/ticket/')
      return response.data.ticket
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to get websocket ticket."
      snackbar.color = 'error'
      snackbar.isVisible = true
      return null
    }
  }
  const connectWebsocket = async (ticket: string) => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    try {
      const ws = new WebSocket(`${protocol}://${window.location.host}/ws/instructor/?ticket=${ticket}`)
      ws.onmessage = onWebsocketMessage
      return ws
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to connect to websocket."
      snackbar.color = 'error'
      snackbar.isVisible = true
      return null
    }
  }
  const onWebsocketMessage = async (event: MessageEvent) => {
    const data = JSON.parse(event.data)
    if (data.type === 'instructor_live_quiz') {
      quiz.value = data.quiz_data
      showAnswer.value = false
      showResult.value = false
      isResultsLoading.value = false
      result.orders = []
      result.ratios = []
    }
  }
  const loadResults = async () => {
    if (isResultsLoading.value || !quiz.value) {
      return
    }
    isResultsLoading.value = true
    try {
      const response = await http.get(`/api/instructor/quizzes/${quiz.value.id}/results/`)
      const data = response.data
      result.orders = data.orders
      if (data.total === 0) {
        result.ratios = data.counts.map(
          () => 0
        )
      } else {
        result.ratios = data.counts.map(
          (count: number) => Math.floor(count / data.total * 100)
        )
      }
      showResult.value = true
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to reveal results."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      isResultsLoading.value = false
    }
  }

  onMounted(async () => {
    const ticket = await getWebsocketTicket()
    if (ticket) {
      const ws = await connectWebsocket(ticket)
      if (ws) {
        ws.onmessage = onWebsocketMessage
      }
    }
  })

</script>
