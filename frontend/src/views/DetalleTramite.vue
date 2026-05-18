<template>
  <div>
    <v-btn variant="text" prepend-icon="mdi-arrow-left" @click="$router.back()" class="mb-4">
      Volver
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
          <p class="text-caption text-grey">Funcionario asignado</p>
          <p>{{ tramite.funcionario_asignado.nombre }} {{ tramite.funcionario_asignado.apellido }}
            ({{ tramite.funcionario_asignado.area }})</p>
        </div>

        <div v-if="tramite.descripcion" class="mt-3">
          <p class="text-caption text-grey">Descripción</p>
          <p>{{ tramite.descripcion }}</p>
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
                  : `${com.ciudadano.nombre} ${com.ciudadano.apellido}` }}
            </strong>
            <v-spacer />
            <span class="text-caption text-grey">{{ formatFecha(com.fecha) }}</span>
          </div>
          <p class="text-body-2">{{ com.texto }}</p>
        </div>

        <!-- Formulario para nuevo comentario -->
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
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

const route  = useRoute()
const notify = inject('notify')

const tramite            = ref(null)
const loading            = ref(false)
const nuevoComentario    = ref('')
const enviandoComentario = ref(false)

const coloresEstado = {
  pendiente:  'warning',
  en_proceso: 'info',
  devuelto:   'error',
  finalizado: 'success',
  cancelado:  'grey',
}

const formatFecha = (fecha) => {
  if (!fecha) return ''
  return new Date(fecha).toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

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

const enviarComentario = async () => {
  if (!nuevoComentario.value.trim()) return

  enviandoComentario.value = true
  try {
    await api.post(`/tramites/${route.params.id}/comentarios/`, {
      texto: nuevoComentario.value
    })
    nuevoComentario.value = ''
    notify('Comentario enviado')
    await cargarTramite()
  } catch (err) {
    notify('Error al enviar comentario', 'error')
  } finally {
    enviandoComentario.value = false
  }
}

onMounted(cargarTramite)
</script>