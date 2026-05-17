<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4">

        <div class="text-center mb-6">
          <v-icon icon="mdi-bank" size="64" color="primary" />
          <h1 class="text-h5 mt-2">Sistema de Trámites</h1>
          <p class="text-body-2 text-grey">
            Secretaría de Industria y Promoción Económica
          </p>
        </div>

        <v-card class="pa-6">
          <v-card-title class="text-h6 text-center pb-4">
            Inicio de sesión
          </v-card-title>

          <v-card-text>
            <v-text-field
              v-model="username"
              label="Usuario"
              prepend-inner-icon="mdi-account"
              :error-messages="errors.username"
              @keyup.enter="login"
              autofocus
            />

            <v-text-field
              v-model="password"
              label="Contraseña"
              prepend-inner-icon="mdi-lock"
              :type="showPassword ? 'text' : 'password'"
              :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="showPassword = !showPassword"
              :error-messages="errors.password"
              @keyup.enter="login"
              class="mt-2"
            />

            <v-alert
              v-if="errorGeneral"
              type="error"
              variant="tonal"
              class="mt-2 mb-4"
              density="compact"
            >
              {{ errorGeneral }}
            </v-alert>

            <v-btn
              color="primary"
              size="large"
              block
              :loading="loading"
              @click="login"
              class="mt-4"
            >
              Ingresar
            </v-btn>
          </v-card-text>

          <v-card-actions class="justify-center">
            <v-btn
              variant="text"
              size="small"
              color="primary"
              @click="dialogRecuperar = true"
            >
              ¿Olvidaste tu contraseña?
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- CU06 — Diálogo de recuperar contraseña -->
    <v-dialog v-model="dialogRecuperar" max-width="400">
      <v-card class="pa-4">
        <v-card-title>Recuperar cuenta</v-card-title>
        <v-card-text>
          <p class="mb-4 text-body-2">
            Ingresá tu correo electrónico para recuperar tu cuenta.
          </p>
          <v-text-field
            v-model="emailRecuperar"
            label="Correo electrónico"
            prepend-inner-icon="mdi-email"
            type="email"
          />
          <v-alert
            v-if="mensajeRecuperar"
            type="info"
            variant="tonal"
            density="compact"
            class="mt-2"
          >
            {{ mensajeRecuperar }}
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogRecuperar = false">Cancelar</v-btn>
          <v-btn
            color="primary"
            :loading="loadingRecuperar"
            @click="recuperarSesion"
          >
            Buscar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const auth   = useAuthStore()
const router = useRouter()

// ─── Login ──────────────────────────────────────────────────────────
const username     = ref('')
const password     = ref('')
const showPassword = ref(false)
const loading      = ref(false)
const errorGeneral = ref('')
const errors       = reactive({ username: '', password: '' })

const login = async () => {
  // Limpiar errores
  errors.username = ''
  errors.password = ''
  errorGeneral.value = ''

  // Validar campos vacíos
  if (!username.value) { errors.username = 'El usuario es obligatorio'; return }
  if (!password.value) { errors.password = 'La contraseña es obligatoria'; return }

  loading.value = true
  try {
    await auth.login(username.value, password.value)
    // Redirigir según el rol
    if (auth.esFuncionario) {
      router.push({ name: 'FuncionarioDashboard' })
    } else {
      router.push({ name: 'Dashboard' })
    }
  } catch (err) {
    if (err.response?.status === 401) {
      errorGeneral.value = 'Usuario o contraseña incorrectos.'
    } else {
      errorGeneral.value = 'Error de conexión. Intentá de nuevo.'
    }
  } finally {
    loading.value = false
  }
}

// ─── CU06 — Recuperar sesión ────────────────────────────────────────
const dialogRecuperar  = ref(false)
const emailRecuperar   = ref('')
const mensajeRecuperar = ref('')
const loadingRecuperar = ref(false)

const recuperarSesion = async () => {
  loadingRecuperar.value = true
  mensajeRecuperar.value = ''
  try {
    const { data } = await api.post('/usuarios/recuperar-sesion/', {
      email: emailRecuperar.value
    })
    mensajeRecuperar.value = data.mensaje
  } catch {
    mensajeRecuperar.value = 'Si el correo está registrado, recibirás un enlace.'
  } finally {
    loadingRecuperar.value = false
  }
}
</script>