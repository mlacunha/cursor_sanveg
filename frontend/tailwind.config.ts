import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  theme: {
    extend: {
      colors: {
        'brand-blue': '#1714EF',
        'brand-blue-light': '#4A48FC',
        'suspect-orange': '#f59e0b',
        'outbreak-red': '#ef4444',
        Colors: {
          BrandBlue: '#1714EF',
          BrandBlueLight: '#4A48FC',
          SuspectOrange: '#f59e0b',
          OutbreakRed: '#ef4444',
          Nav: 'rgba(255, 255, 255, 0.75)'
        }
      },
      // Configuração para permitir o uso de nomes de ícones lucide no padrão solicitado
      Icons: {
        Prefix: 'lucide'
      }
    }
  }
}
