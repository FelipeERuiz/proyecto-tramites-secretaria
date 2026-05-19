<template>
  <div>
    <v-btn variant="text" prepend-icon="mdi-arrow-left" @click="$router.push({ name: 'FuncionarioDashboard' })" class="mb-4">
      Volver al panel
    </v-btn>

    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <template v-else-if="tramite">
      <!-- Encabezado -->
      <v-card class="mb-4 pa-4">
        <div class="d-flex align-center justify-space-between flex-wrap">
          <div>
            <h1 class="text-h5">Trámite #{{ tramite.id }}</h1>
            <p class="text-body-2 text-grey mt-1">{{ tramite.tipo?.nombre }}</p>
          </div>
          <v-chip :color="coloresEstado[tramite.estado_actual]" size="large">
            {{ tramite.estado_actual }}
          </v-chip>
        </div>

        <v-divider class="my-4" />

        <v-row dense>
          <v-col cols="12" sm="4">
            <p class="text-caption text-grey">Ciudadano</p>
            <p>{{ tramite.ciudadano?.nombre }} {{ tramite.ciudadano?.apellido }}</p>
            <p class="text-caption">DNI: {{ tramite.ciudadano?.dni }}</p>
          </v-col>
          <v-col cols="12" sm="4">
            <p class="text-caption text-grey">Fecha de inicio</p>
            <p>{{ tramite.fecha_inicio }}</p>
          </v-col>
          <v-col cols="12" sm="4">
            <p class="text-caption text-grey">Vencimiento</p>
            <p>{{ tramite.vencimiento || 'Sin vencimiento' }}</p>
          </v-col>
        </v-row>

        <div v-if="tramite.funcionario_asignado" class="mt-3">
          <p class="text-caption text-grey">Asignado a</p>
          <p>{{ tramite.funcionario_asignado.nombre }} {{ tramite.funcionario_asignado.apellido }}
            ({{ tramite.funcionario_asignado.area }})</p>
        </div>

        <div v-if="tramite.descripcion" class="mt-3">
          <p class="text-caption text-grey">Descripción</p>
          <p>{{ tramite.descripcion }}</p>
        </div>
      </v-card>

      <!-- Acciones del funcionario -->
      <v-card v-if="tramite.estado_actual !== 'finalizado' && tramite.estado_actual !== 'cancelado'" class="mb-4 pa-4">
        <h2 class="text-h6 mb-3">
          <v-icon start icon="mdi-cog" />
          Acciones
        </h2>
        <div class="d-flex flex-wrap gap-2">
          <v-btn
            color="info"
            prepend-icon="mdi-swap-horizontal"
            @click="dialogEstado = true"
          >
            Cambiar estado
          </v-btn>
          <v-btn
            color="warning"
            prepend-icon="mdi-arrow-left-circle"
            @click="dialogDevolucion = true"
          >
            Devolver al ciudadano
          </v-btn>
          <v-btn
            color="success"
            prepend-icon="mdi-gavel"
            @click="dialogResolucion = true"
          >
            Emitir resolución
          </v-btn>
        </div>
      </v-card>

      <!-- Historial de estados -->
      <v-card class="mb-4 pa-4">
        <h2 class="text-h6 mb-3">
          <v-icon start icon="mdi-history" />
          Historial de estados
        </h2>
        <v-timeline density="compact" side="end">
          <v-timeline-item
            v-for="estado in tramite.historial_estados"
            :key="estado.id"
            :dot-color="coloresEstado[estado.tipo_estado]"
            size="small"
          >
            <div>
              <v-chip :color="coloresEstado[estado.tipo_estado]" size="small" class="mb-1">
                {{ estado.tipo_estado }}
              </v-chip>
              <p class="text-body-2">{{ estado.motivo }}</p>
              <p class="text-caption text-grey">
                {{ formatFecha(estado.fecha_cambio) }}
                <span v-if="estado.funcionario">
                  — {{ estado.funcionario.nombre }} {{ estado.funcionario.apellido }}
                </span>
              </p>
            </div>
          </v-timeline-item>
        </v-timeline>
      </v-card>

      <!-- Resoluciones -->
      <v-card v-if="tramite.resoluciones?.length" class="mb-4 pa-4">
        <h2 class="text-h6 mb-3">
          <v-icon start icon="mdi-gavel" />
          Resoluciones
        </h2>
        <v-card
          v-for="res in tramite.resoluciones"
          :key="res.id"
          variant="outlined"
          class="mb-2 pa-3"
        >
          <p>{{ res.descripcion }}</p>
          <p class="text-caption text-grey mt-1">
            {{ res.fecha }} — {{ res.funcionario?.nombre }} {{ res.funcionario?.apellido }}
          </p>
        </v-card>
      </v-card>

      <!-- Comentarios -->
      <v-card class="pa-4">
        <h2 class="text-h6 mb-3">
          <v-icon start icon="mdi-comment-multiple" />
          Comentarios ({{ tramite.comentarios?.length || 0 }})
        </h2>

        <div v-if="!tramite.comentarios?.length" class="text-body-2 text-grey mb-4">
          Sin comentarios aún.
        </div>

        <div
          v-for="com in tramite.comentarios"
          :key="com.id"
          class="mb-3 pa-3 rounded-lg"
          :class="com.funcionario ? 'bg-blue-lighten-5' : 'bg-grey-lighten-4'"
        >
          <div class="d-flex align-center mb-1">
            <v-icon
              :icon="com.funcionario ? 'mdi-shield-account' : 'mdi-account'"
              size="small"
              class="mr-1"
            />
            <strong class="text-body-2">
              {{ com.funcionario
                  ? `${com.funcionario.nombre} ${com.funcionario.apellido}`
                  : `${com.ciudadano?.nombre} ${com.ciudadano?.apellido}` }}
            </strong>
            <v-spacer />
            <span class="text-caption text-grey">{{ formatFecha(com.fecha) }}</span>
          </div>
          <p class="text-body-2">{{ com.texto }}</p>
        </div>

        <v-divider class="my-4" />
        <div class="d-flex gap-2">
          <v-text-field
            v-model="nuevoComentario"
            label="Escribí un comentario..."
            density="compact"
            hide-details
            @keyup.enter="enviarComentario"
          />
          <v-btn
            color="primary"
            icon="mdi-send"
            :loading="enviandoComentario"
            @click="enviarComentario"
          />
        </div>
      </v-card>
    </template>

    <!-- Diálogo: Cambiar estado (CU03) -->
    <v-dialog v-model="dialogEstado" max-width="450">
      <v-card class="pa-4">
        <v-card-title>Cambiar estado del trámite</v-card-title>
        <v-card-text>
          <v-select
            v-model="nuevoEstado"
            :items="estadosDisponibles"
            label="Nuevo estado"
            prepend-inner-icon="mdi-swap-horizontal"
          />
          <v-textarea
            v-model="motivoEstado"
            label="Motivo del cambio"
            rows="3"
            class="mt-2"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogEstado = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="loadingAccion" @click="cambiarEstado">
            Confirmar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo: Devolución (CU10) -->
    <v-dialog v-model="dialogDevolucion" max-width="450">
      <v-card class="pa-4">
        <v-card-title>Devolver trámite al ciudadano</v-card-title>
        <v-card-text>
          <v-alert type="warning" variant="tonal" density="compact" class="mb-4">
            El trámite será devuelto al ciudadano. Indicá el motivo.
          </v-alert>
          <v-textarea
            v-model="motivoDevolucion"
            label="Motivo de la devolución (mínimo 10 caracteres)"
            rows="3"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogDevolucion = false">Cancelar</v-btn>
          <v-btn color="warning" :loading="loadingAccion" @click="devolverTramite">
            Devolver
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo: Resolución (CU11) -->
    <v-dialog v-model="dialogResolucion" max-width="500">
      <v-card class="pa-4">
        <v-card-title>Emitir resolución</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="descripcionResolucion"
            label="Descripción de la resolución (mínimo 10 caracteres)"
            rows="4"
          />
          <v-checkbox
            v-model="finalizarConResolucion"
            label="Finalizar el trámite con esta resolución"
            color="success"
            hide-details
            class="mt-2"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogResolucion = false">Cancelar</v-btn>
          <v-btn color="success" :loading="loadingAccion" @click="emitirResolucion">
            Emitir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route  = useRoute()
const router = useRouter()

const tramite            = ref(null)
const loading            = ref(false)
const loadingAccion      = ref(false)
const nuevoComentario    = ref('')
const enviandoComentario = ref(false)

const coloresEstado = {
  pendiente:  'warning',
  en_proceso: 'info',
  devuelto:   'error',
  finalizado: 'success',
  cancelado:  'grey',
}

const estadosDisponibles = computed(() => {
  const actual = tramite.value?.estado_actual
  const todos = [
    { title: 'Pendiente',  value: 'pendiente' },
    { title: 'En proceso', value: 'en_proceso' },
    { title: 'Finalizado', value: 'finalizado' },
    { title: 'Cancelado',  value: 'cancelado' },
  ]
  return todos.filter(e => e.value !== actual)
})

const formatFecha = (fecha) => {
  if (!fecha) return ''
  return new Date(fecha).toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

// ─── Cargar trámite ──────────────────────────────────────────────────
const cargarTramite = async () => {
  loading.value = true
  try {
    const { data } = await api.get(`/tramites/${route.params.id}/`)
    tramite.value = data
  } catch (err) {
    console.error('Error al cargar trámite:', err)
  } finally {
    loading.value = false
  }
}

// ─── CU03: Cambiar estado ────────────────────────────────────────────
const dialogEstado = ref(false)
const nuevoEstado  = ref(null)
const motivoEstado = ref('')

const cambiarEstado = async () => {
  if (!nuevoEstado.value) return
  loadingAccion.value = true
  try {
    await api.post(`/tramites/${tramite.value.id}/cambiar-estado/`, {
      tipo_estado: nuevoEstado.value,
      motivo: motivoEstado.value,
    })
    dialogEstado.value = false
    nuevoEstado.value = null
    motivoEstado.value = ''
    await cargarTramite()
  } catch (err) {
    console.error('Error al cambiar estado:', err)
  } finally {
    loadingAccion.value = false
  }
}

// ─── CU10: Devolución ────────────────────────────────────────────────
const dialogDevolucion  = ref(false)
const motivoDevolucion  = ref('')

const devolverTramite = async () => {
  if (motivoDevolucion.value.length < 10) return
  loadingAccion.value = true
  try {
    await api.post(`/tramites/${tramite.value.id}/devolver/`, {
      motivo: motivoDevolucion.value,
    })
    dialogDevolucion.value = false
    motivoDevolucion.value = ''
    await cargarTramite()
  } catch (err) {
    console.error('Error al devolver:', err)
  } finally {
    loadingAccion.value = false
  }
}

// ─── CU11: Resolución ───────────────────────────────────────────────
const dialogResolucion       = ref(false)
const descripcionResolucion  = ref('')
const finalizarConResolucion = ref(false)

const emitirResolucion = async () => {
  if (descripcionResolucion.value.length < 10) return
  loadingAccion.value = true
  try {
    await api.post(`/tramites/${tramite.value.id}/resoluciones/`, {
      descripcion: descripcionResolucion.value,
      finalizar: finalizarConResolucion.value,
    })
    dialogResolucion.value = false
    descripcionResolucion.value = ''
    finalizarConResolucion.value = false
    await cargarTramite()
  } catch (err) {
    console.error('Error al emitir resolución:', err)
  } finally {
    loadingAccion.value = false
  }
}

// ─── CU13: Comentarios ──────────────────────────────────────────────
const enviarComentario = async () => {
  if (!nuevoComentario.value.trim()) return
  enviandoComentario.value = true
  try {
    await api.post(`/tramites/${tramite.value.id}/comentarios/`, {
      texto: nuevoComentario.value,
    })
    nuevoComentario.value = ''
    await cargarTramite()
  } catch (err) {
    console.error('Error al enviar comentario:', err)
  } finally {
    enviandoComentario.value = false
  }
}

onMounted(cargarTramite)
</script>

<style scoped>
.gap-2 { gap: 8px; }
</style>