<template>
  <v-card class="mb-3 tramite-card" @click="$emit('click')" hover>
    <v-card-text class="d-flex align-center">
      <!-- Ícono según estado -->
      <v-avatar :color="coloresEstado[tramite.estado_actual]" size="42" class="mr-4">
        <v-icon :icon="iconosEstado[tramite.estado_actual]" color="white" />
      </v-avatar>

      <!-- Info principal -->
      <div class="flex-grow-1">
        <div class="d-flex align-center">
          <strong class="text-body-1">Trámite #{{ tramite.id }}</strong>
          <v-chip
            :color="coloresEstado[tramite.estado_actual]"
            size="small"
            class="ml-2"
          >
            {{ tramite.estado_actual }}
          </v-chip>
        </div>
        <p class="text-body-2 text-grey mt-1">{{ tramite.tipo?.nombre }}</p>
        <p class="text-caption text-grey">
          Iniciado: {{ tramite.fecha_inicio }}
          <span v-if="tramite.vencimiento"> · Vence: {{ tramite.vencimiento }}</span>
        </p>
      </div>

      <!-- Flecha -->
      <v-icon icon="mdi-chevron-right" color="grey" />
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  tramite: { type: Object, required: true }
})

defineEmits(['click'])

const coloresEstado = {
  pendiente:  'warning',
  en_proceso: 'info',
  devuelto:   'error',
  finalizado: 'success',
  cancelado:  'grey',
}

const iconosEstado = {
  pendiente:  'mdi-clock-outline',
  en_proceso: 'mdi-progress-wrench',
  devuelto:   'mdi-arrow-left-circle',
  finalizado: 'mdi-check-circle',
  cancelado:  'mdi-close-circle',
}
</script>

<style scoped>
.tramite-card {
  cursor: pointer;
  transition: transform 0.15s;
}
.tramite-card:hover {
  transform: translateX(4px);
}
</style>