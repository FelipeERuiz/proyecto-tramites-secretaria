<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="5">

        <div class="text-center mb-6">
          <v-icon icon="mdi-account-plus" size="64" color="primary" />
          <h1 class="text-h5 mt-2">Crear cuenta</h1>
          <p class="text-body-2 text-grey">
            Sistema de Trámites — Secretaría de Industria
          </p>
        </div>

        <v-card class="pa-6">
          <v-card-text>
            <v-btn-toggle v-model="tipoRegistro" mandatory color="primary" class="mb-4" style="width:100%">
              <v-btn value="ciudadano" style="flex:1">Ciudadano</v-btn>
              <v-btn value="funcionario" style="flex:1">Funcionario</v-btn>
            </v-btn-toggle>

            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model="form.nombre" label="Nombre" prepend-inner-icon="mdi-account" :error-messages="fieldError('nombre')" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="form.apellido" label="Apellido" :error-messages="fieldError('apellido')" />
              </v-col>
            </v-row>

            <template v-if="tipoRegistro === 'ciudadano'">
              <v-text-field v-model="form.dni" label="DNI" prepend-inner-icon="mdi-card-account-details" type="number" :error-messages="fieldError('dni')" />
              <v-text-field v-model="form.telefono" label="Teléfono (opcional)" prepend-inner-icon="mdi-phone" />
            </template>

            <template v-if="tipoRegistro === 'funcionario'">
              <v-text-field v-model="form.fecha_nacimiento" label="Fecha de nacimiento" prepend-inner-icon="mdi-calendar" type="date" :error-messages="fieldError('fecha_nacimiento')" />
              <v-text-field v-model="form.area" label="Área (opcional)" prepend-inner-icon="mdi-domain" />
            </template>

            <v-text-field v-model="form.email" label="Correo electrónico" prepend-inner-icon="mdi-email" type="email" :error-messages="fieldError('email')" />
            <v-text-field v-model="form.username" label="Nombre de usuario" prepend-inner-icon="mdi-account-circle" :error-messages="fieldError('username')" />
            <v-text-field v-model="form.password" label="Contraseña" prepend-inner-icon="mdi-lock" :type="showPassword ? 'text' : 'password'" :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'" @click:append-inner="showPassword = !showPassword" :error-messages="fieldError('password')" />
            <v-text-field v-model="form.password2" label="Repetir contraseña" prepend-inner-icon="mdi-lock-check" :type="showPassword ? 'text' : 'password'" :error-messages="fieldError('password2')" @keyup.enter="registrar" />

            <v-alert v-if="exito" type="success" variant="tonal" class="mt-2" density="compact">
              ¡Cuenta creada exitosamente! Redirigiendo al login...
            </v-alert>

            <v-alert v-if="errorGeneral" type="error" variant="tonal" class="mt-2" density="compact">
              {{ errorGeneral }}
            </v-alert>

            <v-btn color="primary" size="large" block :loading="loading" :disabled="exito" @click="registrar" class="mt-4">
              Crear cuenta
            </v-btn>
          </v-card-text>

          <v-card-actions class="justify-center">
            <v-btn variant="text" size="small" color="primary" @click="$router.push({ name: 'Login' })">
              ¿Ya tenés cuenta? Iniciá sesión
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../services/api'

const tipoRegistro = ref('ciudadano')
const showPassword = ref(false)
const loading      = ref(false)
const exito        = ref(false)
const errorGeneral = ref('')
const errores      = ref({})

const form = reactive({
  nombre: '', apellido: '', email: '', username: '', password: '', password2: '',
  dni: '', telefono: '',
  fecha_nacimiento: '', area: '',
})

const fieldError = (field) => {
  if (errores.value[field]) {
    return Array.isArray(errores.value[field]) ? errores.value[field][0] : errores.value[field]
  }
  return ''
}

const registrar = async () => {
  errorGeneral.value = ''
  errores.value = {}

  if (!form.nombre)   { errores.value.nombre = ['El nombre es obligatorio']; return }
  if (!form.apellido) { errores.value.apellido = ['El apellido es obligatorio']; return }
  if (!form.email)    { errores.value.email = ['El email es obligatorio']; return }
  if (!form.username) { errores.value.username = ['El usuario es obligatorio']; return }
  if (!form.password) { errores.value.password = ['La contraseña es obligatoria']; return }
  if (form.password !== form.password2) { errores.value.password2 = ['Las contraseñas no coinciden']; return }

  if (tipoRegistro.value === 'ciudadano' && !form.dni) {
    errores.value.dni = ['El DNI es obligatorio']; return
  }
  if (tipoRegistro.value === 'funcionario' && !form.fecha_nacimiento) {
    errores.value.fecha_nacimiento = ['La fecha de nacimiento es obligatoria']; return
  }

  loading.value = true
  try {
    const endpoint = tipoRegistro.value === 'ciudadano'
      ? '/usuarios/registro-ciudadano/'
      : '/usuarios/registro-funcionario/'

    const payload = {
      nombre: form.nombre, apellido: form.apellido,
      email: form.email, username: form.username,
      password: form.password, password2: form.password2,
    }

    if (tipoRegistro.value === 'ciudadano') {
      payload.dni = parseInt(form.dni)
      payload.telefono = form.telefono
    } else {
      payload.fecha_nacimiento = form.fecha_nacimiento
      payload.area = form.area
    }

    await api.post(endpoint, payload)
    exito.value = true
    setTimeout(() => { window.location.href = '/login' }, 2000)
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      errores.value = err.response.data
    } else {
      errorGeneral.value = 'Error de conexión.'
    }
  } finally {
    loading.value = false
  }
}
</script>