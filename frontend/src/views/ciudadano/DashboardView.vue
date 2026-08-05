<template>
  <div>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h5">Mis Trámites</h1>
        <p class="text-body-2 text-grey">Bienvenido/a, {{ auth.nombreCompleto }}</p>
      </div>
      <v-btn color="primary" prepend-icon="mdi-plus" :to="{ name: 'NuevoTramite' }">
        Nuevo trámite
      </v-btn>
    </div>

    <v-card class="mb-4 pa-4">
      <v-row dense>
        <v-col cols="12" sm="4">
          <v-select
            v-model="filtroEstado"
            :items="estados"
            label="Estado"
            clearable
            density="compact"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model="fechaDesde"
            label="Desde"
            type="date"
            density="compact"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model="fechaHasta"
            label="Hasta"
            type="date"
            density="compact"
          />
        </v-col>
      </v-row>
    </v-card>

    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <v-alert v-else-if="tramites.length === 0" type="info" variant="tonal">
      No tenés trámites registrados. ¡Creá uno nuevo!
    </v-alert>

    <div v-else>
      <TramiteCard
        v-for="tramite in tramites"
        :key="tramite.id"
        :tramite="tramite"
        @click="verDetalle(tramite.id)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../services/api'
import TramiteCard from '../../components/TramiteCard.vue'

const auth   = useAuthStore()
const router = useRouter()

const tramites    = ref([])
const loading     = ref(false)
const filtroEstado = ref(null)
const fechaDesde  = ref('')
const fechaHasta  = ref('')

const estados = [
  { title: 'Pendiente',  value: 'pendiente' },
  { title: 'En proceso', value: 'en_proceso' },
  { title: 'Devuelto',   value: 'devuelto' },
  { title: 'Finalizado', value: 'finalizado' },
  { title: 'Cancelado',  value: 'cancelado' },
]

const cargarTramites = async () => {
  loading.value = true
  try {
    const params = {}
    if (filtroEstado.value)  params.estado      = filtroEstado.value
    if (fechaDesde.value)    params.fecha_desde  = fechaDesde.value
    if (fechaHasta.value)    params.fecha_hasta  = fechaHasta.value

    const { data } = await api.get('/tramites/', { params })
    tramites.value = data
  } catch (err) {
    console.error('Error al cargar trámites:', err)
  } finally {
    loading.value = false
  }
}

const verDetalle = (id) => {
  router.push({ name: 'DetalleTramite', params: { id } })
}

onMounted(cargarTramites)
watch([filtroEstado, fechaDesde, fechaHasta], cargarTramites)
</script>