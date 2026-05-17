<template>
  <v-card class="mb-3">
    <v-card-title>Trámite #{{ tramite.id }}</v-card-title>
    <v-card-subtitle>{{ tramite.tipo?.nombre }}</v-card-subtitle>
    <v-card-text>
      <v-chip :color="coloresEstado[tramite.estado_actual]" size="small">
        {{ tramite.estado_actual }}
      </v-chip>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  tramite: { type: Object, required: true }
})

const coloresEstado = {
  pendiente:  'warning',
  en_proceso: 'info',
  devuelto:   'error',
  finalizado: 'success',
  cancelado:  'grey',
}
</script>