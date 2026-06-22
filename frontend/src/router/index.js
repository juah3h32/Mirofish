import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import SlideReportView from '../views/SlideReportView.vue'
import GateView from '../views/GateView.vue'

const STORAGE_KEY = 'mf_access'

const routes = [
  {
    path: '/gate',
    name: 'Gate',
    component: GateView,
    meta: { public: true },
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true,
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true,
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true,
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true,
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true,
  },
  {
    path: '/slide-report',
    name: 'SlideReport',
    component: SlideReportView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.public) return true
  const isAuth = sessionStorage.getItem(STORAGE_KEY) === '1'
  if (!isAuth) {
    return { name: 'Gate', query: { redirect: to.fullPath } }
  }
})

export default router
