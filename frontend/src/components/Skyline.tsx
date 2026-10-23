// An original silhouette of a gothic campus at night: a tall Harkness-style tower,
// chapel roofs, spires, and elm canopies, with windows that glow and flicker.
// Purely decorative, drawn in SVG so it stays crisp at any width.

const WINDOWS: [number, number][] = [
  // the tall tower (x 700-820)
  [735, 170], [777, 170], [735, 215], [756, 215], [777, 215], [735, 262], [756, 262], [777, 262], [745, 310], [767, 310],
  // the left chapel (x 400-550)
  [432, 312], [458, 312], [484, 312], [510, 312], [445, 350], [497, 350],
  // the right chapel (x 900-1064)
  [925, 322], [952, 322], [979, 322], [1006, 322], [1033, 322], [952, 360], [1006, 360],
  // smaller halls
  [190, 322], [222, 322], [276, 336], [1128, 340], [1154, 340], [1268, 326],
]

export default function Skyline() {
  return (
    <svg className="skyline" viewBox="0 0 1400 420" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      <defs>
        <linearGradient id="skyline-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0b2347" />
          <stop offset="100%" stopColor="#040a17" />
        </linearGradient>
        <linearGradient id="skyline-edge" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#6fd3ff" stopOpacity="0" />
          <stop offset="50%" stopColor="#6fd3ff" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#9d8cff" stopOpacity="0" />
        </linearGradient>
        <filter id="window-glow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Elm canopies behind the buildings */}
      <g className="skyline__elms">
        <ellipse cx="120" cy="330" rx="140" ry="80" />
        <ellipse cx="330" cy="300" rx="120" ry="90" />
        <ellipse cx="590" cy="320" rx="130" ry="70" />
        <ellipse cx="820" cy="310" rx="120" ry="85" />
        <ellipse cx="1060" cy="300" rx="150" ry="90" />
        <ellipse cx="1300" cy="320" rx="140" ry="85" />
      </g>

      <path
        className="skyline__buildings"
        fill="url(#skyline-fill)"
        d="M0 420 V360 h60 v-30 h20 v30 h90 V300 l20-30 l20 30 v60 h40 V312 h70 v-26 l18-22 l18 22 v26 h20 v108
           H400 V290 l30-34 l30 34 V250 l15-40 l15 40 v40 l30-34 l30 34 v130 h60 V340 h40 v-20 h10 v20 h40
           V200 h12 V150 l10-24 l10 24 h12 V110 l9-16 h4 l3-30 l3 30 h4 l9 16 V150 h12 l10-24 l10 24 V200 h12
           v220 h80 V300 l35-40 l35 40 v-20 l12-28 l12 28 v20 l35-40 l35 40 v120 h50 V320 h60 v-30 l20-26 l20 26
           v30 h40 V300 l22-30 l22 30 v120 h60 V340 h50 v-28 l14-18 l14 18 v28 h70 V420 Z"
      />
      <path className="skyline__edge" stroke="url(#skyline-edge)" fill="none" d="M0 360 H1400" />

      <g className="skyline__windows" filter="url(#window-glow)">
        {WINDOWS.map(([x, y], index) => (
          <rect key={`${x}-${y}`} x={x} y={y} width="7" height="12" rx="3" style={{ animationDelay: `${(index * 0.73) % 6}s` }} />
        ))}
      </g>
    </svg>
  )
}
