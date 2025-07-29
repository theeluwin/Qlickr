<template>
  <div id="instructor-dashboard-view" class="container-large py-5">
    <h1 class="mb-5">Dashboard</h1>
    <div v-if="quiz">
      <h2>Lesson {{ quiz?.lesson_id }} / Quiz {{ quiz?.order }} / Answer {{ quiz?.answer }}</h2>
      <v-row class="mt-5">
        <v-col
          cols="3"
          v-for="item in rows"
          :key="item.student.personal_sid"
        >
          <v-card>
            <v-card-title>
              {{ item.student.personal_name }}
              <span v-if="!item.response">
                <v-chip
                  color="grey"
                  variant="flat"
                  size="small"
                  class="ml-1 v-card-title-chip"
                >
                  -
                </v-chip>
              </span>
              <span v-else>
                <span v-if="item.response?.option_order === quiz?.answer">
                  <v-chip
                    color="success"
                    variant="flat"
                    size="small"
                    class="ml-1 v-card-title-chip"
                  >
                    <b>{{ item.response?.option_order }}</b>
                  </v-chip>
                </span>
                <span v-else>
                  <v-chip
                    color="error"
                    variant="flat"
                    size="small"
                    class="ml-1 v-card-title-chip"
                  >
                    <b>{{ item.response?.option_order }}</b>
                  </v-chip>
                </span>
              </span>
            </v-card-title>
            <v-card-text class="text-grey">
              <p>{{ item.student.role_major }} {{ item.student.role_year }}</p>
              <p>{{ item.student.personal_sid }}</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
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
    onUnmounted,
  } from 'vue'

  import http from '@/http'

  import type {
    QuizType,
    ResponseType,
  } from '@/types'

  interface RowType {
    student: {
      personal_sid: string
      personal_name: string
      role_department: string
      role_major: string
      role_year: number
    },
    response: ResponseType | null,
  }


  let interval: number | null = null

  const isLoading = ref(false)
  const quiz = ref<QuizType | null>(null)
  const rows = ref<RowType[]>([])

  const snackbar = reactive({
    message: '',
    color: '',
    isVisible: false
  })


  const loadDashboard = async () => {
    isLoading.value = true
    try {
      const response = await http.get('/api/instructor/dashboard/')
      const data = response.data
      quiz.value = data.quiz
      rows.value = data.data
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to load dashboard."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      isLoading.value = false
    }
  }

  onMounted(async () => {
    await loadDashboard()
    interval = setInterval(async () => {
      await loadDashboard()
    }, 1000)
  })
  onUnmounted(() => {
    if (interval) {
      clearInterval(interval)
    }
  })

</script>
