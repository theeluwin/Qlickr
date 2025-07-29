<template>
  <div id="profile-view" class="container-small py-5">
    <h1 class="text-center mb-5">Profile</h1>
    <v-card class="mb-10">
      <v-card-title class="px-5 py-6">
        <v-icon color="info">mdi-email</v-icon>
        Change Email
      </v-card-title>
      <v-card-text class="px-5 py-0">
        <v-form
          lazy-validation
          ref="usernameFormRef"
          v-model="usernameForm.isValid"
          @submit.prevent="changeUsername"
        >
          <v-text-field
            class="mb-3"
            label="Email"
            variant="outlined"
            prepend-inner-icon="mdi-email-outline"
            required
            type="email"
            v-model="usernameForm.username"
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
            v-model="usernameForm.usernameConfirm"
            :rules="[
              (v: string) => !!v || 'Email confirm is required',
              (v: string) => /.+@.+\..+/.test(v) || 'Please enter a valid email address',
              (v: string) => v === usernameForm.username || 'Emails do not match'
            ]"
          />
          <v-btn
            class="mb-5"
            block
            size="large"
            color="info"
            prepend-icon="mdi-email-edit"
            type="submit"
            :disabled="!usernameForm.isValid"
            :loading="usernameForm.isLoading"
          >
            Change
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
    <v-card class="mb-10">
      <v-card-title class="px-5 py-6">
        <v-icon color="warning">mdi-lock</v-icon>
        Change Password
      </v-card-title>
      <v-card-text class="px-5 py-0">
        <v-form
          lazy-validation
          ref="passwordFormRef"
          v-model="passwordForm.isValid"
          @submit.prevent="changePassword"
        >
          <v-text-field
            class="mb-3"
            label="New Password"
            variant="outlined"
            prepend-inner-icon="mdi-lock-outline"
            required
            type="password"
            v-model="passwordForm.password"
            :rules="[
              (v: string) => !!v || 'New password is required',
              (v: string) => v.length >= 8 || 'Password must be at least 8 characters'
            ]"
          />
          <v-text-field
            class="mb-3"
            label="New Password Confirm"
            variant="outlined"
            prepend-inner-icon="mdi-lock-check-outline"
            required
            type="password"
            v-model="passwordForm.passwordConfirm"
            :rules="[
              (v: string) => !!v || 'New password confirm is required',
              (v: string) => v.length >= 8 || 'Password must be at least 8 characters',
              (v: string) => v === passwordForm.password || 'Passwords do not match'
            ]"
          />
          <v-btn
            class="mb-5"
            block
            size="large"
            color="warning"
            prepend-icon="mdi-lock-reset"
            type="submit"
            :disabled="!passwordForm.isValid"
            :loading="passwordForm.isLoading"
          >
            Change
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
    <v-card class="mb-10" v-if="!userStore.isStaff">
      <v-card-title class="px-5 py-6">
        <v-icon color="success">mdi-school</v-icon>
        Modify Student Information
      </v-card-title>
      <v-card-text class="px-5 py-0">
        <v-form
          lazy-validation
          ref="studentFormRef"
          v-model="studentForm.isValid"
          @submit.prevent="modifyStudent"
        >
          <v-text-field
            class="mb-3"
            label="Student ID"
            variant="outlined"
            prepend-inner-icon="mdi-identifier"
            required
            v-model="studentForm.personalSid"
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
            v-model="studentForm.personalName"
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
            v-model="studentForm.roleDepartment"
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
            v-model="studentForm.roleMajor"
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
            v-model="studentForm.roleYear"
            :rules="[
              (v: number) => !!v || 'Year is required',
              (v: number) => v > 0 || 'Year must be at least 1'
            ]"
          />
          <v-btn
            class="mb-5"
            block
            size="large"
            color="success"
            prepend-icon="mdi-content-save"
            type="submit"
            :disabled="!studentForm.isValid"
            :loading="studentForm.isLoading"
          >
            Modify
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
    onMounted,
  } from 'vue'

  import http from '@/http'
  import { useUserStore } from '@/stores/user'


  const userStore = useUserStore()

  const usernameFormRef = ref()
  const passwordFormRef = ref()
  const studentFormRef = ref()

  const usernameForm = reactive({
    username: userStore.username || '',
    usernameConfirm: userStore.username || '',
    isValid: true,
    isLoading: false
  })
  const passwordForm = reactive({
    password: '',
    passwordConfirm: '',
    isValid: true,
    isLoading: false
  })
  const studentForm = reactive({
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


  const changeUsername = async () => {
    if (usernameForm.isLoading) {
      return
    }
    if (!usernameFormRef.value?.validate()) {
      return
    }
    usernameForm.isLoading = true
    try {
      const res = await http.patch('/api/user/me/', {
        username: usernameForm.username
      })
      await userStore.loadMe()
      usernameForm.username = userStore.username
      usernameForm.usernameConfirm = userStore.username
      snackbar.message = res.data.message || "Email has been successfully changed."
      snackbar.color = 'success'
      snackbar.isVisible = true
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to change email."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      usernameForm.isLoading = false
    }
  }
  const changePassword = async () => {
    if (passwordForm.isLoading) {
      return
    }
    if (!passwordFormRef.value?.validate()) {
      return
    }
    passwordForm.isLoading = true
    try {
      const res = await http.patch('/api/user/me/', {
        password: passwordForm.password
      })
      passwordForm.password = ''
      passwordForm.passwordConfirm = ''
      await nextTick()
      passwordFormRef.value?.resetValidation()
      snackbar.message = res.data.message || 'Password has been successfully changed.'
      snackbar.color = 'success'
      snackbar.isVisible = true
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to change password."
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      passwordForm.isLoading = false
    }
  }
  const loadStudent = async () => {
    try {
      const res = await http.get('/api/student/me/')
      const data = res.data
      studentForm.personalSid = data.personal_sid
      studentForm.personalName = data.personal_name
      studentForm.roleDepartment = data.role_department
      studentForm.roleMajor = data.role_major
      studentForm.roleYear = data.role_year
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || "Failed to load student information."
      snackbar.color = 'error'
      snackbar.isVisible = true
    }
  }
  const modifyStudent = async () => {
    if (studentForm.isLoading) {
      return
    }
    if (!studentFormRef.value?.validate()) {
      return
    }
    studentForm.isLoading = true
    try {
      const updateData = {
        personal_sid: studentForm.personalSid,
        personal_name: studentForm.personalName,
        role_department: studentForm.roleDepartment,
        role_major: studentForm.roleMajor,
        role_year: studentForm.roleYear
      }
      const res = await http.patch('/api/student/me/', updateData)
      snackbar.message = res.data.message || 'Student information has been successfully modified.'
      snackbar.color = 'success'
      snackbar.isVisible = true
      await loadStudent()
    } catch (err: any) {
      snackbar.message = err.response?.data?.error || 'Failed to modify student information.'
      snackbar.color = 'error'
      snackbar.isVisible = true
    } finally {
      studentForm.isLoading = false
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
