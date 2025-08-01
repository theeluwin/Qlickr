// vue
import { createApp } from 'vue'
import { createPinia } from 'pinia'

// vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// styles
import '@/assets/custom.css'

// components
import App from '@/App.vue'
import router from '@/router'
import { setHttpUnauthorizedHandler } from '@/http'


// init vuetify
const vuetify = createVuetify({
  components,
  directives,
})

// init http
setHttpUnauthorizedHandler(() => {
  router.push({ name: 'login' })
})

// init app
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.mount('#app')
