import { defineStore } from "pinia";
import api from "../services/api";

export const useAuthStore = defineStore("auth", {
  // ─── Estado ──────────────────────────────────────────────────────────
  state: () => ({
    user: null, // { id, username, rol, ciudadano, funcionario }
    accessToken: localStorage.getItem("access_token") || null,
    refreshToken: localStorage.getItem("refresh_token") || null,
  }),

  // ─── Getters (propiedades computadas) ────────────────────────────────
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    esCiudadano: (state) => state.user?.rol === "ciudadano",
    esFuncionario: (state) => state.user?.rol === "funcionario",
    nombreCompleto: (state) => {
      if (!state.user) return "";
      const perfil = state.user.ciudadano || state.user.funcionario;
      return perfil
        ? `${perfil.nombre} ${perfil.apellido}`
        : state.user.username;
    },
  },

  // ─── Acciones ────────────────────────────────────────────────────────
  actions: {
    /**
     * CU07 — Registrar inicio de sesión.
     * Envía credenciales, guarda tokens y carga el perfil.
     */
    async login(username, password) {
      const { data } = await api.post("/auth/login/", { username, password });

      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);

      // Cargar datos del usuario
      await this.cargarPerfil();
    },

    /**
     * Obtiene el perfil del usuario autenticado.
     */
    async cargarPerfil() {
      try {
        const { data } = await api.get("/usuarios/perfil/");
        this.user = data;
      } catch {
        this.logout();
      }
    },

    /**
     * Cierra la sesión limpiando todo.
     */
    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    },
  },
});
