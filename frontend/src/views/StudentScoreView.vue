<template>
  <div id="student-score-view" class="container-small py-5">
    <h1 class="text-center mb-5">Score</h1>
    <v-table>
      <thead>
        <tr>
          <th class="text-left">
            Item
          </th>
          <th class="text-left">
            Score
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Quiz</td>
          <td>{{ student.eval_quiz }} / {{ student.quiz_count }}</td>
        </tr>
        <tr>
          <td>Project 1</td>
          <td>{{ student.eval_project1 }}</td>
        </tr>
        <tr>
          <td>Project 2</td>
          <td>{{ student.eval_project2 }}</td>
        </tr>
        <tr>
          <td>Project 3</td>
          <td>{{ student.eval_project3 }}</td>
        </tr>
        <tr>
          <td>Midterm</td>
          <td>{{ student.eval_midterm }}</td>
        </tr>
        <tr>
          <td>Finals</td>
          <td>{{ student.eval_finals }}</td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup lang="ts">

  import {
    reactive,
    onMounted,
  } from 'vue'

  import http from '@/http'
  import { useUserStore } from '@/stores/user'


  const userStore = useUserStore()

  const student = reactive({
    eval_project1: 0,
    eval_project2: 0,
    eval_project3: 0,
    eval_midterm: 0,
    eval_finals: 0,
    eval_quiz: 0,
    quiz_count: 0,
    isLoading: false
  })
  const snackbar = reactive({
    message: '',
    color: 'error',
    isVisible: false
  })


  const loadStudent = async () => {
    if (student.isLoading) {
      return
    }
    student.isLoading = true
    try {
      const res = await http.get('/api/student/me/')
      const data = res.data
      student.eval_project1 = data.eval_project1
      student.eval_project2 = data.eval_project2
      student.eval_project3 = data.eval_project3
      student.eval_midterm = data.eval_midterm
      student.eval_finals = data.eval_finals
      student.eval_quiz = data.eval_quiz
      student.quiz_count = data.quiz_count
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to load student information."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      student.isLoading = false
    }
  }

  onMounted(async () => {
    if (!userStore.isStaff) {
      try {
        await loadStudent()
      } catch (err: any) {
        snackbar.message = err.response?.data?.error || "Failed to load student information."
        snackbar.color = 'error'
        snackbar.isVisible = true
      }
    }
  })

</script>
