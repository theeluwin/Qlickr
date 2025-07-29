<template>
  <div id="password-request-view" class="container-small py-10">
    <h1 class="text-center mb-5">{{ SITE_TITLE }} Password Request</h1>
    <v-card class="mb-10">
      <v-card-text class="px-5 pt-5 pb-0">
        <v-form
          lazy-validation
          ref="formRef"
          v-model="form.isValid"
          @submit.prevent="requestPassword"
        >
          <v-text-field
            class="mb-3"
            label="Email"
            variant="outlined"
            prepend-inner-icon="mdi-email-outline"
            required
            type="email"
            v-model="form.email"
            :rules="[
              (v: string) => !!v || 'Email is required',
              (v: string) => /.+@.+\..+/.test(v) || 'Please enter a valid email address'
            ]"
          />
          <v-btn
            class="mb-5"
            block
            size="large"
            color="info"
            variant="elevated"
            prepend-icon="mdi-email-lock"
            type="submit"
            :disabled="!form.isValid"
            :loading="form.isLoading"
          >
            Send reset link
          </v-btn>
          <v-btn
            class="mb-5"
            block
            size="large"
            color="info"
            variant="text"
            @click="router.push({ name: 'login' })"
          >
            Go to login
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
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
    nextTick,
  } from 'vue'
  import { useRouter } from 'vue-router'

  import http from '@/http'
  import { SITE_TITLE } from '@/constants'


  const router = useRouter()

  const formRef = ref()

  const form = reactive({
    email: '',
    isValid: true,
    isLoading: false
  })
  const snackbar = reactive({
    message: '',
    color: 'error',
    isVisible: false
  })


  const requestPassword = async () => {
    if (form.isLoading) {
      return
    }
    if (!formRef.value?.validate()) {
      return
    }
    form.isLoading = true
    try {
      const res = await http.post('/api/user/password/request/', {
        email: form.email
      })
      form.email = ''
      await nextTick()
      formRef.value?.resetValidation()
      snackbar.message = res.data.message || "Password reset link has been sent to your email."
      snackbar.color = 'success'
      snackbar.isVisible = true
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to send password reset link."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      form.isLoading = false
    }
  }

</script>
