<template>
  <div class="slide-builder">
    <!-- Toolbar -->
    <div class="sb-toolbar">
      <button class="sb-btn-toggle" @click="showForm = !showForm">
        {{ showForm ? '◀ Ocultar' : '▶ Editar Datos' }}
      </button>
      <span class="sb-toolbar-title">Constructor de Reporte de Mercado</span>
      <button class="sb-btn-pdf" @click="downloadPdf" :disabled="downloading">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        {{ downloading ? 'Generando...' : 'Descargar PDF' }}
      </button>
    </div>

    <div class="sb-body">
      <!-- Form Sidebar -->
      <div class="sb-form" v-show="showForm">
        <div class="sb-form-inner">
          <!-- ENCABEZADO -->
          <div class="sf-section">
            <div class="sf-section-header" @click="toggleSection('meta')">
              <span>Encabezado</span>
              <span>{{ openSections.has('meta') ? '▲' : '▼' }}</span>
            </div>
            <div class="sf-section-body" v-show="openSections.has('meta')">
              <label>Supertítulo</label>
              <input v-model="report.meta.supertitle" />
              <label>Empresa</label>
              <input v-model="report.meta.company" />
              <label>Subtag empresa</label>
              <input v-model="report.meta.companyTag" />
              <label>Título principal</label>
              <input v-model="report.meta.title" />
              <label>Número de reporte</label>
              <input v-model="report.meta.reportNum" />
              <label>Fecha</label>
              <input v-model="report.meta.reportDate" />
              <label>Confidencialidad</label>
              <input v-model="report.meta.confidential" />
            </div>
          </div>

          <!-- KPIs -->
          <div class="sf-section">
            <div class="sf-section-header" @click="toggleSection('kpis')">
              <span>KPIs</span>
              <span>{{ openSections.has('kpis') ? '▲' : '▼' }}</span>
            </div>
            <div class="sf-section-body" v-show="openSections.has('kpis')">
              <div v-for="(kpi, i) in report.kpis" :key="i" class="sf-kpi-group">
                <div class="sf-group-title">KPI {{ i + 1 }}</div>
                <label>Etiqueta</label>
                <input v-model="kpi.label" />
                <label>Valor</label>
                <input v-model="kpi.value" />
                <label>Unidad</label>
                <input v-model="kpi.unit" />
                <label>Nota</label>
                <input v-model="kpi.note" />
                <label>Tema (default / green / red)</label>
                <select v-model="kpi.theme">
                  <option value="default">Default</option>
                  <option value="green">Verde oscuro</option>
                  <option value="red">Rojo/Terracota</option>
                </select>
              </div>
            </div>
          </div>

          <!-- PANEL 01 -->
          <div class="sf-section">
            <div class="sf-section-header" @click="toggleSection('p1')">
              <span>Panel 01 · Panorama Competitivo</span>
              <span>{{ openSections.has('p1') ? '▲' : '▼' }}</span>
            </div>
            <div class="sf-section-body" v-show="openSections.has('p1')">
              <label>Título</label>
              <input v-model="report.p1.title" />
              <label>Categorías del gráfico (separadas por coma)</label>
              <input :value="report.p1.cats.join(', ')" @input="e => report.p1.cats = e.target.value.split(',').map(s=>s.trim())" />
              <div v-for="(ser, si) in report.p1.series" :key="si">
                <div class="sf-group-title">Serie: {{ ser.name }}</div>
                <label>Nombre</label>
                <input v-model="ser.name" />
                <label>Valores (uno por categoría, separados por coma)</label>
                <input :value="ser.values.join(', ')" @input="e => ser.values = e.target.value.split(',').map(s=>parseInt(s.trim())||0)" />
              </div>
              <label>Texto de posicionamiento</label>
              <input v-model="report.p1.posText" />
              <label>Precio de posicionamiento</label>
              <input v-model="report.p1.posValue" />
              <label>Unidad de precio</label>
              <input v-model="report.p1.posUnit" />
              <label>Nota de pie</label>
              <textarea v-model="report.p1.footer" rows="2"></textarea>
            </div>
          </div>

          <!-- PANEL 02 -->
          <div class="sf-section">
            <div class="sf-section-header" @click="toggleSection('p2')">
              <span>Panel 02 · Consumidor y Demanda</span>
              <span>{{ openSections.has('p2') ? '▲' : '▼' }}</span>
            </div>
            <div class="sf-section-body" v-show="openSections.has('p2')">
              <label>Título</label>
              <input v-model="report.p2.title" />
              <div class="sf-group-title">Factores de Decisión</div>
              <div v-for="(f, i) in report.p2.factores" :key="i" class="sf-inline">
                <input v-model="f.name" style="flex:2" placeholder="Nombre" />
                <input v-model.number="f.val" style="flex:1" type="number" placeholder="Val" />
                <label style="flex:1;font-size:10px">↑ Trend
                  <input type="checkbox" v-model="f.up" />
                </label>
              </div>
              <div class="sf-group-title">Apertura a Alternativas</div>
              <label>% Abiertos</label>
              <input v-model.number="report.p2.aperturaPct" type="number" />
              <div v-for="(seg, i) in report.p2.aperturaSeg" :key="i" class="sf-inline">
                <input v-model="seg.label" style="flex:2" placeholder="Etiqueta" />
                <input v-model.number="seg.pct" style="flex:1" type="number" placeholder="%" />
              </div>
              <div class="sf-group-title">Sectores Ancla</div>
              <div v-for="(s, i) in report.p2.sectores" :key="i" class="sf-inline">
                <input v-model="s.name" style="flex:2" placeholder="Sector" />
                <input v-model.number="s.val" style="flex:1" type="number" placeholder="Val" />
              </div>
              <label>Nota de pie</label>
              <textarea v-model="report.p2.footer" rows="2"></textarea>
            </div>
          </div>

          <!-- PANEL 03 -->
          <div class="sf-section">
            <div class="sf-section-header" @click="toggleSection('p3')">
              <span>Panel 03 · Política y Riesgos</span>
              <span>{{ openSections.has('p3') ? '▲' : '▼' }}</span>
            </div>
            <div class="sf-section-body" v-show="openSections.has('p3')">
              <label>Título</label>
              <input v-model="report.p3.title" />
              <div class="sf-group-title">Timeline</div>
              <div v-for="(t, i) in report.p3.timeline" :key="i">
                <label>Período {{ i + 1 }}</label>
                <input v-model="t.period" placeholder="Ej: T0 · HOY" />
                <input v-model="t.title" placeholder="Título" />
                <input v-model="t.desc" placeholder="Descripción" />
              </div>
              <div class="sf-group-title">Matriz de Riesgos/Oportunidades</div>
              <div v-for="(m, i) in report.p3.matrix" :key="i">
                <label>Item {{ i + 1 }}</label>
                <select v-model="m.type">
                  <option value="RIESGO">RIESGO</option>
                  <option value="OPORTUNIDAD">OPORTUNIDAD</option>
                </select>
                <input v-model="m.title" placeholder="Título" />
                <textarea v-model="m.desc" rows="2"></textarea>
              </div>
              <label>Nota de pie</label>
              <textarea v-model="report.p3.footer" rows="2"></textarea>
            </div>
          </div>

          <!-- CITAS -->
          <div class="sf-section">
            <div class="sf-section-header" @click="toggleSection('quotes')">
              <span>Citas</span>
              <span>{{ openSections.has('quotes') ? '▲' : '▼' }}</span>
            </div>
            <div class="sf-section-body" v-show="openSections.has('quotes')">
              <div v-for="(q, i) in report.quotes" :key="i">
                <div class="sf-group-title">Cita {{ i + 1 }}</div>
                <label>Fuente</label>
                <input v-model="q.src" />
                <label>Texto</label>
                <textarea v-model="q.text" rows="2"></textarea>
                <label>Destacar fuente
                  <input type="checkbox" v-model="q.accent" />
                </label>
              </div>
            </div>
          </div>

          <!-- BOTTOM -->
          <div class="sf-section">
            <div class="sf-section-header" @click="toggleSection('bottom')">
              <span>Postura y Acciones</span>
              <span>{{ openSections.has('bottom') ? '▲' : '▼' }}</span>
            </div>
            <div class="sf-section-body" v-show="openSections.has('bottom')">
              <label>Postura recomendada</label>
              <textarea v-model="report.bottom.postTitle" rows="3"></textarea>
              <div v-for="(a, i) in report.bottom.actions" :key="i">
                <div class="sf-group-title">Acción {{ a.num }} · {{ a.lbl }}</div>
                <label>Categoría</label>
                <input v-model="a.lbl" />
                <label>Título</label>
                <input v-model="a.title" />
                <label>Descripción</label>
                <textarea v-model="a.desc" rows="2"></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Slide Preview -->
      <div class="sb-preview" ref="previewArea">
        <div class="sb-slide-wrapper" :style="wrapperStyle">
          <!-- ========================== THE SLIDE ========================== -->
          <div class="s-slide" ref="slideRef">

            <!-- SUPERTITLE -->
            <div class="s-supertitle">{{ report.meta.supertitle }}</div>

            <!-- HEADER -->
            <div class="s-header">
              <div class="s-header-left">
                <div class="s-logo">
                  <svg viewBox="0 0 16 16" width="16" height="16"><polygon points="8,0 16,8 8,16 0,8" fill="#1A1A1A"/></svg>
                  <div class="s-logo-text">
                    <span class="s-logo-company">{{ report.meta.company }}</span>
                    <span class="s-logo-tag">{{ report.meta.companyTag }}</span>
                  </div>
                </div>
              </div>
              <div class="s-header-center">
                <h1 class="s-main-title">{{ report.meta.title }}</h1>
              </div>
              <div class="s-header-right">
                <span class="s-rep-num">{{ report.meta.reportNum }}</span>
                <span class="s-rep-date">{{ report.meta.reportDate }}</span>
                <span class="s-rep-conf">{{ report.meta.confidential }}</span>
              </div>
            </div>
            <div class="s-header-rule"></div>

            <!-- KPI CARDS -->
            <div class="s-kpis">
              <div
                v-for="(kpi, i) in report.kpis"
                :key="i"
                class="s-kpi"
                :class="`s-kpi--${kpi.theme}`"
              >
                <span class="s-kpi-label">{{ kpi.label }}</span>
                <div class="s-kpi-value-row">
                  <span class="s-kpi-value">{{ kpi.value }}</span>
                  <span class="s-kpi-unit" v-if="kpi.unit">{{ kpi.unit }}</span>
                </div>
                <span class="s-kpi-note">{{ kpi.note }}</span>
              </div>
            </div>

            <!-- THREE PANELS -->
            <div class="s-panels">

              <!-- PANEL 01 -->
              <div class="s-panel">
                <span class="s-panel-label">{{ report.p1.secLabel }}</span>
                <h2 class="s-panel-title">{{ report.p1.title }}</h2>

                <!-- Grouped Bar Chart -->
                <svg class="s-barchart" :viewBox="`0 0 ${barData.totalW} 140`" preserveAspectRatio="xMidYMid meet">
                  <!-- Baseline -->
                  <line :x1="0" :y1="barData.baseY" :x2="barData.totalW" :y2="barData.baseY" stroke="#CCCCCC" stroke-width="0.5"/>
                  <!-- Bars -->
                  <rect
                    v-for="(b, bi) in barData.bars"
                    :key="bi"
                    :x="b.x" :y="b.y" :width="b.w" :height="b.h" :fill="b.color"
                  />
                  <!-- Category Labels -->
                  <text
                    v-for="(cat, ci) in report.p1.cats"
                    :key="'cl'+ci"
                    :x="ci * barData.groupW + barData.groupW / 2"
                    :y="barData.baseY + 14"
                    text-anchor="middle"
                    font-size="7.5"
                    font-family="Inter, sans-serif"
                    fill="#777"
                    font-weight="600"
                    letter-spacing="0.3"
                  >{{ cat }}</text>
                </svg>

                <!-- Legend -->
                <div class="s-chart-legend">
                  <div v-for="(ser, si) in report.p1.series" :key="si" class="s-legend-item">
                    <span class="s-legend-dot" :style="{background: ser.color}"></span>
                    <span class="s-legend-label">{{ ser.name }}</span>
                  </div>
                </div>

                <!-- Positioning Box -->
                <div class="s-pos-box">
                  <div class="s-pos-box-top">
                    <span class="s-pos-box-label">{{ report.p1.posLabel }}</span>
                  </div>
                  <div class="s-pos-box-bottom">
                    <span class="s-pos-box-text">{{ report.p1.posText }}</span>
                    <div class="s-pos-box-price">
                      <span class="s-pos-box-value">{{ report.p1.posValue }}</span>
                      <span class="s-pos-box-unit">{{ report.p1.posUnit }}</span>
                    </div>
                  </div>
                </div>

                <p class="s-panel-footer">{{ report.p1.footer }}</p>
              </div>

              <!-- PANEL 02 -->
              <div class="s-panel s-panel--mid">
                <span class="s-panel-label">{{ report.p2.secLabel }}</span>
                <h2 class="s-panel-title">{{ report.p2.title }}</h2>

                <!-- Factores label -->
                <span class="s-chart-label">{{ report.p2.factoresLabel }}</span>

                <!-- Factores Horizontal Bars -->
                <svg class="s-hbarchart" viewBox="0 0 260 98" preserveAspectRatio="xMidYMid meet">
                  <g v-for="(f, i) in report.p2.factores" :key="i">
                    <text x="0" :y="i * 18 + 11" font-size="9" font-family="Inter, sans-serif" fill="#1A1A1A">{{ f.name }}</text>
                    <rect :x="78" :y="i * 18 + 2" :width="(f.val / 100) * 158" height="9" fill="#1A1A1A" rx="0.5"/>
                    <text :x="242" :y="i * 18 + 11" font-size="9" font-family="Inter, sans-serif" fill="#1A1A1A" text-anchor="end">
                      {{ f.val }}{{ f.up ? ' ▲' : '' }}
                    </text>
                  </g>
                </svg>

                <!-- Apertura row -->
                <div class="s-apertura-row">
                  <div class="s-apertura-left">
                    <span class="s-chart-label">{{ report.p2.aperturaLabel }}</span>
                    <!-- Donut -->
                    <div class="s-donut-wrap">
                      <svg viewBox="0 0 84 84" width="80" height="80">
                        <path v-for="(seg, i) in donutPaths" :key="i" :d="seg.path" :fill="seg.color"/>
                        <text x="42" y="39" text-anchor="middle" font-size="13" font-weight="700" font-family="Inter, sans-serif" fill="#1A1A1A">{{ report.p2.aperturaPct }}%</text>
                        <text x="42" y="51" text-anchor="middle" font-size="7" font-family="Inter, sans-serif" fill="#555">ABIERTOS</text>
                      </svg>
                    </div>
                    <!-- Legend -->
                    <div class="s-donut-legend">
                      <div v-for="(seg, i) in report.p2.aperturaSeg" :key="i" class="s-donut-leg-item">
                        <span class="s-donut-leg-dot" :style="{background: seg.color}"></span>
                        <span class="s-donut-leg-label">{{ seg.label }}</span>
                        <span class="s-donut-leg-pct">{{ seg.pct }}%</span>
                      </div>
                    </div>
                  </div>

                  <div class="s-apertura-right">
                    <span class="s-chart-label">{{ report.p2.sectoresLabel }}</span>
                    <svg viewBox="0 0 148 96" preserveAspectRatio="xMidYMid meet" style="width:100%;max-width:148px">
                      <g v-for="(s, i) in report.p2.sectores" :key="i">
                        <text x="0" :y="i * 18 + 11" font-size="8.5" font-family="Inter, sans-serif" fill="#1A1A1A">{{ s.name }}</text>
                        <rect :x="0" :y="i * 18 + 14" :width="(s.val / 100) * 120" height="5" fill="#1A1A1A" rx="0.5"/>
                        <text :x="126" :y="i * 18 + 19" font-size="8.5" font-family="Inter, sans-serif" fill="#1A1A1A" text-anchor="end" font-weight="600">{{ s.val }}</text>
                      </g>
                    </svg>
                  </div>
                </div>

                <p class="s-panel-footer">{{ report.p2.footer }}</p>
              </div>

              <!-- PANEL 03 -->
              <div class="s-panel">
                <span class="s-panel-label">{{ report.p3.secLabel }}</span>
                <h2 class="s-panel-title">{{ report.p3.title }}</h2>

                <!-- Timeline -->
                <div class="s-timeline">
                  <div v-for="(t, i) in report.p3.timeline" :key="i" class="s-timeline-item">
                    <span class="s-timeline-period">{{ t.period }}</span>
                    <div class="s-timeline-dot"></div>
                    <div class="s-timeline-content">
                      <span class="s-timeline-title">{{ t.title }}</span>
                      <span class="s-timeline-desc">{{ t.desc }}</span>
                    </div>
                  </div>
                </div>

                <!-- Matrix 2x2 -->
                <div class="s-matrix">
                  <div v-for="(m, i) in report.p3.matrix" :key="i" class="s-matrix-item" :class="m.type === 'RIESGO' ? 's-matrix-risk' : 's-matrix-opp'">
                    <div class="s-matrix-tag">
                      <span class="s-matrix-dot" :class="m.type === 'RIESGO' ? 's-dot-risk' : 's-dot-opp'"></span>
                      <span class="s-matrix-type">{{ m.type }}</span>
                    </div>
                    <span class="s-matrix-title">{{ m.title }}</span>
                    <p class="s-matrix-desc">{{ m.desc }}</p>
                  </div>
                </div>

                <p class="s-panel-footer">{{ report.p3.footer }}</p>
              </div>
            </div>

            <!-- QUOTES -->
            <div class="s-quotes">
              <div v-for="(q, i) in report.quotes" :key="i" class="s-quote" :class="{'s-quote--accent': q.accent}">
                <span class="s-quote-src" :class="{'s-quote-src--accent': q.accent}">{{ q.src }}</span>
                <p class="s-quote-text">{{ q.text }}</p>
              </div>
            </div>

            <!-- BOTTOM -->
            <div class="s-bottom">
              <div class="s-postura">
                <span class="s-postura-label">{{ report.bottom.postLabel }}</span>
                <h2 class="s-postura-title" v-html="report.bottom.postTitle.replace(/\n/g, '<br>')"></h2>
              </div>
              <div v-for="(a, i) in report.bottom.actions" :key="i" class="s-action">
                <div class="s-action-header">
                  <span class="s-action-num">{{ a.num }}</span>
                  <span class="s-action-lbl">· {{ a.lbl }}</span>
                </div>
                <span class="s-action-title">{{ a.title }}</span>
                <p class="s-action-desc">{{ a.desc }}</p>
              </div>
            </div>

          </div>
          <!-- ======================== END SLIDE ========================= -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const showForm = ref(false)
const downloading = ref(false)
const slideRef = ref(null)
const previewArea = ref(null)
const slideScale = ref(0.6)
const openSections = reactive(new Set(['meta']))

const toggleSection = (key) => {
  if (openSections.has(key)) openSections.delete(key)
  else openSections.add(key)
}

const SLIDE_W = 1440
const SLIDE_H = 810

const report = reactive({
  meta: {
    supertitle: 'REPORTE · PRONÓSTICO 18 MESES',
    company: 'GRUPO ORTIZ GO',
    companyTag: 'INTELIGENCIA DE MERCADO',
    title: 'Mercado de Bolsas de Plástico · México',
    reportNum: 'R-2026.03',
    reportDate: 'MAYO 2026',
    confidential: 'CONFIDENCIAL',
  },
  kpis: [
    { label: 'HORIZONTE', value: '18', unit: 'meses', note: 'Ventana de pronóstico cubierta.', theme: 'default' },
    { label: 'PRECIO ENTRADA · GO', value: '60', unit: 'MXN/kg', note: 'LLDPE ligero · calibre 50 galgas.', theme: 'green' },
    { label: 'CALIBRE OBJETIVO', value: '50', unit: 'galgas', note: 'Foco en alto volumen.', theme: 'default' },
    { label: 'ESTADO PILOTO', value: 'Michoacán', unit: '', note: 'Primera restricción a un solo uso.', theme: 'default' },
    { label: 'RIESGO REGULATORIO', value: 'Alto', unit: '', note: 'Tendencia a normativa más estricta.', theme: 'red' },
  ],
  p1: {
    secLabel: '01 · PANORAMA COMPETITIVO',
    title: 'Tres tipos de jugador, tres ventajas distintas',
    cats: ['CAPACIDAD', 'TECNOLOGÍA', 'FLEXIBILIDAD', 'SERVICIO', 'PRECIO', 'LLDPE LIG.'],
    series: [
      { name: 'GRANDES (REYMA)', color: '#1A1A1A', values: [85, 78, 52, 70, 58, 42] },
      { name: 'LOCALES', color: '#9E9E9E', values: [60, 55, 70, 62, 72, 52] },
      { name: 'ENTRANTES (GO)', color: '#2A5A1A', values: [40, 45, 82, 72, 88, 92] },
    ],
    posLabel: 'POSICIONAMIENTO DE GRUPO ORTIZ GO',
    posText: 'LLDPE ligero · Calibre 50 ga.',
    posValue: '60',
    posUnit: 'MXN/kg',
    footer: 'Captura rápida de cuota vía precio en agricultura, retail pequeño y empaque de alimentos.',
  },
  p2: {
    secLabel: '02 · CONSUMIDOR Y DEMANDA',
    title: 'Alta aceptación, nueva sensibilidad ambiental',
    factoresLabel: 'FACTORES DE DECISIÓN DE COMPRA',
    factores: [
      { name: 'Precio', val: 94, up: false },
      { name: 'Conveniencia', val: 84, up: false },
      { name: 'Durabilidad', val: 78, up: false },
      { name: 'Calidad', val: 70, up: false },
      { name: 'Sostenibilidad', val: 62, up: true },
    ],
    aperturaLabel: 'APERTURA A ALTERNATIVAS',
    aperturaPct: 58,
    aperturaSeg: [
      { label: 'Ya prueban eco', pct: 58, color: '#1A1A1A' },
      { label: 'Considerarían', pct: 30, color: '#8B3220' },
      { label: 'Resistentes', pct: 12, color: '#CCCCCC' },
    ],
    sectoresLabel: 'SECTORES ANCLA · ACEPTACIÓN',
    sectores: [
      { name: 'Agricultura', val: 92 },
      { name: 'Retail pequeño', val: 86 },
      { name: 'Empaque alim.', val: 84 },
      { name: 'Foodservice', val: 68 },
      { name: 'Logística lig.', val: 54 },
    ],
    footer: 'Precio sigue siendo dominante; sostenibilidad es el criterio que más sube en B2C urbano.',
  },
  p3: {
    secLabel: '03 · POLÍTICA · 04 · RIESGOS Y OPORTUNIDADES',
    title: 'Michoacán abre la puerta · matriz estratégica',
    timeline: [
      { period: 'T0 · HOY', title: 'Michoacán', desc: 'Restricciones a plásticos de un solo uso.' },
      { period: '+6 M', title: 'Espejo estatal', desc: 'Estados vecinos inician anteproyectos similares.' },
      { period: '+12 M', title: 'Endurecimiento', desc: 'Posible normativa federal más estricta.' },
      { period: '+18 M', title: 'Reacomodo', desc: 'Migración a SKU sostenibles a escala.' },
    ],
    matrix: [
      { type: 'RIESGO', title: 'Regulación más estricta', desc: 'Restricciones afectan producción y venta de bolsas tradicionales.' },
      { type: 'RIESGO', title: 'Guerra de precios', desc: 'Entrada de competidores erosiona márgenes en segmento eco.' },
      { type: 'OPORTUNIDAD', title: 'Bio-plásticos', desc: 'Materiales biodegradables con curva de costo descendente.' },
      { type: 'OPORTUNIDAD', title: 'Empaque inteligente', desc: 'Segmento de mayor margen frente al commodity tradicional.' },
    ],
    footer: 'Empresas que no migren pierden cuota ante portafolios sostenibles en el horizonte 18 meses.',
  },
  quotes: [
    { src: 'GRUPO ORTIZ GO · REPRESENTANTE', text: '"LLDPE 50 galgas a 60 MXN/kg — objetivo: captura rápida de cuota."', accent: false },
    { src: 'FUNCIONARIO · MICHOACÁN', text: '"Restringir plásticos de un solo uso tendrá impacto significativo en los negocios locales."', accent: true },
    { src: 'SÍNTESIS · ANALISTAS', text: '"A corto plazo hay fricción; a largo plazo, transparencia y sostenibilidad."', accent: false },
  ],
  bottom: {
    postLabel: 'POSTURA RECOMENDADA',
    postTitle: 'Capturar hoy.\nTransitar con\ndisciplina.',
    actions: [
      { num: '01', lbl: 'COMERCIAL', title: 'Defender 60 MXN/kg en LLDPE', desc: 'Sostener la posición de precio en calibre 50 mientras dura la ventana en agricultura y retail pequeño.' },
      { num: '02', lbl: 'PRODUCTO', title: 'Abrir línea biodegradable', desc: 'Acelerar I+D en bio-plásticos y reutilizables. SKU listo antes de que las restricciones se vuelvan nacionales.' },
      { num: '03', lbl: 'REGULATORIO', title: 'Monitor Michoacán+', desc: 'Vigilancia activa por estado. Plan de respuesta documentado por escenario regulatorio.' },
    ],
  },
})

// Bar chart data computed
const barData = computed(() => {
  const cats = report.p1.cats
  const series = report.p1.series
  const totalW = 390
  const groupW = totalW / cats.length
  const barW = 12
  const barGap = 2
  const totalBarsW = series.length * barW + (series.length - 1) * barGap
  const padding = (groupW - totalBarsW) / 2
  const chartH = 92
  const baseY = 108

  const bars = []
  cats.forEach((cat, ci) => {
    series.forEach((ser, si) => {
      const x = ci * groupW + padding + si * (barW + barGap)
      const val = ser.values[ci] || 0
      const h = (val / 100) * chartH
      const y = baseY - h
      bars.push({ x, y, w: barW, h, color: ser.color })
    })
  })

  return { bars, groupW, cats, baseY, totalW }
})

// Donut chart paths computed
const donutPaths = computed(() => {
  const segs = report.p2.aperturaSeg
  const cx = 42, cy = 42, outerR = 36, innerR = 24
  let startDeg = -90
  return segs.map(seg => {
    const sweep = (seg.pct / 100) * 360
    const endDeg = startDeg + sweep
    const toRad = d => d * Math.PI / 180
    const large = sweep > 180 ? 1 : 0
    const sx = cx + outerR * Math.cos(toRad(startDeg))
    const sy = cy + outerR * Math.sin(toRad(startDeg))
    const ex = cx + outerR * Math.cos(toRad(endDeg))
    const ey = cy + outerR * Math.sin(toRad(endDeg))
    const ix = cx + innerR * Math.cos(toRad(endDeg))
    const iy = cy + innerR * Math.sin(toRad(endDeg))
    const jx = cx + innerR * Math.cos(toRad(startDeg))
    const jy = cy + innerR * Math.sin(toRad(startDeg))
    const path = `M${sx},${sy} A${outerR},${outerR} 0 ${large} 1 ${ex},${ey} L${ix},${iy} A${innerR},${innerR} 0 ${large} 0 ${jx},${jy} Z`
    startDeg = endDeg
    return { path, color: seg.color }
  })
})

// Wrapper style for scaling
const wrapperStyle = computed(() => ({
  width: SLIDE_W + 'px',
  height: SLIDE_H + 'px',
  transform: `scale(${slideScale.value})`,
  transformOrigin: 'top left',
}))

const updateScale = () => {
  if (!previewArea.value) return
  const availW = previewArea.value.clientWidth - 32
  const availH = previewArea.value.clientHeight - 32
  const scaleW = availW / SLIDE_W
  const scaleH = availH / SLIDE_H
  slideScale.value = Math.min(scaleW, scaleH, 1)
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)
})
onUnmounted(() => window.removeEventListener('resize', updateScale))

const downloadPdf = async () => {
  if (!slideRef.value || downloading.value) return
  downloading.value = true
  try {
    const canvas = await html2canvas(slideRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#FFFFFF',
      width: SLIDE_W,
      height: SLIDE_H,
      logging: false,
    })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ orientation: 'landscape', unit: 'px', format: [SLIDE_W, SLIDE_H] })
    pdf.addImage(imgData, 'PNG', 0, 0, SLIDE_W, SLIDE_H)
    const filename = `reporte-${report.meta.reportNum || 'mercado'}.pdf`
    pdf.save(filename)
  } catch (err) {
    console.error('PDF error:', err)
    alert('Error al generar PDF. Intente de nuevo.')
  } finally {
    downloading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── BUILDER SHELL ─────────────────────────────────────── */
.slide-builder {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1C1C1E;
  font-family: 'Inter', -apple-system, sans-serif;
  overflow: hidden;
}

.sb-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: #111;
  border-bottom: 1px solid #333;
  flex-shrink: 0;
}

.sb-toolbar-title {
  color: #AAA;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.03em;
}

.sb-btn-toggle {
  background: #2A2A2E;
  color: #DDD;
  border: 1px solid #444;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-family: inherit;
}
.sb-btn-toggle:hover { background: #383840; }

.sb-btn-pdf {
  display: flex;
  align-items: center;
  gap: 7px;
  background: #1A5C28;
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  font-weight: 600;
  transition: background 0.15s;
}
.sb-btn-pdf:hover:not(:disabled) { background: #1E7030; }
.sb-btn-pdf:disabled { opacity: 0.5; cursor: not-allowed; }

.sb-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ── FORM SIDEBAR ─────────────────────────────────────── */
.sb-form {
  width: 320px;
  flex-shrink: 0;
  background: #1A1A1C;
  border-right: 1px solid #333;
  overflow-y: auto;
}

.sb-form-inner { padding: 12px; }

.sf-section {
  margin-bottom: 4px;
  border: 1px solid #2C2C30;
  border-radius: 6px;
  overflow: hidden;
}

.sf-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 12px;
  background: #222226;
  cursor: pointer;
  color: #CCC;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  user-select: none;
}
.sf-section-header:hover { background: #2A2A30; }

.sf-section-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sf-section-body label {
  font-size: 10px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: 6px;
}

.sf-section-body input,
.sf-section-body textarea,
.sf-section-body select {
  background: #111;
  border: 1px solid #333;
  color: #DDD;
  padding: 5px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}
.sf-section-body input:focus,
.sf-section-body textarea:focus,
.sf-section-body select:focus {
  outline: none;
  border-color: #2A5C1A;
}

.sf-group-title {
  font-size: 11px;
  font-weight: 700;
  color: #777;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #2A2A2E;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sf-kpi-group {
  border: 1px solid #222;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 6px;
}

.sf-inline {
  display: flex;
  gap: 6px;
  align-items: center;
}

/* ── PREVIEW AREA ─────────────────────────────────────── */
.sb-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #111;
  padding: 16px;
}

.sb-slide-wrapper {
  flex-shrink: 0;
  box-shadow: 0 8px 40px rgba(0,0,0,0.7);
}

/* ══════════════════════════════════════════════════════════
   THE SLIDE — 1440×810 pixels
   ══════════════════════════════════════════════════════════ */
.s-slide {
  width: 1440px;
  height: 810px;
  background: #FFFFFF;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #1A1A1A;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  box-sizing: border-box;
}

/* SUPERTITLE */
.s-supertitle {
  text-align: center;
  font-size: 9.5px;
  font-weight: 500;
  letter-spacing: 0.14em;
  color: #888;
  padding: 8px 0 4px;
  flex-shrink: 0;
}

/* HEADER */
.s-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0 38px 12px;
  flex-shrink: 0;
}

.s-header-left {
  width: 200px;
  flex-shrink: 0;
}

.s-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.s-logo-text {
  display: flex;
  flex-direction: column;
}

.s-logo-company {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #1A1A1A;
}

.s-logo-tag {
  font-size: 8px;
  font-weight: 500;
  letter-spacing: 0.1em;
  color: #666;
  margin-top: 1px;
}

.s-header-center {
  flex: 1;
  text-align: center;
  padding: 0 20px;
}

.s-main-title {
  margin: 0;
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -0.01em;
  line-height: 1.1;
  color: #1A1A1A;
}

.s-header-right {
  width: 200px;
  flex-shrink: 0;
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  padding-top: 2px;
}

.s-rep-num {
  font-size: 9px;
  font-weight: 600;
  color: #888;
  letter-spacing: 0.08em;
}

.s-rep-date {
  font-size: 9px;
  font-weight: 700;
  color: #1A1A1A;
  letter-spacing: 0.08em;
}

.s-rep-conf {
  font-size: 8px;
  font-weight: 500;
  color: #999;
  letter-spacing: 0.1em;
}

.s-header-rule {
  height: 2px;
  background: #1A1A1A;
  margin: 0 38px;
  flex-shrink: 0;
}

/* KPI CARDS */
.s-kpis {
  display: flex;
  border-top: 1px solid #E0E0DC;
  flex-shrink: 0;
}

.s-kpi {
  flex: 1;
  padding: 10px 16px 10px;
  border-right: 1px solid #E0E0DC;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.s-kpi:last-child { border-right: none; }

.s-kpi--green {
  background: #1C3B1A;
  color: #fff;
}

.s-kpi--red {
  background: #7C2E18;
  color: #fff;
}

.s-kpi-label {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: inherit;
  opacity: 0.8;
  text-transform: uppercase;
}

.s-kpi--green .s-kpi-label,
.s-kpi--red .s-kpi-label {
  color: rgba(255,255,255,0.75);
  opacity: 1;
}

.s-kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.s-kpi-value {
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
  color: inherit;
  letter-spacing: -0.02em;
}

.s-kpi-unit {
  font-size: 12px;
  font-weight: 500;
  color: inherit;
  opacity: 0.8;
}

.s-kpi-note {
  font-size: 9px;
  color: inherit;
  opacity: 0.7;
  margin-top: 2px;
}

/* PANELS */
.s-panels {
  display: flex;
  flex: 1;
  border-top: 1px solid #E0E0DC;
  overflow: hidden;
}

.s-panel {
  flex: 1;
  border-right: 1px solid #E0E0DC;
  padding: 12px 16px 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.s-panel:last-child { border-right: none; }

.s-panel-label {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #888;
  text-transform: uppercase;
  margin-bottom: 3px;
}

.s-panel-title {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.25;
  color: #1A1A1A;
  letter-spacing: -0.01em;
}

.s-panel-footer {
  margin: auto 0 0;
  font-size: 8.5px;
  color: #888;
  line-height: 1.45;
  padding-top: 8px;
  border-top: 1px solid #E8E6E0;
}

/* BAR CHART */
.s-barchart {
  width: 100%;
  height: 140px;
  flex-shrink: 0;
}

/* CHART LEGEND */
.s-chart-legend {
  display: flex;
  gap: 12px;
  margin: 5px 0 8px;
  flex-shrink: 0;
}

.s-legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.s-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 1px;
  flex-shrink: 0;
}

.s-legend-label {
  font-size: 8px;
  color: #555;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* POSITIONING BOX */
.s-pos-box {
  background: #1A1A1A;
  color: #fff;
  border-radius: 3px;
  padding: 8px 12px;
  margin: 6px 0;
  flex-shrink: 0;
}

.s-pos-box-top {
  margin-bottom: 5px;
}

.s-pos-box-label {
  font-size: 7.5px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
}

.s-pos-box-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.s-pos-box-text {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.s-pos-box-price {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.s-pos-box-value {
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  line-height: 1;
}

.s-pos-box-unit {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  font-weight: 500;
}

/* PANEL 02 */
.s-chart-label {
  font-size: 7.5px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #888;
  text-transform: uppercase;
  margin-bottom: 4px;
  display: block;
}

.s-hbarchart {
  width: 100%;
  height: 98px;
  flex-shrink: 0;
  margin-bottom: 6px;
}

.s-apertura-row {
  display: flex;
  gap: 10px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.s-apertura-left {
  display: flex;
  flex-direction: column;
  width: 130px;
  flex-shrink: 0;
}

.s-donut-wrap {
  display: flex;
  justify-content: center;
  margin: 4px 0;
}

.s-donut-legend {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.s-donut-leg-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.s-donut-leg-dot {
  width: 8px;
  height: 8px;
  border-radius: 1px;
  flex-shrink: 0;
}

.s-donut-leg-label {
  font-size: 8.5px;
  color: #1A1A1A;
  flex: 1;
}

.s-donut-leg-pct {
  font-size: 8.5px;
  font-weight: 600;
  color: #1A1A1A;
}

.s-apertura-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* PANEL 03 */
.s-timeline {
  display: flex;
  gap: 0;
  margin-bottom: 10px;
  flex-shrink: 0;
  border-bottom: 1px solid #E0DDD8;
  padding-bottom: 10px;
}

.s-timeline-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-right: 8px;
  position: relative;
}

.s-timeline-period {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #888;
  text-transform: uppercase;
  margin-bottom: 5px;
}

.s-timeline-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #7C2E18;
  margin-bottom: 5px;
  flex-shrink: 0;
}

.s-timeline-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.s-timeline-title {
  font-size: 11px;
  font-weight: 700;
  color: #1A1A1A;
  line-height: 1.2;
}

.s-timeline-desc {
  font-size: 8.5px;
  color: #666;
  line-height: 1.35;
}

/* MATRIX */
.s-matrix {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 6px;
  flex: 1;
  min-height: 0;
}

.s-matrix-item {
  padding: 7px 8px;
  background: #F7F6F3;
  border-radius: 2px;
}

.s-matrix-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 3px;
}

.s-matrix-dot {
  width: 8px;
  height: 8px;
  flex-shrink: 0;
}

.s-dot-risk { background: #7C2E18; }
.s-dot-opp { background: #1A1A1A; }

.s-matrix-type {
  font-size: 7px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.s-matrix-risk .s-matrix-type { color: #7C2E18; }
.s-matrix-opp .s-matrix-type { color: #1A1A1A; }

.s-matrix-title {
  font-size: 11px;
  font-weight: 700;
  color: #1A1A1A;
  display: block;
  margin-bottom: 3px;
  line-height: 1.2;
}

.s-matrix-desc {
  margin: 0;
  font-size: 8px;
  color: #666;
  line-height: 1.4;
}

/* QUOTES */
.s-quotes {
  display: flex;
  border-top: 1px solid #E0DDD8;
  background: #F7F6F3;
  flex-shrink: 0;
}

.s-quote {
  flex: 1;
  padding: 9px 16px;
  border-right: 1px solid #E0DDD8;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.s-quote:last-child { border-right: none; }

.s-quote-src {
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #555;
  text-transform: uppercase;
}

.s-quote-src--accent {
  color: #7C2E18;
}

.s-quote-text {
  margin: 0;
  font-size: 9.5px;
  color: #1A1A1A;
  line-height: 1.45;
  font-style: italic;
}

/* BOTTOM */
.s-bottom {
  display: flex;
  border-top: 2px solid #1A1A1A;
  flex-shrink: 0;
  min-height: 100px;
}

.s-postura {
  padding: 12px 18px;
  border-right: 1px solid #E0DDD8;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  width: 200px;
  flex-shrink: 0;
  border-left: 5px solid #1A1A1A;
}

.s-postura-label {
  font-size: 7.5px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: #888;
  text-transform: uppercase;
  margin-bottom: 5px;
}

.s-postura-title {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  line-height: 1.2;
  color: #1A1A1A;
  letter-spacing: -0.02em;
}

.s-action {
  flex: 1;
  padding: 10px 16px;
  border-right: 1px solid #E0DDD8;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.s-action:last-child { border-right: none; }

.s-action-header {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 3px;
}

.s-action-num {
  font-size: 9px;
  font-weight: 800;
  color: #1A1A1A;
  letter-spacing: 0.05em;
}

.s-action-lbl {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #555;
  text-transform: uppercase;
}

.s-action-title {
  font-size: 12px;
  font-weight: 700;
  color: #1A1A1A;
  line-height: 1.2;
}

.s-action-desc {
  margin: 0;
  font-size: 8.5px;
  color: #666;
  line-height: 1.4;
}

/* MIDDLE PANEL STYLES */
.s-panel--mid {
  flex: 1.05;
}
</style>
