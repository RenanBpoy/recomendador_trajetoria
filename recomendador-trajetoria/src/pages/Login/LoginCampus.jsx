import { useId } from 'react'
import salomao from '../../assets/img/salomao-heart.png'

const trees = [
  [26, 208, 1.35], [73, 192, 0.92], [115, 186, 0.68],
  [246, 186, 0.7], [289, 194, 0.93], [340, 218, 1.4],
]

export default function LoginCampus({ children }) {
  const roadFadeId = useId()

  return (
    <div className="login-campus">
      <svg className="login-campus__landscape" viewBox="0 0 360 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <defs>
          <linearGradient id={roadFadeId} gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="194" y2="202">
            <stop offset="0" stopColor="white" stopOpacity="0" />
            <stop offset=".3" stopColor="white" stopOpacity=".2" />
            <stop offset=".72" stopColor="white" stopOpacity=".82" />
            <stop offset="1" stopColor="white" />
          </linearGradient>
          <mask id={roadFadeId + "-mask"} maskUnits="userSpaceOnUse" x="0" y="194" width="360" height="146">
            <rect x="0" y="194" width="360" height="146" fill={`url(#${roadFadeId})`} />
          </mask>
        </defs>
        <circle cx="264" cy="92" r="41" fill="#78a7c9" opacity=".77" />
        <path d="M0 209Q65 164 124 193T228 190T360 189V340H0Z" fill="var(--campus-soil)" />
        <g mask={`url(#${roadFadeId}-mask)`}>
          <path d="M165 194H199L351 340H7Z" fill="var(--campus-road)" />
          <path d="M179 196h5l13 144h-32z" fill="#1d526d" opacity=".55" />
        </g>
        {trees.map(([x, y, scale]) => (
          <g key={x} transform={`translate(${x} ${y}) scale(${scale})`}>
            <path d="M0 38V0m0 11-10-9m10 17 12-15" stroke="#122a3f" strokeWidth="2" fill="none" />
            <path d="M-20 5Q-29-9-17-16Q-16-29-3-23Q11-32 20-17Q30-10 22 1Q16 12-20 5Z" fill="var(--campus-tree)" />
          </g>
        ))}
        <ellipse cx="42" cy="268" rx="36" ry="7" fill="#172d34" opacity=".52" />
        <ellipse cx="318" cy="268" rx="36" ry="7" fill="#172d34" opacity=".52" />
        <path d="M18 267C51 117 111 58 180 58S309 117 342 267H313C289 147 239 87 180 87S71 147 47 267Z" fill="var(--campus-shade)" />
        <path d="M18 267C51 117 111 58 180 58S309 117 342 267H326C297 132 244 74 180 74S63 132 34 267Z" fill="var(--campus-arch)" />
        <path d="M18 267H47L44 271H20ZM313 267H342L340 271H316Z" fill="#263e50" />
        <path d="M26 257C58 120 114 63 180 63S302 120 334 257" fill="none" stroke="#e2f9ff" strokeOpacity=".28" strokeWidth="2" />
      </svg>
      <img className="login-campus__mascot" src={salomao} alt="" />
      {children}
    </div>
  )
}
