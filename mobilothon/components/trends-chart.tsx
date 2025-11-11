// "use client"

// import { useState, useEffect } from "react"
// import {
//   LineChart,
//   Line,
//   AreaChart,
//   Area,
//   BarChart,
//   Bar,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   Legend,
//   ResponsiveContainer,
// } from "recharts"
// import { Loader2 } from "lucide-react"

// interface TrendData {
//   time: string
//   fatigue_score: number
//   eye_ratio: number
//   blink_count: number
// }

// export default function TrendsChart() {
//   const [data, setData] = useState<TrendData[]>([])
//   const [loading, setLoading] = useState(true)
//   const [error, setError] = useState<string | null>(null)
//   const [chartType, setChartType] = useState<"line" | "area" | "bar">("line")

//   useEffect(() => {
//     const fetchTrends = async () => {
//       try {
//         setLoading(true)
//         const response = await fetch("/api/history")
//         if (!response.ok) throw new Error("Failed to fetch trends")
//         const rawData = await response.json()

//         // Process data into trends (last 24 records)
//         const processed = rawData.slice(-24).map((record: any, index: number) => {
//           const date = new Date(record.timestamp)
//           const hours = String(date.getHours()).padStart(2, "0")
//           const minutes = String(date.getMinutes()).padStart(2, "0")
//           return {
//             time: `${hours}:${minutes}`,
//             fatigue_score: record.fatigue_score || 0,
//             eye_ratio: Number(record.eye_ratio) || 0,
//             blink_count: record.blink_count || 0,
//           }
//         })

//         setData(processed)
//         setError(null)
//       } catch (err) {
//         setError(err instanceof Error ? err.message : "Unknown error")
//       } finally {
//         setLoading(false)
//       }
//     }

//     fetchTrends()
//     const interval = setInterval(fetchTrends, 10000)
//     return () => clearInterval(interval)
//   }, [])

//   if (loading && !data.length) {
//     return (
//       <div className="flex items-center justify-center py-12 rounded-xl bg-[#1E293B] border border-gray-700">
//         <Loader2 className="w-8 h-8 text-[#22D3EE] animate-spin" />
//         <span className="ml-2 text-gray-300 font-medium">
//           Loading trends...
//         </span>
//       </div>
//     )
//   }

//   if (error && !data.length) {
//     return (
//       <div className="px-4 py-3 rounded-xl bg-red-900/20 border border-red-500/30">
//         <span className="text-red-400 font-medium">
//           Error loading trends: {error}
//         </span>
//       </div>
//     )
//   }

//   if (!data.length && !loading) {
//     return (
//       <div className="bg-[#1E293B] rounded-xl p-8 text-center relative overflow-hidden shadow-lg">
//         <p className="text-gray-300 font-medium">
//           No trend data available yet. Start the camera module to begin collecting data.
//         </p>
//       </div>
//     )
//   }

//   const commonProps = {
//     width: "100%",
//     height: 400,
//     margin: { top: 5, right: 30, left: 0, bottom: 5 },
//   }

//   return (
//     <div className="space-y-6">
//       <div className="flex gap-2">
//         {(["line", "area", "bar"] as const).map((type) => (
//           <button
//             key={type}
//             onClick={() => setChartType(type)}
//             className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
//               chartType === type
//                 ? "bg-gradient-to-r from-[#3B82F6] to-[#22D3EE] text-white shadow-lg hover:shadow-[0_0_20px_rgba(255,255,255,0.8)]"
//                 : "bg-[#1E293B] text-white hover:bg-gray-700/50"
//             }`}
//           >
//             {type.charAt(0).toUpperCase() + type.slice(1)}
//           </button>
//         ))}
//       </div>

//       <div className="bg-[#1E293B] rounded-xl p-6 relative overflow-hidden shadow-lg">
//         <h3 className="text-xl font-bold text-white mb-4">
//           Fatigue Score Trend
//         </h3>
//         <ResponsiveContainer width="100%" height={400}>
//           {chartType === "line" && (
//             <LineChart data={data} {...commonProps}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
//               <XAxis 
//                 dataKey="time" 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//               />
//               <YAxis 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//                 domain={[0, 100]} 
//               />
//               <Tooltip
//                 contentStyle={{
//                   backgroundColor: "#1E293B",
//                   border: "1px solid #374151",
//                   borderRadius: "0.5rem",
//                   color: "#FFFFFF",
//                 }}
//                 labelStyle={{ color: "#FFFFFF" }}
//               />
//               <Legend wrapperStyle={{ color: "#FFFFFF" }} />
//               <Line
//                 type="monotone"
//                 dataKey="fatigue_score"
//                 stroke="#3B82F6"
//                 strokeWidth={2}
//                 dot={{ fill: "#3B82F6", r: 4 }}
//                 activeDot={{ r: 6 }}
//                 name="Fatigue Score"
//               />
//             </LineChart>
//           )}
//           {chartType === "area" && (
//             <AreaChart data={data} {...commonProps}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
//               <XAxis 
//                 dataKey="time" 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//               />
//               <YAxis 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//                 domain={[0, 100]} 
//               />
//               <Tooltip
//                 contentStyle={{
//                   backgroundColor: "#1E293B",
//                   border: "1px solid #374151",
//                   borderRadius: "0.5rem",
//                   color: "#FFFFFF",
//                 }}
//                 labelStyle={{ color: "#FFFFFF" }}
//               />
//               <Legend wrapperStyle={{ color: "#FFFFFF" }} />
//               <Area
//                 type="monotone"
//                 dataKey="fatigue_score"
//                 fill="#3B82F6"
//                 fillOpacity={0.6}
//                 stroke="#3B82F6"
//                 strokeWidth={2}
//                 name="Fatigue Score"
//               />
//             </AreaChart>
//           )}
//           {chartType === "bar" && (
//             <BarChart data={data} {...commonProps}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
//               <XAxis 
//                 dataKey="time" 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//               />
//               <YAxis 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//                 domain={[0, 100]} 
//               />
//               <Tooltip
//                 contentStyle={{
//                   backgroundColor: "#1E293B",
//                   border: "1px solid #374151",
//                   borderRadius: "0.5rem",
//                   color: "#FFFFFF",
//                 }}
//                 labelStyle={{ color: "#FFFFFF" }}
//               />
//               <Legend wrapperStyle={{ color: "#FFFFFF" }} />
//               <Bar 
//                 dataKey="fatigue_score" 
//                 fill="#3B82F6"
//                 name="Fatigue Score"
//                 radius={[4, 4, 0, 0]}
//               />
//             </BarChart>
//           )}
//         </ResponsiveContainer>
//       </div>

//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//         <div className="bg-[#1E293B] rounded-xl p-6 relative overflow-hidden shadow-lg">
//           <h3 className="text-lg font-bold text-white mb-4">
//             Eye Ratio Trend
//           </h3>
//           <ResponsiveContainer width="100%" height={300}>
//             <LineChart data={data}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
//               <XAxis 
//                 dataKey="time" 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//               />
//               <YAxis 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//               />
//               <Tooltip
//                 contentStyle={{
//                   backgroundColor: "#1E293B",
//                   border: "1px solid #374151",
//                   borderRadius: "0.5rem",
//                   color: "#FFFFFF",
//                 }}
//                 labelStyle={{ color: "#FFFFFF" }}
//               />
//               <Line
//                 type="monotone"
//                 dataKey="eye_ratio"
//                 stroke="#22D3EE"
//                 strokeWidth={2}
//                 dot={{ fill: "#22D3EE", r: 3 }}
//                 activeDot={{ r: 5 }}
//                 name="Eye Ratio"
//               />
//             </LineChart>
//           </ResponsiveContainer>
//         </div>

//         <div className="bg-[#1E293B] rounded-xl p-6 relative overflow-hidden shadow-lg">
//           <h3 className="text-lg font-bold text-white mb-4">
//             Blink Count Trend
//           </h3>
//           <ResponsiveContainer width="100%" height={300}>
//             <BarChart data={data}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
//               <XAxis 
//                 dataKey="time" 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//               />
//               <YAxis 
//                 stroke="#9CA3AF"
//                 tick={{ fill: "#9CA3AF" }}
//               />
//               <Tooltip
//                 contentStyle={{
//                   backgroundColor: "#1E293B",
//                   border: "1px solid #374151",
//                   borderRadius: "0.5rem",
//                   color: "#FFFFFF",
//                 }}
//                 labelStyle={{ color: "#FFFFFF" }}
//               />
//               <Bar 
//                 dataKey="blink_count" 
//                 fill="#8B5CF6"
//                 name="Blink Count"
//                 radius={[4, 4, 0, 0]}
//               />
//             </BarChart>
//           </ResponsiveContainer>
//         </div>
//       </div>
//     </div>
//   )
// }
"use client"

import { useState, useEffect } from "react"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { Loader2 } from "lucide-react"

interface TrendData {
  time: string
  fatigue_score: number
  eye_ratio: number
  blink_count: number
}

export default function TrendsChart() {
  const [data, setData] = useState<TrendData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [chartType, setChartType] = useState<"line" | "area" | "bar">("line")

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true)
        const response = await fetch("/api/history")
        if (!response.ok) throw new Error("Failed to fetch trends")
        const rawData = await response.json()

        const processed = rawData.slice(-24).map((record: any) => {
          const date = new Date(record.timestamp)
          const hours = String(date.getHours()).padStart(2, "0")
          const minutes = String(date.getMinutes()).padStart(2, "0")
          return {
            time: `${hours}:${minutes}`,
            fatigue_score: record.fatigue_score || 0,
            eye_ratio: Number(record.eye_ratio) || 0,
            blink_count: record.blink_count || 0,
          }
        })

        setData(processed)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        setLoading(false)
      }
    }

    fetchTrends()
    const interval = setInterval(fetchTrends, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading && !data.length) {
    return (
      <div className="flex items-center justify-center py-12 rounded-xl bg-[#1E293B] border border-gray-700">
        <Loader2 className="w-8 h-8 text-[#22D3EE] animate-spin" />
        <span className="ml-2 text-gray-300 font-medium">
          Loading trends...
        </span>
      </div>
    )
  }

  if (error && !data.length) {
    return (
      <div className="px-4 py-3 rounded-xl bg-red-900/20 border border-red-500/30">
        <span className="text-red-400 font-medium">
          Error loading trends: {error}
        </span>
      </div>
    )
  }

  if (!data.length && !loading) {
    return (
      <div className="bg-[#1E293B] rounded-xl p-8 text-center relative overflow-hidden shadow-lg">
        <p className="text-gray-300 font-medium">
          No trend data available yet. Start the camera module to begin collecting data.
        </p>
      </div>
    )
  }

  const commonProps = {
    margin: { top: 5, right: 30, left: 0, bottom: 5 },
  }
  

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        {(["line", "area", "bar"] as const).map((type) => (
          <button
            key={type}
            onClick={() => setChartType(type)}
            className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
              chartType === type
                ? "bg-gradient-to-r from-[#3B82F6] to-[#22D3EE] text-white shadow-lg hover:shadow-[0_0_20px_rgba(255,255,255,0.8)]"
                : "bg-[#1E293B] text-white hover:bg-gray-700/50"
            }`}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {/* MAIN FATIGUE CHART */}
      <div className="bg-[#1E293B] rounded-xl p-6 relative overflow-hidden shadow-lg">
        <h3 className="text-xl font-bold text-white mb-4">
          Fatigue Score Trend
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <>
            {chartType === "line" && (
              <LineChart data={data} {...commonProps}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
                <YAxis stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1E293B",
                    border: "1px solid #374151",
                    borderRadius: "0.5rem",
                    color: "#FFFFFF",
                  }}
                  labelStyle={{ color: "#FFFFFF" }}
                />
                <Legend wrapperStyle={{ color: "#FFFFFF" }} />
                <Line
                  type="monotone"
                  dataKey="fatigue_score"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={{ fill: "#3B82F6", r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Fatigue Score"
                />
              </LineChart>
            )}

            {chartType === "area" && (
              <AreaChart data={data} {...commonProps}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
                <YAxis stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1E293B",
                    border: "1px solid #374151",
                    borderRadius: "0.5rem",
                    color: "#FFFFFF",
                  }}
                  labelStyle={{ color: "#FFFFFF" }}
                />
                <Legend wrapperStyle={{ color: "#FFFFFF" }} />
                <Area
                  type="monotone"
                  dataKey="fatigue_score"
                  fill="#3B82F6"
                  fillOpacity={0.6}
                  stroke="#3B82F6"
                  strokeWidth={2}
                  name="Fatigue Score"
                />
              </AreaChart>
            )}

            {chartType === "bar" && (
              <BarChart data={data} {...commonProps}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
                <YAxis stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1E293B",
                    border: "1px solid #374151",
                    borderRadius: "0.5rem",
                    color: "#FFFFFF",
                  }}
                  labelStyle={{ color: "#FFFFFF" }}
                />
                <Legend wrapperStyle={{ color: "#FFFFFF" }} />
                <Bar
                  dataKey="fatigue_score"
                  fill="#3B82F6"
                  name="Fatigue Score"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            )}
          </>
        </ResponsiveContainer>
      </div>

      {/* SECONDARY CHARTS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#1E293B] rounded-xl p-6 relative overflow-hidden shadow-lg">
          <h3 className="text-lg font-bold text-white mb-4">
            Eye Ratio Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
              <YAxis stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1E293B",
                  border: "1px solid #374151",
                  borderRadius: "0.5rem",
                  color: "#FFFFFF",
                }}
                labelStyle={{ color: "#FFFFFF" }}
              />
              <Line
                type="monotone"
                dataKey="eye_ratio"
                stroke="#22D3EE"
                strokeWidth={2}
                dot={{ fill: "#22D3EE", r: 3 }}
                activeDot={{ r: 5 }}
                name="Eye Ratio"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-[#1E293B] rounded-xl p-6 relative overflow-hidden shadow-lg">
          <h3 className="text-lg font-bold text-white mb-4">
            Blink Count Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
              <YAxis stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1E293B",
                  border: "1px solid #374151",
                  borderRadius: "0.5rem",
                  color: "#FFFFFF",
                }}
                labelStyle={{ color: "#FFFFFF" }}
              />
              <Bar
                dataKey="blink_count"
                fill="#8B5CF6"
                name="Blink Count"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
