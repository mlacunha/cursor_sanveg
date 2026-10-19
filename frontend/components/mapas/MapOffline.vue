<template>
  <div class="relative h-full w-full">
    <!-- Indicador de Modo Offline -->
    <div class="absolute top-3 left-12 z-[1000] bg-slate-900/80 text-white text-[10px] font-bold px-2.5 py-1 rounded-lg border border-slate-700/50 backdrop-blur-sm tracking-wider uppercase">
      Offline Mode (Pontos Locais)
    </div>

    <!-- Container do Mapa -->
    <div
      id="map-offline"
      class="h-full w-full rounded-2xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800"
    ></div>

    <!-- Alerta de dados vazios -->
    <div
      v-if="markersCount === 0 && !loading"
      class="absolute bottom-4 left-4 z-[1000] bg-white/95 dark:bg-slate-900/95 border border-slate-200 dark:border-slate-800 px-4 py-2.5 rounded-xl shadow-lg max-w-xs text-xs text-slate-500"
    >
      Nenhum ponto georreferenciado encontrado no banco de dados local.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { db } from '~/utils/db'

const markersCount = ref(0)
const loading = ref(true)
let map: any = null

onMounted(async () => {
  if (!process.client) return

  try {
    // Importações dinâmicas do Leaflet (Evita quebra no SSR)
    const L = await import('leaflet')
    await import('leaflet/dist/leaflet.css')

    // Inicializa o mapa com zoom focado no Pará
    map = L.map('map-offline', {
      zoomControl: true,
      zoomSnap: 0.5,
      zoomDelta: 0.5
    }).setView([-3.85, -52.5], 6)

    // 1. Carrega contorno vetorial simplificado do Pará (obtido da pasta public)
    const geoResponse = await fetch('/geojs-15-mun-simplified.json')
    if (geoResponse.ok) {
      const geoJsonData = await geoResponse.json()
      L.geoJSON(geoJsonData, {
        style: {
          color: '#64748b',
          weight: 1.5,
          fillColor: '#94a3b8',
          fillOpacity: 0.05
        },
        interactive: false
      }).addTo(map)
    }

    // 2. Consulta pontos das inspeções salvas no Dexie
    const [areas, programas, propriedades] = await Promise.all([
      db.area_inspecionada.toArray(),
      db.area_programa.toArray(),
      db.propriedades.toArray()
    ])

    // Mapeia nomes de propriedades
    const propNameMap = new Map<string, string>()
    propriedades.forEach(p => propNameMap.set(p.id, p.nome || ''))

    // Agrupa resultados por ID de área física
    const statusPorArea = new Map<string, { status: string; programa: string }>()
    programas.forEach(p => {
      if (p.id_area) {
        const cur = statusPorArea.get(p.id_area)
        const res = String(p.resultado).toUpperCase()
        
        // Prioridade de cor: POSITIVO > SUSPEITA > NORMAL
        if (!cur || res === 'POSITIVO' || res === 'FOCO' || (res === 'SUSPEITA' && cur.status !== 'POSITIVO')) {
          statusPorArea.set(p.id_area, {
            status: res,
            programa: p.id_programa
          })
        }
      }
    })

    const bounds: any[] = []

    // 3. Plota marcadores CircleMarker
    areas.forEach(area => {
      const lat = Number(area.latitude)
      const lon = Number(area.longitude)

      if (!isNaN(lat) && !isNaN(lon) && lat !== 0 && lon !== 0) {
        const areaInfo = statusPorArea.get(area.id)
        const status = areaInfo?.status || 'NORMAL'
        
        // Definição de Cores por Status
        const color = status === 'POSITIVO' || status === 'FOCO'
          ? '#ef4444' // Vermelho
          : status === 'SUSPEITA'
            ? '#f97316' // Laranja
            : '#3b82f6' // Azul

        const marker = L.circleMarker([lat, lon], {
          radius: 6,
          fillColor: color,
          fillOpacity: 0.85,
          color: '#ffffff',
          weight: 1.5
        })

        // Constrói HTML do Popup
        const popupHtml = `
          <div style="font-family: sans-serif; min-width: 180px; padding: 4px;">
            <b style="color: #1714EF; font-size: 13px;">Ponto Local (Offline)</b><br>
            <b style="font-size: 12px; display: block; margin-top: 5px;">${area.nome_local || 'Local Sem Nome'}</b>
            <hr style="margin: 8px 0; border: 0; border-top: 1px solid #eee;" />
            <span style="font-size: 11px; color: #64748b;">
              <b>Status:</b> ${status}<br>
              <b>Latitude:</b> ${lat.toFixed(5)}<br>
              <b>Longitude:</b> ${lon.toFixed(5)}
            </span>
          </div>
        `

        marker.bindPopup(popupHtml)
        marker.addTo(map)
        
        bounds.push([lat, lon])
        markersCount.value++
      }
    })

    // Ajusta o enquadramento se houver marcadores plotados
    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40] })
    }

  } catch (err) {
    console.error('[MapOffline] Erro ao carregar mapa offline:', err)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>
