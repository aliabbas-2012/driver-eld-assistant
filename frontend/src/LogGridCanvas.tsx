import { useEffect, useRef } from 'react'

type Interval = { start_h: number; end_h: number }

type GridData = {
  intervals?: Record<string, Interval[]>
}

const ROWS = [
  { key: 'off_duty', label: 'Off duty' },
  { key: 'sleeper', label: 'Sleeper' },
  { key: 'driving', label: 'Driving' },
  { key: 'on_duty_not_driving', label: 'On duty (N/D)' },
] as const

export function LogGridCanvas({
  logDate,
  gridData,
}: {
  logDate: string
  gridData: GridData | null | undefined
}) {
  const ref = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const w = canvas.width
    const h = canvas.height
    ctx.clearRect(0, 0, w, h)
    const margin = 88
    const hourW = (w - margin - 8) / 24
    const rowH = (h - 36) / 4

    ctx.fillStyle = '#f8fafc'
    ctx.fillRect(0, 0, w, h)
    ctx.strokeStyle = '#cbd5e1'
    ctx.lineWidth = 1
    for (let hr = 0; hr <= 24; hr++) {
      const x = margin + hr * hourW
      ctx.beginPath()
      ctx.moveTo(x, 8)
      ctx.lineTo(x, h - 8)
      ctx.stroke()
    }
    for (let r = 0; r <= 4; r++) {
      const y = 8 + r * rowH
      ctx.beginPath()
      ctx.moveTo(margin, y)
      ctx.lineTo(w - 8, y)
      ctx.stroke()
    }

    ctx.fillStyle = '#0f172a'
    ctx.font = '11px system-ui'
    for (let hr = 0; hr < 24; hr++) {
      ctx.fillText(`${hr}`, margin + hr * hourW + 2, h - 12)
    }
    ROWS.forEach((row, ri) => {
      ctx.fillText(row.label, 8, 8 + ri * rowH + rowH / 2 + 4)
    })

    const intervals = gridData?.intervals || {}
    const colors: Record<string, string> = {
      off_duty: '#64748b',
      sleeper: '#7c3aed',
      driving: '#0ea5e9',
      on_duty_not_driving: '#f59e0b',
    }
    ROWS.forEach((row, ri) => {
      const list = intervals[row.key] || []
      const y0 = 8 + ri * rowH + 4
      const rh = rowH - 8
      list.forEach((iv: Interval) => {
        const x0 = margin + iv.start_h * hourW
        const x1 = margin + iv.end_h * hourW
        ctx.fillStyle = colors[row.key] || '#334155'
        ctx.fillRect(x0, y0, Math.max(x1 - x0, 1), rh)
      })
    })

    ctx.fillStyle = '#0f172a'
    ctx.font = 'bold 12px system-ui'
    ctx.fillText(`Log date: ${logDate}`, margin, 22)
  }, [logDate, gridData])

  return (
    <canvas
      ref={ref}
      width={720}
      height={200}
      className="w-full max-w-[720px] h-auto rounded-lg border border-slate-200 bg-white"
    />
  )
}
