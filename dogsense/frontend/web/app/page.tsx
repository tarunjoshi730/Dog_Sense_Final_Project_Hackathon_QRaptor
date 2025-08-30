import { Dashboard } from "@/components/dashboard"
import { PetList } from "@/components/pet-list"
import { AlertPanel } from "@/components/alert-panel"
import { StatsCards } from "@/components/stats-cards"
import { RecentActivity } from "@/components/recent-activity"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">DogSense Dashboard</h1>
          <p className="text-gray-600">Smart Pet Health & Safety Monitor</p>
        </div>
        
        <StatsCards />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          <div className="lg:col-span-2">
            <Dashboard />
          </div>
          <div className="space-y-6">
            <AlertPanel />
            <RecentActivity />
          </div>
        </div>
        
        <div className="mt-8">
          <PetList />
        </div>
      </div>
    </div>
  )
}