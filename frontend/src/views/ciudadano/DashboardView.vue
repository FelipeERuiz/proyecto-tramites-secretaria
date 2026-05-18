<template>
  <div>
    <v-btn variant="text" prepend-icon="mdi-arrow-left" :to="{ name: 'Dashboard' }" class="mb-4">
      Volver a mis trámites
    </v-btn>

    <v-card class="pa-6" max-width="600">
      <v-card-title class="text-h6 pb-4">
        <v-icon start icon="mdi-file-plus" />
        Nuevo Trámite
      </v-card-title>

      <v-card-text>
        <v-select
          v-model="form.tipo_id"
          :items="tipos"
          item-title="nombre"
          item-value="id"
          label="Tipo de trámite"
          prepend-inner-icon="mdi-folder-open"
          :error-messages="errors.tipo_id"
          :loading="loadingTipos"
        />

        <v-textarea
          v-model="form.descripcion"
          label="Descripción del trámite"
          prepend-inner-icon="mdi-text"
          :error-messages="errors.descripcion"
          rows="4"
          class="mt-2"
          placeholder="Describí el motivo de tu solicitud..."
        />

        <v-text-field
          v-model="form.vencimiento"
          label="Fecha de vencimiento (opcional)"
          type="date"
          prepend-inner-icon="mdi-calendar"
          class="mt-2"
        />

        <v-alert
          v-if="errorGeneral"
          type="error"
          variant="tonal"
          class="mt-4"
          density="compact"
        >
          {{ errorGeneral }}
        </v-alert>
      </v-card-text>

      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn variant="text" :to="{ name: 'Dashboard' }">Cancelar</v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          @click="registrarTramite"
          prepend-icon="mdi-send"
        >
          Registrar trámite
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()
const notify = inject('notify')

const tipos        = ref([])
const loadingTipos = ref(false)
const loading      = ref(false)
const errorGeneral = ref('')
const errors       = reactive({ tipo_id: '', descripcion: '' })

const form = reactive({
  tipo_id:     null,
  descripcion: '',
  vencimiento: '',
})

const cargarTipos = async () => {
  loadingTipos.value = true
  try {
    const { data } = await api.get('/tramites/tipos/')
    tipos.value = data
  } catch {
    errorGeneral.value = 'No se pudieron cargar los tipos de trámite.'
  } finally {
    loadingTipos.value = false
  }
}

const registrarTramite = async () => {
  errors.tipo_id = ''
  errors.descripcion = ''
  errorGeneral.value = ''

  if (!form.tipo_id)     { errors.tipo_id = 'Seleccioná un tipo de trámite'; return }
  if (!form.descripcion) { errors.descripcion = 'La descripción es obligatoria'; return }

  loading.value = true
  try {
    const payload = {
      tipo_id:     form.tipo_id,
      descripcion: form.descripcion,
    }
    if (form.vencimiento) payload.vencimiento = form.vencimiento

    await api.post('/tramites/', payload)
    notify('Trámite registrado exitosamente')
    router.push({ name: 'Dashboard' })
  } catch (err) {
    errorGeneral.value = err.response?.data?.error || 'Error al registrar el trámite.'
  } finally {
    loading.value = false
  }
}

onMounted(cargarTipos)
</script>