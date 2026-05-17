<template>
  <v-app>
    <NavBar v-if="auth.isAuthenticated" />

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <!-- Snackbar global para notificaciones -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { reactive, provide } from 'vue'
import { useAuthStore } from './stores/auth'
import NavBar from './components/NavBar.vue'

const auth = useAuthStore()

// Sistema de notificaciones global
const snackbar = reactive({ show: false, text: '', color: 'success' })

const notify = (text, color = 'success') => {
  snackbar.text  = text
  snackbar.color = color
  snackbar.show  = true
}

// Disponible en cualquier componente hijo con inject('notify')
provide('notify', notify)
</script>