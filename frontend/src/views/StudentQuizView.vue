<template>
  <div id="student-quiz-view" class="container-small py-5">
    <div v-if="quiz">
      <p class="text-center mb-3">
        {{ quiz?.content }}
      </p>
      <v-img
        v-if="quiz?.image_url"
        :src="quiz?.image_url"
        max-width="100%"
      />
      <v-divider class="my-5" />
      <v-card
        v-for="option in quiz?.options"
        :key="option.order"
        @click="selectOption(option)"
        :class="option.is_selected ? 'selected' : ''"
        class="cursor-pointer mt-3"
      >
        <v-card-text>
          <p>
            <b class="text-primary">[Option {{ option.order }}]</b>
            {{ option.content }}
          </p>
        </v-card-text>
      </v-card>
    </div>
    <div v-else>
      <div class="d-flex flex-column align-center justify-center py-10">
        <v-progress-circular
          indeterminate
          color="primary"
        />
        <p class="mt-5">Waiting for quiz...</p>
      </div>
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

<style scoped>
  .selected p {
    font-weight: bold;
  }
</style>

<script setup lang="ts">

  import {
    ref,
    reactive,
    onMounted,
  } from 'vue'
  import shuffle from 'lodash/shuffle'

  import http from '@/http'

  import type {
    OptionType,
    QuizType,
  } from '@/types'


  const quiz = ref<QuizType | null>(null)
  const isResponseLoading = ref(false)
  const isSelectLoading = ref(false)

  const snackbar = reactive({
    message: '',
    color: '',
    isVisible: false
  })


  const loadResponses = async () => {
    if (isResponseLoading.value || !quiz.value) {
      return
    }
    isResponseLoading.value = true
    try {
      const res = await http.get('/api/student/responses/', {
        params: {
          quiz: quiz.value?.id,
        },
      })
      let selected_option_id = null
      for (const response of res.data.results) {
        selected_option_id = response.option
      }
      for (const option of quiz.value?.options || []) {
        option.is_selected = option.id === selected_option_id
      }
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to load responses."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      isResponseLoading.value = false
    }
  }
  const selectOption = async (option: OptionType) => {
    if (isSelectLoading.value) {
      return
    }
    isSelectLoading.value = true
    try {
      await http.post('/api/student/responses/', {
        quiz: quiz.value?.id,
        option: option.id,
      })
      await loadResponses()
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to submit response."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      isSelectLoading.value = false
    }
  }
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
      const ws = new WebSocket(`${protocol}://${window.location.host}/ws/student/?ticket=${ticket}`)
      ws.onmessage = onWebsocketMessage
      return ws
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to connect websocket."
      snackbar.color = 'error'
      snackbar.isVisible = true
      return null
    }
  }
  const onWebsocketMessage = async (event: MessageEvent) => {
    const data = JSON.parse(event.data)
    if (data.type === 'student_live_quiz') {
      quiz.value = data.quiz_data
      if (quiz.value) {
        quiz.value.options = shuffle(quiz.value.options)
        await loadResponses()
      }
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
