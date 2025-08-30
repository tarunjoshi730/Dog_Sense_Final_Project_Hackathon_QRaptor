"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface PetData {
  id: string
  name: string
  heartRate: number
  temperature: number
  activityLevel: number
  location: {
    lat: number
    lng: number
  }
  lastUpdate: string
}

interface ChartData {
  time: string
  heartRate: number
  temperature: number
  activity: number
}

export function Dashboard() {
  const [selectedPet, setSelectedPet] = useState<string>("1")
  const [petData, setPetData] = useState<PetData[]>([])
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [isConnected, setIsConnected] = useState(true)

  // Mock data - replace with real WebSocket connection
  useEffect(() => {
    const mockData: PetData[] = [
      {
        id: "1",
        name: "Max",
        heartRate: 85,
        temperature: 38.5,
        activityLevel: 65,
        location: { lat: 40.7128, lng: -74.0060 },
        lastUpdate: "2 minutes ago"
      },
      {
        id: "2",
        name: "Bella",
        heartRate: 78,
        temperature: 38.2,
        activityLevel: 45,
        location: { lat: 40.7589, lng: -73.9851 },
        lastUpdate: "5 minutes ago"
      }
    ]
    
    const mockChartData: ChartData[] = [
      { time: "00:00", heartRate: 82, temperature: 38.4, activity: 60 },
      { time: "04:00", heartRate: 75, temperature: 38.2, activity: 20 },
      { time: "08:00", heartRate: 88, temperature: 38.6, activity: 85 },
      { time: "12:00", heartRate: 92, temperature: 38.8, activity: 75 },
      { time: "16:00", heartRate: 85, temperature: 38.5, activity: 65 },
      { time: "20:00", heartRate: 80, temperature: 38.3, activity: 40 },
    ]
    
    setPetData(mockData)
    setChartData(mockChartData)
  }, [])

  const currentPet = petData.find(p => p.id === selectedPet) || petData[0]

  const getStatusColor = (value: number, type: string) => {
    switch(type) {
      case 'heartRate':
        if (value < 60 || value > 120) return "text-red-500"
        if (value < 70 || value > 100) return "text-yellow-500"
        return "text-green-500"
      case 'temperature':
        if (value < 37.5 || value > 39.5) return "text-red-500"
        if (value < 38 || value > 39) return "text-yellow-500"
        return "text-green-500"
      default:
        return "text-gray-700"
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Real-time Monitoring</h2>
        <Badge variant={isConnected ? "default" : "destructive"}>
          {isConnected ? "Online" : "Offline"}
        </Badge>
      </div>

      <Tabs value={selectedPet} onValueChange={setSelectedPet}>
        <TabsList>
          {petData.map(pet => (
            <TabsTrigger key={pet.id} value={pet.id}>
              {pet.name}
            </TabsTrigger>
          ))}
        </TabsList>
        
        {petData.map(pet => (
          <TabsContent key={pet.id} value={pet.id} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Heart Rate</CardTitle>
                  <CardDescription>Current BPM</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{pet.heartRate}</div>
                  <p className={`text-xs ${getStatusColor(pet.heartRate, 'heartRate')}`}>
                    {pet.heartRate < 60 ? 'Low' : pet.heartRate > 120 ? 'High' : 'Normal'}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Temperature</CardTitle>
                  <CardDescription>Body temperature °C</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{pet.temperature}°</div>
                  <p className={`text-xs ${getStatusColor(pet.temperature, 'temperature')}`}>
                    {pet.temperature < 37.5 ? 'Low' : pet.temperature > 39.5 ? 'High' : 'Normal'}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Activity Level</CardTitle>
                  <CardDescription>Current activity</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{pet.activityLevel}%</div>
                  <p className="text-xs text-gray-500">
                    {pet.activityLevel < 30 ? 'Resting' : pet.activityLevel > 70 ? 'Active' : 'Moderate'}
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Vital Signs Trend</CardTitle>
                <CardDescription>Last 24 hours</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="heartRate"
                      stroke="#ef4444"
                      strokeWidth={2}
                      name="Heart Rate"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="temperature"
                      stroke="#f97316"
                      strokeWidth={2}
                      name="Temperature"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Activity Pattern</CardTitle>
                <CardDescription>Activity levels throughout the day</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="activity"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}