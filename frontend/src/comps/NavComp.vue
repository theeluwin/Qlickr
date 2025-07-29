<template>
  <v-navigation-drawer
    app
    v-model="isDrawerOpened"
    :location="$vuetify.display.mobile ? 'bottom' : 'left'"
    clipped
  >
    <v-list>
      <v-list-item
        link
        prepend-icon="mdi-account-group"
        v-if="userStore.isStaff"
        @click="navigate('instructor-dashboard')"
      >
        Dashboard
      </v-list-item>
      <v-list-item
        link
        prepend-icon="mdi-presentation"
        v-if="userStore.isStaff"
        @click="navigate('instructor-chalkboard')"
      >
        Chalkboard
      </v-list-item>
      <v-list-item
        link
        prepend-icon="mdi-school"
        v-if="userStore.isStaff"
        @click="navigate('instructor-lessons')"
      >
        Lessons
      </v-list-item>
      <v-list-item
        link
        prepend-icon="mdi-book-edit"
        v-if="userStore.isStaff"
        @click="navigate('instructor-quizzes')"
      >
        Quizzes
      </v-list-item>
      <v-list-item
        link
        prepend-icon="mdi-pencil"
        v-if="!userStore.isStaff"
        @click="navigate('student-quiz')"
      >
        Quiz
      </v-list-item>
      <v-list-item
        link
        prepend-icon="mdi-book-account"
        v-if="!userStore.isStaff"
        @click="navigate('student-score')"
      >
        Score
      </v-list-item>
      <v-divider />
      <v-list-item
        link
        prepend-icon="mdi-logout"
        @click="logout"
      >
        Logout
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
  <v-app-bar color="primary">
    <template v-slot:prepend>
      <v-app-bar-nav-icon
        @click.stop="isDrawerOpened = !isDrawerOpened"
      />
    </template>
    <v-app-bar-title
      class="cursor-pointer"
      @click="navigate('index')"
    >
      {{ SITE_TITLE }}
    </v-app-bar-title>
    <template v-slot:append>
      <v-btn
        class="text-transform-none"
        prepend-icon="mdi-account"
        @click="navigate('profile')"
      >
        {{ userStore.username }}
      </v-btn>
    </template>
  </v-app-bar>
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
</template>

<script setup lang="ts">

  import {
    ref,
    reactive,
  } from 'vue'
  import { useRouter } from 'vue-router'

  import { useAuthStore } from '@/stores/auth'
  import { useUserStore } from '@/stores/user'
  import { SITE_TITLE } from '@/constants'


  const router = useRouter()
  const authStore = useAuthStore()
  const userStore = useUserStore()

  const isDrawerOpened = ref(false)

  const snackbar = reactive({
    message: '',
    color: '',
    isVisible: false,
  })


  const navigate = (name: string) => {
    isDrawerOpened.value = false
    router.push({ name })
  }

  const logout = async () => {
    isDrawerOpened.value = false
    await authStore.logout()
    router.push({ name: 'login' })
  }

</script>
