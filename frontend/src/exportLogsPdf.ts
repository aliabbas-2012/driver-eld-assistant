import { jsPDF } from 'jspdf'

type DutyRow = {
  status: string
  start_time: string
  end_time: string
  duration_hours: string | null
  location: string
}

export type DailyLogPdf = {
  day_number: number
  log_date: string
  total_miles_driven: number
  driving_hours: string
  on_duty_hours: string
  remarks: string
  duty_changes: DutyRow[]
}

export type TripPdfInput = {
  id: number
  current_location: string
  pickup_location: string
  dropoff_location: string
  total_distance_miles: number | null
  total_days: number | null
  trip_start_date: string | null
  route_instructions_json: {
    driving_steps?: { kind: string; instruction: string; distance_m?: number | null }[]
    hos_stops?: { kind?: string; label?: string }[]
    hos_summary?: Record<string, unknown>
  } | null
  daily_logs: DailyLogPdf[]
}

function splitLines(doc: jsPDF, text: string, maxWidth: number): string[] {
  const words = text.split(/\s+/)
  const lines: string[] = []
  let cur = ''
  for (const w of words) {
    const test = cur ? `${cur} ${w}` : w
    if (doc.getTextWidth(test) <= maxWidth) {
      cur = test
    } else {
      if (cur) lines.push(cur)
      cur = w
    }
  }
  if (cur) lines.push(cur)
  return lines.length ? lines : ['']
}

function clip(s: string, n: number) {
  return s.length > n ? `${s.slice(0, n - 3)}...` : s
}

export function downloadTripLogsPdf(trip: TripPdfInput) {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const pageW = doc.internal.pageSize.getWidth()
  const margin = 14
  const maxW = pageW - margin * 2
  let y = 18

  doc.setFontSize(16)
  doc.text('Driver ELD Assistant — Trip package', margin, y)
  y += 10
  doc.setFontSize(10)
  for (const line of splitLines(
    doc,
    `Trip #${trip.id}  |  ${trip.total_distance_miles ?? '—'} mi  |  ${trip.total_days ?? '—'} day(s)  |  Start ${trip.trip_start_date ?? '—'}`,
    maxW,
  )) {
    doc.text(line, margin, y)
    y += 5
  }
  y += 4
  doc.setFontSize(11)
  doc.text('Stops', margin, y)
  y += 6
  doc.setFontSize(9)
  for (const label of [
    `Current: ${trip.current_location}`,
    `Pickup: ${trip.pickup_location}`,
    `Dropoff: ${trip.dropoff_location}`,
  ]) {
    for (const line of splitLines(doc, label, maxW)) {
      doc.text(line, margin, y)
      y += 4.5
      if (y > 270) {
        doc.addPage()
        y = 18
      }
    }
  }

  const ri = trip.route_instructions_json
  if (ri?.hos_summary) {
    y += 4
    doc.setFontSize(11)
    doc.text('HOS planning summary', margin, y)
    y += 6
    doc.setFontSize(9)
    const blob = JSON.stringify(ri.hos_summary)
    for (const line of splitLines(doc, blob, maxW)) {
      doc.text(line, margin, y)
      y += 4.5
      if (y > 270) {
        doc.addPage()
        y = 18
      }
    }
  }

  if (ri?.hos_stops?.length) {
    y += 4
    doc.setFontSize(11)
    doc.text('Planned HOS stops (fuel / break / pickup / dropoff)', margin, y)
    y += 6
    doc.setFontSize(9)
    for (const s of ri.hos_stops) {
      const t = `${s.kind ?? 'stop'}: ${s.label ?? ''}`
      for (const line of splitLines(doc, t, maxW)) {
        doc.text(line, margin, y)
        y += 4.5
        if (y > 270) {
          doc.addPage()
          y = 18
        }
      }
    }
  }

  if (ri?.driving_steps?.length) {
    y += 4
    doc.setFontSize(11)
    doc.text('Turn-by-turn (OSRM, excerpt)', margin, y)
    y += 6
    doc.setFontSize(8)
    let n = 0
    for (const step of ri.driving_steps) {
      if (n++ > 120) break
      const distMi =
        step.distance_m != null && step.distance_m !== undefined
          ? ` (${(step.distance_m / 1609.34).toFixed(2)} mi)`
          : ''
      const raw = `${step.instruction || ''}${distMi}`
      for (const line of splitLines(doc, raw, maxW)) {
        doc.text(line, margin, y)
        y += 3.8
        if (y > 275) {
          doc.addPage()
          y = 18
        }
      }
    }
  }

  for (const log of trip.daily_logs) {
    doc.addPage()
    y = 18
    doc.setFontSize(14)
    doc.text(`Daily log — Day ${log.day_number} (${log.log_date})`, margin, y)
    y += 8
    doc.setFontSize(9)
    doc.text(
      `Driving ${log.driving_hours} h  |  Miles (planned day) ${log.total_miles_driven}  |  On-duty ${log.on_duty_hours} h`,
      margin,
      y,
    )
    y += 8
    doc.setFontSize(8)
    doc.text('Status', margin, y)
    doc.text('Start', margin + 28, y)
    doc.text('End', margin + 48, y)
    doc.text('Hrs', margin + 68, y)
    doc.text('Location', margin + 82, y)
    y += 5
    doc.line(margin, y, pageW - margin, y)
    y += 5
    for (const d of log.duty_changes ?? []) {
      if (y > 278) {
        doc.addPage()
        y = 18
      }
      doc.text(clip(d.status, 18), margin, y)
      doc.text(clip(String(d.start_time), 10), margin + 28, y)
      doc.text(clip(String(d.end_time), 10), margin + 48, y)
      doc.text(clip(String(d.duration_hours ?? ''), 6), margin + 68, y)
      doc.text(clip(d.location, 95), margin + 82, y)
      y += 5.5
    }
    if (log.remarks) {
      y += 4
      doc.setFontSize(9)
      doc.text('Remarks', margin, y)
      y += 5
      doc.setFontSize(8)
      for (const line of splitLines(doc, log.remarks, maxW)) {
        doc.text(line, margin, y)
        y += 4
        if (y > 280) {
          doc.addPage()
          y = 18
        }
      }
    }
  }

  doc.save(`eld-trip-${trip.id}-logs.pdf`)
}
