<template>
  <div>
    <div class="mb-6">
      <h1 class="text-h5">Administración</h1>
      <p class="text-body-2 text-grey">Gestión de usuarios del sistema</p>
    </div>

    <v-card class="mb-4">
      <v-tabs v-model="tabActiva" color="primary" grow>
        <v-tab value="funcionarios">
          <v-icon start icon="mdi-shield-account" />
          Funcionarios
        </v-tab>
        <v-tab value="ciudadanos">
          <v-icon start icon="mdi-account-group" />
          Ciudadanos
        </v-tab>
      </v-tabs>
    </v-card>

    <div class="d-flex justify-end mb-4">
      <v-btn v-if="tabActiva === 'funcionarios'" color="primary" prepend-icon="mdi-account-plus" @click="dialogNuevoFuncionario = true">
        Nuevo funcionario
      </v-btn>
      <v-btn v-else color="primary" prepend-icon="mdi-account-plus" @click="dialogNuevoCiudadano = true">
        Nuevo ciudadano
      </v-btn>
    </div>

    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Tab Funcionarios -->
    <v-card v-else-if="tabActiva === 'funcionarios'">
      <v-table hover>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Área</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="funcionarios.length === 0">
            <td colspan="5" class="text-center text-grey pa-6">
              No hay funcionarios registrados.
            </td>
          </tr>
          <tr v-for="f in funcionarios" :key="f.id">
            <td>{{ f.nombre }} {{ f.apellido }}</td>
            <td>{{ f.email }}</td>
            <td>{{ f.area || '—' }}</td>
            <td>
              <v-chip :color="f.activo ? 'success' : 'error'" size="small">
                {{ f.activo ? 'Activo' : 'Inactivo' }}
              </v-chip>
            </td>
            <td>
              <v-btn v-if="f.activo" size="small" color="error" variant="text" icon="mdi-account-off" @click="confirmarBaja(f, 'funcionario')" />
              <v-btn v-else size="small" color="success" variant="text" icon="mdi-account-check" @click="reactivar(f, 'funcionario')" />
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <!-- Tab Ciudadanos -->
    <v-card v-else>
      <v-table hover>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>DNI</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="ciudadanos.length === 0">
            <td colspan="5" class="text-center text-grey pa-6">
              No hay ciudadanos registrados.
            </td>
          </tr>
          <tr v-for="c in ciudadanos" :key="c.id">
            <td>{{ c.nombre }} {{ c.apellido }}</td>
            <td>{{ c.dni }}</td>
            <td>{{ c.email }}</td>
            <td>{{ c.telefono || '—' }}</td>
            <td>
              <v-chip :color="c.activo !== false ? 'success' : 'error'" size="small">
                {{ c.activo !== false ? 'Activo' : 'Inactivo' }}
              </v-chip>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <!-- Diálogo Nuevo Funcionario -->
    <v-dialog v-model="dialogNuevoFuncionario" max-width="500">
      <v-card class="pa-4">
        <v-card-title>Registrar nuevo funcionario</v-card-title>
        <v-card-text>
          <v-row dense>
            <v-col cols="6"><v-text-field v-model="nuevoFunc.nombre" label="Nombre" /></v-col>
            <v-col cols="6"><v-text-field v-model="nuevoFunc.apellido" label="Apellido" /></v-col>
          </v-row>
          <v-text-field v-model="nuevoFunc.email" label="Email" type="email" />
          <v-text-field v-model="nuevoFunc.area" label="Área" />
          <v-text-field v-model="nuevoFunc.fecha_nacimiento" label="Fecha de nacimiento" type="date" />
          <v-text-field v-model="nuevoFunc.username" label="Nombre de usuario" />
          <v-text-field v-model="nuevoFunc.password" label="Contraseña" type="password" />
          <v-alert v-if="errorFunc" type="error" variant="tonal" density="compact">{{ errorFunc }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogNuevoFuncionario = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="loadingCrear" @click="crearFuncionario">Crear</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo Nuevo Ciudadano -->
    <v-dialog v-model="dialogNuevoCiudadano" max-width="500">
      <v-card class="pa-4">
        <v-card-title>Registrar nuevo ciudadano</v-card-title>
        <v-card-text>
          <v-row dense>
            <v-col cols="6"><v-text-field v-model="nuevoCiu.nombre" label="Nombre" /></v-col>
            <v-col cols="6"><v-text-field v-model="nuevoCiu.apellido" label="Apellido" /></v-col>
          </v-row>
          <v-text-field v-model="nuevoCiu.dni" label="DNI" type="number" />
          <v-text-field v-model="nuevoCiu.email" label="Email" type="email" />
          <v-text-field v-model="nuevoCiu.telefono" label="Teléfono (opcional)" />
          <v-text-field v-model="nuevoCiu.username" label="Nombre de usuario" />
          <v-text-field v-model="nuevoCiu.password" label="Contraseña" type="password" />
          <v-alert v-if="errorCiu" type="error" variant="tonal" density="compact">{{ errorCiu }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogNuevoCiudadano = false">Cancelar</v-btn>
          <v-btn color="primary" :loading="loadingCrear" @click="crearCiudadano">Crear</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo Confirmar Baja -->
    <v-dialog v-model="dialogBaja" max-width="400">
      <v-card class="pa-4">
        <v-card-title>Dar de baja</v-card-title>
        <v-card-text>
          ¿Confirmás la baja de <strong>{{ personaBaja?.nombre }} {{ personaBaja?.apellido }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogBaja = false">Cancelar</v-btn>
          <v-btn color="error" :loading="loadingBaja" @click="darDeBaja">Dar de baja</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import api from '../../services/api'

const tabActiva = ref('funcionarios')
const funcionarios = ref([])
const ciudadanos = ref([])
const loading = ref(false)
const loadingCrear = ref(false)
const loadingBaja = ref(false)
const dialogNuevoFuncionario = ref(false)
const dialogNuevoCiudadano = ref(false)
const dialogBaja = ref(false)
const personaBaja = ref(null)
const tipoBaja = ref('')
const errorFunc = ref('')
const errorCiu = ref('')

const nuevoFunc = reactive({
  nombre: '', apellido: '', email: '', area: '',
  fecha_nacimiento: '', username: '', password: '',
})

const nuevoCiu = reactive({
  nombre: '', apellido: '', dni: '', email: '',
  telefono: '', username: '', password: '',
})

const cargarFuncionarios = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/usuarios/funcionarios/')
    funcionarios.value = data
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

const cargarCiudadanos = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/usuarios/ciudadanos/')
    ciudadanos.value = data
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

const crearFuncionario = async () => {
  errorFunc.value = ''
  loadingCrear.value = true
  try {
    await api.post('/usuarios/registro-funcionario/', {
      ...nuevoFunc,
      password2: nuevoFunc.password,
    })
    dialogNuevoFuncionario.value = false
    Object.keys(nuevoFunc).forEach(k => nuevoFunc[k] = '')
    await cargarFuncionarios()
  } catch (err) {
    errorFunc.value = 'Error al crear el funcionario. Verificá los datos.'
  } finally {
    loadingCrear.value = false
  }
}

const crearCiudadano = async () => {
  errorCiu.value = ''
  loadingCrear.value = true
  try {
    await api.post('/usuarios/registro-ciudadano/', {
      ...nuevoCiu,
      dni: parseInt(nuevoCiu.dni),
      password2: nuevoCiu.password,
    })
    dialogNuevoCiudadano.value = false
    Object.keys(nuevoCiu).forEach(k => nuevoCiu[k] = '')
    await cargarCiudadanos()
  } catch (err) {
    errorCiu.value = 'Error al crear el ciudadano. Verificá los datos.'
  } finally {
    loadingCrear.value = false
  }
}

const confirmarBaja = (persona, tipo) => {
  personaBaja.value = persona
  tipoBaja.value = tipo
  dialogBaja.value = true
}

const darDeBaja = async () => {
  loadingBaja.value = true
  try {
    await api.post(`/usuarios/funcionarios/${personaBaja.value.id}/baja/`)
    dialogBaja.value = false
    await cargarFuncionarios()
  } catch (err) { console.error(err) }
  finally { loadingBaja.value = false }
}

const reactivar = async (persona, tipo) => {
  try {
    await api.post(`/usuarios/funcionarios/${persona.id}/reactivar/`)
    await cargarFuncionarios()
  } catch (err) { console.error(err) }
}

watch(tabActiva, (val) => {
  if (val === 'funcionarios') cargarFuncionarios()
  else cargarCiudadanos()
})

onMounted(cargarFuncionarios)
</script>