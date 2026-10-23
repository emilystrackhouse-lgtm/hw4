import { useEffect, useRef } from 'react'

// Bioluminescent "elm spores": soft points of Yale-blue light that drift up behind
// every page and brighten when the shopper's pointer passes near, like the glowing
// seeds of a night forest. Drawn on one canvas; paused when the tab is hidden and
// frozen in place for shoppers who prefer reduced motion.

type Spore = { x: number; y: number; r: number; speed: number; sway: number; phase: number; hue: string }

const COLORS = ['111, 211, 255', '123, 160, 197', '94, 234, 212', '157, 140, 255']
const COLOR_WEIGHTS = [0.55, 0.25, 0.12, 0.08] // mostly Yale-blue glow, a little aqua and violet

function pickColor() {
  let roll = Math.random()
  for (let i = 0; i < COLORS.length; i++) {
    roll -= COLOR_WEIGHTS[i]
    if (roll <= 0) return COLORS[i]
  }
  return COLORS[0]
}

export default function Spores() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const context = canvas?.getContext('2d')
    if (!canvas || !context) return
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const pointer = { x: -9999, y: -9999 }
    let spores: Spore[] = []
    let frame = 0
    let width = 0
    let height = 0

    const resize = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2)
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width * ratio
      canvas.height = height * ratio
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      const count = Math.round(Math.min(110, Math.max(40, (width * height) / 14000)))
      spores = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        r: 0.6 + Math.random() * 1.9,
        speed: 0.08 + Math.random() * 0.32,
        sway: 0.3 + Math.random() * 0.9,
        phase: Math.random() * Math.PI * 2,
        hue: pickColor(),
      }))
    }

    const draw = (time: number) => {
      context.clearRect(0, 0, width, height)
      for (const s of spores) {
        if (!reduceMotion) {
          s.y -= s.speed
          s.x += Math.sin(time / 1800 + s.phase) * s.sway * 0.25
          if (s.y < -10) {
            s.y = height + 10
            s.x = Math.random() * width
          }
        }
        const distance = Math.hypot(s.x - pointer.x, s.y - pointer.y)
        const near = Math.max(0, 1 - distance / 160) // brighter close to the pointer
        const twinkle = 0.45 + 0.35 * Math.sin(time / 900 + s.phase * 3)
        const alpha = Math.min(1, twinkle + near * 0.6)
        const radius = s.r * (1 + near * 1.2)
        const glow = context.createRadialGradient(s.x, s.y, 0, s.x, s.y, radius * 6)
        glow.addColorStop(0, `rgba(${s.hue}, ${alpha})`)
        glow.addColorStop(0.35, `rgba(${s.hue}, ${alpha * 0.35})`)
        glow.addColorStop(1, `rgba(${s.hue}, 0)`)
        context.fillStyle = glow
        context.beginPath()
        context.arc(s.x, s.y, radius * 6, 0, Math.PI * 2)
        context.fill()
      }
      if (!reduceMotion && !document.hidden) frame = requestAnimationFrame(draw)
    }

    const onMove = (event: PointerEvent) => {
      pointer.x = event.clientX
      pointer.y = event.clientY
    }
    const onVisibility = () => {
      cancelAnimationFrame(frame)
      if (!document.hidden) frame = requestAnimationFrame(draw)
    }

    resize()
    frame = requestAnimationFrame(draw)
    window.addEventListener('resize', resize)
    window.addEventListener('pointermove', onMove, { passive: true })
    document.addEventListener('visibilitychange', onVisibility)
    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('resize', resize)
      window.removeEventListener('pointermove', onMove)
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [])

  return <canvas ref={canvasRef} className="spores" aria-hidden="true" />
}
