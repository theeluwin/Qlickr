<template>
  <div id="instructor-lessons-view" class="container-small pt-5">
    <h1 class="text-center mb-5">Lessons</h1>
    <v-data-table-server
      no-data-text="No lessons."
      loading-text="Loading lessons..."
      items-per-page-text="Lessons per page"
      :headers="headers"
      :items="dt.items"
      :items-length="dt.itemsLength"
      :loading="dt.isLoading"
      v-model:page="dt.options.page"
      v-model:items-per-page="dt.options.itemsPerPage"
      v-model:sort-by="dt.options.sortBy"
      :items-per-page-options="[10, 20, 50, 100]"
      :hide-default-footer="dt.itemsLength <= dt.options.itemsPerPage"
      @update:options="loadLessons"
    >
      <template v-slot:item.seq="{ item }">
        {{ item.seq }}
      </template>
      <template v-slot:item.date="{ item }">
        {{ formatDate(item.date) }}
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
          color="grey"
          variant="flat"
          prepend-icon="mdi-check-circle-outline"
        >
          Closed
        </v-chip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn
          v-if="item.state === 1"
          prepend-icon="mdi-play"
          color="primary"
          variant="elevated"
          size="small"
          @click="showActivateLessonDialog(item.seq)"
        >
          Activate
        </v-btn>
        <v-btn
          v-if="item.state === 2"
          prepend-icon="mdi-stop"
          color="error"
          variant="elevated"
          size="small"
          @click="showCloseLessonDialog(item.seq)"
        >
          Close
        </v-btn>
        <v-btn
          v-if="item.state === 3"
          prepend-icon="mdi-restart"
          color="grey"
          variant="elevated"
          size="small"
          @click="showActivateLessonDialog(item.seq)"
        >
          Reactivate
        </v-btn>
      </template>
    </v-data-table-server>
    <v-dialog v-model="activateLessonDialog.isVisible" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Activate Lesson
        </v-card-title>
        <v-card-text>
          Activate lesson {{ activateLessonDialog.seq }}?
          <v-alert
            class="mt-5 mb-0"
            type="warning"
            variant="tonal"
            density="compact"
            icon="mdi-alert-circle-outline"
          >
            All previous lessons will be <b>closed</b>, and all future lessons will be <b>pending</b>. All quizzes will be <b>closed</b>.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="activateLessonDialog.isVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="activateLessonDialog.isLoading"
            @click="activateLesson"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="closeLessonDialog.isVisible" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Close Lesson
        </v-card-title>
        <v-card-text>
          Close lesson {{ closeLessonDialog.seq }}?
          <v-alert
            class="mt-5 mb-0"
            type="warning"
            variant="tonal"
            density="compact"
            icon="mdi-alert-circle-outline"
          >
            All previous lessons will be <b>closed</b>, and all future lessons will be <b>pending</b>. All quizzes will be <b>closed</b>.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey"
            variant="text"
            @click="closeLessonDialog.isVisible = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="closeLessonDialog.isLoading"
            @click="closeLesson"
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

  import { reactive } from 'vue'

  import http from '@/http'
  import { formatDate } from '@/utils'

  import type {
    DataTableSortItem as DataTableSortItemType,
  } from 'vuetify'

  import type {
    LessonType,
    DataTableOptionsType,
  } from '@/types'


  const headers = [
    {
      title: 'No.',
      key: 'seq',
    },
    {
      title: 'Date',
      key: 'date',
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
    items: [] as LessonType[],
    itemsLength: 0,
    options: {
      page: 1,
      itemsPerPage: 10,
      sortBy: [{
        key: 'seq',
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
  const activateLessonDialog = reactive({
    seq: 0,
    isLoading: false,
    isVisible: false
  })
  const closeLessonDialog = reactive({
    seq: 0,
    isLoading: false,
    isVisible: false
  })

  const showActivateLessonDialog = (seq: number) => {
    activateLessonDialog.seq = seq
    activateLessonDialog.isVisible = true
  }
  const showCloseLessonDialog = (seq: number) => {
    closeLessonDialog.seq = seq
    closeLessonDialog.isVisible = true
  }

  const loadLessons = async (options: DataTableOptionsType) => {
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
      const res = await http.get('/api/instructor/lessons/', { params })
      dt.items = res.data.results
      dt.itemsLength = res.data.count
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to load lessons."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      dt.isLoading = false
    }
  }
  const activateLesson = async () => {
    if (activateLessonDialog.isLoading) {
      return
    }
    activateLessonDialog.isLoading = true
    try {
      const res = await http.post(`/api/instructor/lessons/${activateLessonDialog.seq}/activate/`)
      snackbar.message = res.data.message
      snackbar.color = 'primary'
      snackbar.isVisible = true
      await loadLessons(dt.options)
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to activate lesson."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      activateLessonDialog.isLoading = false
      activateLessonDialog.isVisible = false
    }
  }
  const closeLesson = async () => {
    if (closeLessonDialog.isLoading) {
      return
    }
    closeLessonDialog.isLoading = true
    try {
      const res = await http.post(`/api/instructor/lessons/${closeLessonDialog.seq}/close/`)
      snackbar.message = res.data.message
      snackbar.color = 'error'
      snackbar.isVisible = true
      await loadLessons(dt.options)
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to close lesson."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      closeLessonDialog.isLoading = false
      closeLessonDialog.isVisible = false
    }
  }

</script>
