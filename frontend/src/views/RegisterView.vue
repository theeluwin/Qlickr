<template>
  <div id="register-view" class="container-small py-10">
    <h1 class="text-center mb-5">{{ SITE_TITLE }} Register</h1>
    <v-form
      lazy-validation
      ref="formRef"
      v-model="form.isValid"
      @submit.prevent="register"
    >
      <v-text-field
        class="mb-3"
        label="Email"
        variant="outlined"
        prepend-inner-icon="mdi-email-outline"
        required
        type="email"
        v-model="form.username"
        :rules="[
          (v: string) => !!v || 'Email is required',
          (v: string) => /.+@.+\..+/.test(v) || 'Please enter a valid email address'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Email Confirm"
        variant="outlined"
        prepend-inner-icon="mdi-email-check-outline"
        required
        type="email"
        v-model="form.usernameConfirm"
        :rules="[
          (v: string) => !!v || 'Email confirm is required',
          (v: string) => /.+@.+\..+/.test(v) || 'Please enter a valid email address',
          (v: string) => v === form.username || 'Emails do not match'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Password"
        variant="outlined"
        prepend-inner-icon="mdi-lock-outline"
        required
        type="password"
        v-model="form.password"
        :rules="[
          (v: string) => !!v || 'Password is required',
          (v: string) => v.length >= 8 || 'Password must be at least 8 characters'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Password Confirm"
        variant="outlined"
        prepend-inner-icon="mdi-lock-check-outline"
        required
        type="password"
        v-model="form.passwordConfirm"
        :rules="[
          (v: string) => !!v || 'Password confirm is required',
          (v: string) => v.length >= 8 || 'Password must be at least 8 characters',
          (v: string) => v === form.password || 'Passwords do not match'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Student ID"
        variant="outlined"
        prepend-inner-icon="mdi-identifier"
        required
        v-model="form.personalSid"
        :rules="[
          (v: string) => !!v || 'Student ID is required',
          (v: string) => v.length >= 4 || 'Student ID must be at least 4 characters'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Name"
        variant="outlined"
        prepend-inner-icon="mdi-account-edit"
        required
        v-model="form.personalName"
        :rules="[
          (v: string) => !!v || 'Name is required',
          (v: string) => v.length >= 2 || 'Name must be at least 2 characters'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Department"
        variant="outlined"
        prepend-inner-icon="mdi-domain"
        required
        v-model="form.roleDepartment"
        :rules="[
          (v: string) => !!v || 'Department is required',
          (v: string) => v.length >= 2 || 'Department must be at least 2 characters'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Major"
        variant="outlined"
        prepend-inner-icon="mdi-book-education"
        required
        v-model="form.roleMajor"
        :rules="[
          (v: string) => !!v || 'Major is required',
          (v: string) => v.length >= 2 || 'Major must be at least 2 characters'
        ]"
      />
      <v-text-field
        class="mb-3"
        label="Year"
        variant="outlined"
        prepend-inner-icon="mdi-numeric"
        type="number"
        required
        v-model="form.roleYear"
        :rules="[
          (v: number) => !!v || 'Year is required',
          (v: number) => v > 0 || 'Year must be at least 1'
        ]"
      />
      <v-btn
        class="mb-5"
        text="Register"
        block
        size="large"
        color="primary"
        type="submit"
        :disabled="!form.isValid"
        :loading="form.isLoading"
      />
      <v-btn
        class="mb-5"
        text="Go to login"
        block
        size="large"
        color="success"
        @click="router.push({ name: 'login' })"
      />
      <v-snackbar
        :text="snackbar.message"
        location="top"
        variant="outlined"
        :color="snackbar.color"
        v-model="snackbar.isVisible"
      >
        <template #actions>
          <v-btn
            @click="snackbar.isVisible = false"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-form>
  </div>
</template>

<script setup lang="ts">

  import {
    ref,
    reactive,
  } from 'vue'
  import { useRouter } from 'vue-router'

  import http from '@/http'
  import { useAuthStore } from '@/stores/auth'
  import { useUserStore } from '@/stores/user'
  import { SITE_TITLE } from '@/constants'


  const router = useRouter()
  const authStore = useAuthStore()
  const userStore = useUserStore()

  const formRef = ref()

  const form = reactive({
    username: '',
    usernameConfirm: '',
    password: '',
    passwordConfirm: '',
    personalSid: '',
    personalName: '',
    roleDepartment: '',
    roleMajor: '',
    roleYear: 1,
    isValid: true,
    isLoading: false
  })
  const snackbar = reactive({
    message: '',
    color: 'error',
    isVisible: false
  })


  const register = async () => {
    if (form.isLoading) {
      return
    }
    if (!formRef.value?.validate()) {
      return
    }
    form.isLoading = true
    try {
      await http.post('/api/user/register/', {
        username: form.username,
        password: form.password,
        personal_sid: form.personalSid,
        personal_name: form.personalName,
        role_department: form.roleDepartment,
        role_major: form.roleMajor,
        role_year: form.roleYear
      })
      await authStore.login(form.username, form.password)
      await userStore.loadMe()
      router.push({ name: 'index' })
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to register."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      form.isLoading = false
    }
  }

</script>
