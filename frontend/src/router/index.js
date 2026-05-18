import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LoginView.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/",
    redirect: "/dashboard",
  },
  // ─── Rutas de Ciudadano ───────────────────────────────────────────
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("../views/ciudadano/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/tramites/nuevo",
    name: "NuevoTramite",
    component: () => import("../views/ciudadano/NuevoTramiteView.vue"),
    meta: { requiresAuth: true, rol: "ciudadano" },
  },
  // ─── Rutas de Funcionario ─────────────────────────────────────────
  {
    path: "/funcionario",
    name: "FuncionarioDashboard",
    component: () => import("../views/funcionario/DashboardView.vue"),
    meta: { requiresAuth: true, rol: "funcionario" },
  },
  {
    path: "/funcionario/tramite/:id",
    name: "GestionTramite",
    component: () => import("../views/funcionario/GestionTramite.vue"),
    meta: { requiresAuth: true, rol: "funcionario" },
    props: true,
  },
  // ─── Ruta compartida ──────────────────────────────────────────────
  {
    path: "/tramites/:id",
    name: "DetalleTramite",
    component: () => import("../views/DetalleTramite.vue"),
    meta: { requiresAuth: true },
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// ─── Guardia de navegación ──────────────────────────────────────────────
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();

  // Si la ruta requiere auth y no hay token → ir a login
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: "Login" });
  }

  // Si estamos autenticados pero no tenemos datos del usuario → cargarlos
  if (auth.isAuthenticated && !auth.user) {
    await auth.cargarPerfil();
  }

  // Si la ruta tiene un rol específico y el usuario no lo tiene → redirigir
  if (to.meta.rol && auth.user?.rol !== to.meta.rol) {
    if (auth.user?.rol === "ciudadano") return next({ name: "Dashboard" });
    if (auth.user?.rol === "funcionario")
      return next({ name: "FuncionarioDashboard" });
  }

  // Si ya está logueado y va a /login → redirigir al dashboard
  if (to.name === "Login" && auth.isAuthenticated) {
    if (auth.user?.rol === "funcionario")
      return next({ name: "FuncionarioDashboard" });
    return next({ name: "Dashboard" });
  }

  next();
});

export default router;
