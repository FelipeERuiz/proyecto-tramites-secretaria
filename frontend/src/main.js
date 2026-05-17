import { createApp } from 'vue'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'
import router from './router'
import App from './App.vue'

const app = createApp(App)

app.use(createPinia())    // Estado global (stores)
app.use(router)           // Navegación entre páginas
app.use(vuetify)          // Componentes de Material UI

app.mount('#app')