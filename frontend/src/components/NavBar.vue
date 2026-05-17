<template>
  <v-app-bar color="primary" elevation="2">
    <v-app-bar-title>
      <v-icon icon="mdi-bank" class="mr-2" />
      Secretaría de Industria
    </v-app-bar-title>

    <template v-slot:append>
      <v-chip class="mr-3" variant="tonal" color="white">
        <v-icon start :icon="auth.esFuncionario ? 'mdi-shield-account' : 'mdi-account'" />
        {{ auth.nombreCompleto }}
        <span class="ml-1 text-caption">({{ auth.user?.rol }})</span>
      </v-chip>

      <v-btn icon="mdi-logout" @click="cerrarSesion" />
    </template>
  </v-app-bar>

  <!-- Menú lateral -->
  <v-navigation-drawer v-model="drawer" app>
    <v-list nav>
      <!-- Menú Ciudadano -->
      <template v-if="auth.esCiudadano">
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Mis trámites"
          :to="{ name: 'Dashboard' }"
        />
        <v-list-item
          prepend-icon="mdi-plus-circle"
          title="Nuevo trámite"
          :to="{ name: 'NuevoTramite' }"
        />
      </template>

      <!-- Menú Funcionario -->
      <template v-if="auth.esFuncionario">
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Panel de trámites"
          :to="{ name: 'FuncionarioDashboard' }"
        />
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth   = useAuthStore()
const router = useRouter()
const drawer = ref(true)

const cerrarSesion = () => {
  auth.logout()
  router.push({ name: 'Login' })
}
</script>