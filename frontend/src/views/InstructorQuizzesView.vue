<template>
  <div id="instructor-quizzes-view" class="container-medium py-5">
    <h1 class="text-center mb-5">Quizzes</h1>
    <v-data-table-server
      no-data-text="No quizzes."
      loading-text="Loading quizzes..."
      items-per-page-text="Quizzes per page"
      :headers="headers"
      :items="dt.items"
      :items-length="dt.itemsLength"
      :loading="dt.isLoading"
      v-model:page="dt.options.page"
      v-model:items-per-page="dt.options.itemsPerPage"
      v-model:sort-by="dt.options.sortBy"
      :items-per-page-options="[10, 20, 50, 100]"
      :hide-default-footer="dt.itemsLength <= dt.options.itemsPerPage"
      @update:options="loadQuizzes"
    >
      <template v-slot:item.order="{ item }">
        {{ item.order }}
      </template>
      <template v-slot:item.state="{ item }">
        <v-chip
          v-if="item.state === 1"
          color="warning"
          variant="flat"
          prepend-icon="mdi-calendar-outline"
        >
          Pending
        </v-chip>
        <v-chip
          v-if="item.state === 2"
          color="primary"
          variant="flat"
          prepend-icon="mdi-clock-outline"
        >
          Active
        </v-chip>
        <v-chip
          v-if="item.state === 3"
          color="success"
          variant="flat"
          prepend-icon="mdi-chart-bar"
        >
          Reviewing
        </v-chip>
        <v-chip
          v-if="item.state === 4"
          color="grey"
          variant="flat"
          prepend-icon="mdi-check-circle-outline"
        >
          Closed
        </v-chip>
      </template>
      <template v-slot:item.content="{ item }">
        <v-btn
          prepend-icon="mdi-file-document-outline"
          color="info"
          variant="elevated"
          size="small"
          @click="showQuizContentDialog(item)"
        >
          View content
        </v-btn>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn
          v-if="item.state === 1"
          prepend-icon="mdi-play"
          color="primary"
          variant="elevated"
          size="small"
          @click="showActivateQuizDialog(item.id)"
        >
          Activate
        </v-btn>
        <v-btn
          class="mr-3"
          v-if="item.state === 2 || item.state === 3"
          prepend-icon="mdi-stop"
          color="error"
          variant="elevated"
          size="small"
          @click="showCloseQuizDialog(item.id)"
        >
          Close
        </v-btn>
        <v-btn
          class="mr-3"
          v-if="item.state === 2 || item.state === 4"
          prepend-icon="mdi-chart-bar"
          color="success"
          variant="elevated"
          size="small"
          @click="showReviewQuizDialog(item.id)"
        >
          Review
        </v-btn>
        <v-btn
          v-if="item.state === 4"
          prepend-icon="mdi-restart"
          color="grey"
          variant="elevated"
          size="small"
          @click="showActivateQuizDialog(item.id)"
        >
          Reactivate
        </v-btn>
      </template>
    </v-data-table-server>
    <v-dialog v-model="quizContentDialog.isVisible" max-width="560">
      <v-card>
        <v-card-title class="text-h6">
          Quiz {{ quizContentDialog.quiz?.order }} Content
        </v-card-title>
        <v-card-text>
          <div class="d-flex justify-center mb-3">
            <v-img
              v-if="quizContentDialog.quiz?.image_url"
              :src="quizContentDialog.quiz?.image_url"
              max-width="480"
            />
          </div>
          <p class="mb-3">
            {{ quizContentDialog.quiz?.content }}
          </p>
          <v-list>
            <v-list-item
              v-for="option in quizContentDialog.quiz?.options"
              :key="option.id"
              :prepend-icon="option.order === quizContentDialog.quiz?.answer ? 'mdi-check-circle-outline' : 'mdi-circle-outline'"
              :color="option.order === quizContentDialog.quiz?.answer ? 'success' : 'grey'"
            >
              <p>
                <b>[Option {{ option.order }}]</b>
                {{ option.content }}
              </p>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="quizContentDialog.isVisible = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="activateQuizDialog.isVisible" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Activate Quiz
        </v-card-title>
        <v-card-text>
          Activate quiz {{ activateQuizDialog.id }}?
          <v-alert
            class="mt-5 mb-0"
            type="warning"
            variant="tonal"
            density="compact"
            icon="mdi-alert-circle-outline"
          >
            All previous quizzes will be <b>closed</b>, and all future quizzes will be <b>pending</b>.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="activateQuizDialog.isVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="activateQuizDialog.isLoading"
            @click="activateQuiz"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="reviewQuizDialog.isVisible" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Review Quiz
        </v-card-title>
        <v-card-text>
          Review quiz {{ reviewQuizDialog.id }}?
          <v-alert
            class="mt-5 mb-0"
            type="warning"
            variant="tonal"
            density="compact"
            icon="mdi-alert-circle-outline"
          >
            All previous quizzes will be <b>closed</b>, and all future quizzes will be <b>pending</b>.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="reviewQuizDialog.isVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success"
            variant="elevated"
            :loading="reviewQuizDialog.isLoading"
            @click="reviewQuiz"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="closeQuizDialog.isVisible" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Close Quiz
        </v-card-title>
        <v-card-text>
          Close quiz {{ closeQuizDialog.id }}?
          <v-alert
            class="mt-5 mb-0"
            type="warning"
            variant="tonal"
            density="compact"
            icon="mdi-alert-circle-outline"
          >
            All previous quizzes will be <b>closed</b>, and all future quizzes will be <b>pending</b>.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="closeQuizDialog.isVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="closeQuizDialog.isLoading"
            @click="closeQuiz"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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

  import type {
    DataTableSortItem as DataTableSortItemType,
  } from 'vuetify'
  import type {
    QuizType,
    DataTableOptionsType,
  } from '@/types'

  import { reactive } from 'vue'

  import http from '@/http'


  const headers = [
    {
      title: 'Order',
      key: 'order',
    },
    {
      title: 'Content',
      key: 'content',
      sortable: false,
    },
    {
      title: 'State',
      key: 'state',
      sortable: false,
    },
    {
      title: 'Actions',
      key: 'actions',
      sortable: false,
    },
  ]

  const dt = reactive({
    items: [] as QuizType[],
    itemsLength: 0,
    options: {
      page: 1,
      itemsPerPage: 10,
      sortBy: [{
        key: 'order',
        order: 'asc',
      }]
    } as DataTableOptionsType,
    isLoading: true,
  })
  const snackbar = reactive({
    message: '',
    color: '',
    isVisible: false
  })
  const quizContentDialog = reactive({
    quiz: null as (QuizType | null),
    isVisible: false
  })
  const activateQuizDialog = reactive({
    id: 0,
    isLoading: false,
    isVisible: false
  })
  const reviewQuizDialog = reactive({
    id: 0,
    isLoading: false,
    isVisible: false
  })
  const closeQuizDialog = reactive({
    id: 0,
    isLoading: false,
    isVisible: false
  })

  const showQuizContentDialog = (quiz: QuizType) => {
    quizContentDialog.quiz = quiz
    quizContentDialog.isVisible = true
  }
  const showActivateQuizDialog = (id: number) => {
    activateQuizDialog.id = id
    activateQuizDialog.isVisible = true
  }
  const showReviewQuizDialog = (id: number) => {
    reviewQuizDialog.id = id
    reviewQuizDialog.isVisible = true
  }
  const showCloseQuizDialog = (id: number) => {
    closeQuizDialog.id = id
    closeQuizDialog.isVisible = true
  }

  const loadQuizzes = async (options: DataTableOptionsType) => {
    Object.assign(dt.options, options)
    dt.isLoading = true
    const params = {
      page: options.page,
      page_size: options.itemsPerPage,
      ordering: options.sortBy.map(
        (sortItem: DataTableSortItemType) => (sortItem.order === 'desc' ? '-' : '') + sortItem.key
      ).join(',')
    }
    try {
      const res = await http.get('/api/instructor/quizzes/', { params })
      dt.items = res.data.results
      dt.itemsLength = res.data.count
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to load quizzes."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      dt.isLoading = false
    }
  }
  const activateQuiz = async () => {
    if (activateQuizDialog.isLoading) {
      return
    }
    activateQuizDialog.isLoading = true
    try {
      const res = await http.post(`/api/instructor/quizzes/${activateQuizDialog.id}/activate/`)
      snackbar.message = res.data.message
      snackbar.color = 'primary'
      snackbar.isVisible = true
      await loadQuizzes(dt.options)
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to activate quiz."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      activateQuizDialog.isLoading = false
      activateQuizDialog.isVisible = false
    }
  }
  const reviewQuiz = async () => {
    if (reviewQuizDialog.isLoading) {
      return
    }
    reviewQuizDialog.isLoading = true
    try {
      const res = await http.post(`/api/instructor/quizzes/${reviewQuizDialog.id}/review/`)
      snackbar.message = res.data.message
      snackbar.color = 'success'
      snackbar.isVisible = true
      await loadQuizzes(dt.options)
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to review quiz."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      reviewQuizDialog.isLoading = false
      reviewQuizDialog.isVisible = false
    }
  }
  const closeQuiz = async () => {
    if (closeQuizDialog.isLoading) {
      return
    }
    closeQuizDialog.isLoading = true
    try {
      const res = await http.post(`/api/instructor/quizzes/${closeQuizDialog.id}/close/`)
      snackbar.message = res.data.message
      snackbar.color = 'error'
      snackbar.isVisible = true
      await loadQuizzes(dt.options)
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to close quiz."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      closeQuizDialog.isLoading = false
      closeQuizDialog.isVisible = false
    }
  }

</script>
