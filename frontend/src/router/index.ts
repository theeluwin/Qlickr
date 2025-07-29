// base
import {
  createRouter,
  createWebHistory,
} from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { SITE_TITLE } from '@/constants'

// views
import LostView from '@/views/LostView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import PasswordRequestView from '@/views/PasswordRequestView.vue'
import PasswordResetView from '@/views/PasswordResetView.vue'
import ProfileView from '@/views/ProfileView.vue'
import InstructorLessonsView from '@/views/InstructorLessonsView.vue'
import InstructorQuizzesView from '@/views/InstructorQuizzesView.vue'
import InstructorChalkboardView from '@/views/InstructorChalkboardView.vue'
import InstructorDashboardView from '@/views/InstructorDashboardView.vue'
import StudentQuizView from '@/views/StudentQuizView.vue'
import StudentScoreView from '@/views/StudentScoreView.vue'


const requireAuth = () => {
  return (from: any, to: any, next: any) => {
    const authStore = useAuthStore()
    if (authStore.username) {
      return next()
    } else {
      return next({ name: 'login' })
    }
  }
}
const requireStaff = () => {
  return (from: any, to: any, next: any) => {
    const authStore = useAuthStore()
    const userStore = useUserStore()
    if (authStore.username && userStore.isStaff) {
      return next()
    } else {
      return next({ name: 'login' })
    }
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    // views
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        title: `${SITE_TITLE} - Login`,
        hideNav: true
      }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: {
        title: `${SITE_TITLE} - Register`,
        hideNav: true
      }
    },
    {
      path: '/password/request',
      name: 'password-request',
      component: PasswordRequestView,
      meta: {
        title: `${SITE_TITLE} - Password Request`,
        hideNav: true
      }
    },
    {
      path: '/password/reset',
      name: 'password-reset',
      component: PasswordResetView,
      meta: {
        title: `${SITE_TITLE} - Password Reset`,
        hideNav: true
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: {
        title: `${SITE_TITLE} - Profile`,
      },
      beforeEnter: requireAuth()
    },

    // instructor
    {
      path: '/instructor/lessons',
      name: 'instructor-lessons',
      component: InstructorLessonsView,
      meta: {
        title: `${SITE_TITLE} - Lessons`,
      },
      beforeEnter: requireStaff()
    },
    {
      path: '/instructor/quizzes',
      name: 'instructor-quizzes',
      component: InstructorQuizzesView,
      meta: {
        title: `${SITE_TITLE} - Quizzes`,
      },
      beforeEnter: requireStaff()
    },
    {
      path: '/instructor/chalkboard',
      name: 'instructor-chalkboard',
      component: InstructorChalkboardView,
      meta: {
        title: `${SITE_TITLE} - Chalkboard`,
        hideNav: true,
        hideFooter: true,
      },
      beforeEnter: requireStaff()
    },
    {
      path: '/instructor/dashboard',
      name: 'instructor-dashboard',
      component: InstructorDashboardView,
      meta: {
        title: `${SITE_TITLE} - Dashboard`,
      },
      beforeEnter: requireStaff()
    },
    {
      path: '/student/quiz',
      name: 'student-quiz',
      component: StudentQuizView,
      meta: {
        title: `${SITE_TITLE} - Quiz`,
      },
      beforeEnter: requireAuth()
    },
    {
      path: '/student/score',
      name: 'student-score',
      component: StudentScoreView,
      meta: {
        title: `${SITE_TITLE} - Score`,
      },
      beforeEnter: requireAuth()
    },

    // fallback
    {
      path: '/',
      name: 'index',
      redirect: () => {
        const authStore = useAuthStore()
        const userStore = useUserStore()
        if (authStore.username) {
          if (userStore.isStaff) {
            return { name: 'instructor-dashboard' }
          } else {
            return { name: 'student-quiz' }
          }
        } else {
          return { name: 'login' }
        }
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'lost',
      component: LostView,
      meta: {
        title: `${SITE_TITLE}`,
        hideNav: true,
        hideFooter: true
      }
    }

  ],
})

router.afterEach((to) => {
  if (to.meta && to.meta.title) {
    document.title = to.meta.title as string
  } else {
    document.title = SITE_TITLE
  }
})

export default router
