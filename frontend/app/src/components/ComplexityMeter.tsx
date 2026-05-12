interface ComplexityMeterProps {
  value: number
}

export default function ComplexityMeter({ value }: ComplexityMeterProps) {
  const segs = 10
  return (
    <div className="complexity-meter">
      {Array.from({ length: segs }).map((_, i) => (
        <span key={i} className={`seg ${i < value ? 'on' : ''}`} />
      ))}
      <span className="label">Complexity {value}/10</span>
    </div>
  )
}
