<template>
  <div>
    <div class="d-flex align-center justify-space-between mb-6">
      <div>
        <h1 class="text-h5">Panel de Trámites</h1>
        <p class="text-body-2 text-grey">{{ auth.nombreCompleto }} — {{ auth.user?.funcionario?.area }}</p>
      </div>
    </div>

    <!-- Estadísticas rápidas -->
    <v-row class="mb-4">
      <v-col cols="6" sm="3" v-for="stat in estadisticas" :key="stat.label">
        <v-card class="pa-3 text-center" :color="stat.color" variant="tonal">
          <div class="text-h5 font-weight-bold">{{ stat.count }}</div>
          <div class="text-caption">{{ stat.label }}</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-card class="mb-4 pa-4">
      <v-row dense>
        <v-col cols="12" sm="3">
          <v-select
            v-model="filtroEstado"
            :items="estados"
            label="Estado"
            clearable
            density="compact"
          />
        </v-col>
        <v-col cols="12" sm="3">
          <v-text-field
            v-model="fechaDesde"
            label="Desde"
            type="date"
            density="compact"
          />
        </v-col>
        <v-col cols="12" sm="3">
          <v-text-field
            v-model="fechaHasta"
            label="Hasta"
            type="date"
            density="compact"
          />
        </v-col>
        <v-col cols="12" sm="3">
          <v-checkbox
            v-model="soloAsignados"
            label="Solo mis asignados"
            density="compact"
            hide-details
          />
        </v-col>
      </v-row>
    </v-card>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Tabla de trámites -->
    <v-card v-else>
      <v-table hover>
        <thead>
          <tr>
            <th>#</th>
            <th>Tipo</th>
            <th>Ciudadano</th>
            <th>Estado</th>
            <th>Fecha inicio</th>
            <th>Vencimiento</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="tramites.length === 0">
            <td colspan="7" class="text-center text-grey pa-6">
              No hay trámites que coincidan con los filtros.
            </td>
          </tr>
          <tr
            v-for="tramite in tramites"
            :key="tramite.id"
            class="cursor-pointer"
          >
            <td>{{ tramite.id }}</td>
            <td>{{ tramite.tipo?.nombre }}</td>
            <td>{{ tramite.ciudadano?.nombre }} {{ tramite.ciudadano?.apellido }}</td>
            <td>
              <v-chip :color="coloresEstado[tramite.estado_actual]" size="small">
                {{ tramite.estado_actual }}
              </v-chip>
            </td>
            <td>{{ tramite.fecha_inicio }}</td>
            <td>{{ tramite.vencimiento || '—' }}</td>
            <td>
              <v-btn
                size="small"
                color="primary"
                variant="text"
                icon="mdi-eye"
                @click="verTramite(tramite.id)"
              />
              <v-btn
                v-if="tramite.estado_actual === 'pendiente'"
                size="small"
                color="info"
                variant="text"
                icon="mdi-account-arrow-right"
                @click="abrirAsignar(tramite)"
              />
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <!-- Diálogo asignar trámite -->
    <v-dialog v-model="dialogAsignar" max-width="400">
      <v-card class="pa-4">
        <v-card-title>Asignar Trámite #{{ tramiteSeleccionado?.id }}</v-card-title>
        <v-card-text>
          <v-select
            v-model="funcionarioAsignar"
            :items="funcionarios"
            item-title="label"
            item-value="id"
            label="Funcionario"
            prepend-inner-icon="mdi-account"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogAsignar = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="loadingAsignar" @click="asignarTramite">
            Asignar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../services/api'

const auth   = useAuthStore()
const router = useRouter()

const tramites       = ref([])
const loading        = ref(false)
const filtroEstado   = ref(null)
const fechaDesde     = ref('')
const fechaHasta     = ref('')
const soloAsignados  = ref(false)

const estados = [
  { title: 'Pendiente',  value: 'pendiente' },
  { title: 'En proceso', value: 'en_proceso' },
  { title: 'Devuelto',   value: 'devuelto' },
  { title: 'Finalizado', value: 'finalizado' },
  { title: 'Cancelado',  value: 'cancelado' },
]

const coloresEstado = {
  pendiente:  'warning',
  en_proceso: 'info',
  devuelto:   'error',
  finalizado: 'success',
  cancelado:  'grey',
}

const estadisticas = computed(() => [
  { label: 'Pendientes',  count: tramites.value.filter(t => t.estado_actual === 'pendiente').length,  color: 'warning' },
  { label: 'En proceso',  count: tramites.value.filter(t => t.estado_actual === 'en_proceso').length, color: 'info' },
  { label: 'Devueltos',   count: tramites.value.filter(t => t.estado_actual === 'devuelto').length,   color: 'error' },
  { label: 'Finalizados', count: tramites.value.filter(t => t.estado_actual === 'finalizado').length, color: 'success' },
])

const cargarTramites = async () => {
  loading.value = true
  try {
    const params = {}
    if (filtroEstado.value)  params.estado      = filtroEstado.value
    if (fechaDesde.value)    params.fecha_desde  = fechaDesde.value
    if (fechaHasta.value)    params.fecha_hasta  = fechaHasta.value
    if (soloAsignados.value) params.asignados    = '1'

    const { data } = await api.get('/tramites/', { params })
    tramites.value = data
  } catch (err) {
    console.error('Error al cargar trámites:', err)
  } finally {
    loading.value = false
  }
}

const verTramite = (id) => {
  router.push({ name: 'GestionTramite', params: { id } })
}

// ─── Asignar trámite ────────────────────────────────────────────────
const dialogAsignar      = ref(false)
const tramiteSeleccionado = ref(null)
const funcionarioAsignar = ref(null)
const funcionarios       = ref([])
const loadingAsignar     = ref(false)

const abrirAsignar = (tramite) => {
  tramiteSeleccionado.value = tramite
  dialogAsignar.value = true
  cargarFuncionarios()
}

const cargarFuncionarios = async () => {
  try {
    const { data } = await api.get('/usuarios/funcionarios/')
    funcionarios.value = data.map(f => ({
      id: f.id,
      label: `${f.nombre} ${f.apellido} (${f.area || 'Sin área'})`
    }))
  } catch {
    const yo = auth.user?.funcionario
    if (yo) {
      funcionarios.value = [{ id: yo.id, label: `${yo.nombre} ${yo.apellido}` }]
    }
  }
}

const asignarTramite = async () => {
  if (!funcionarioAsignar.value) return
  loadingAsignar.value = true
  try {
    await api.post(`/tramites/${tramiteSeleccionado.value.id}/asignar/`, {
      funcionario_id: funcionarioAsignar.value
    })
    dialogAsignar.value = false
    await cargarTramites()
  } catch (err) {
    console.error('Error al asignar:', err)
  } finally {
    loadingAsignar.value = false
  }
}

onMounted(cargarTramites)
watch([filtroEstado, fechaDesde, fechaHasta, soloAsignados], cargarTramites)
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
</style>