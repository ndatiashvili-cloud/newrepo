import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Select from '@/components/ui/Select'
import { LoadingSpinner } from '@/components/ui/Loading'
import { Badge } from '@/components/ui/Badge'
import { devicesAPI, zabbixAPI } from '@/services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Activity, TrendingUp, Clock, Database } from 'lucide-react'
import { toast } from 'sonner'

export default function ZabbixMetrics() {
  const [selectedDevice, setSelectedDevice] = useState<string>('')
  const [selectedMetric, setSelectedMetric] = useState<string>('')
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h')

  // Get all devices
  const { data: devicesResponse } = useQuery({
    queryKey: ['devices'],
    queryFn: () => devicesAPI.getAll(),
  })

  const devices = devicesResponse?.data || []

  // Calculate time range
  const getTimeRange = () => {
    const now = Math.floor(Date.now() / 1000)
    const ranges = {
      '1h': now - 3600,
      '24h': now - 86400,
      '7d': now - 604800,
      '30d': now - 2592000,
    }
    return { timeFrom: ranges[timeRange], timeTo: now }
  }

  // Get metrics for selected device
  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ['zabbix-metrics', selectedDevice, timeRange],
    queryFn: () => {
      if (!selectedDevice) return null
      const { timeFrom, timeTo } = getTimeRange()
      return zabbixAPI.getHostMetrics(selectedDevice, timeFrom, timeTo)
    },
    enabled: !!selectedDevice,
  })

  const metrics = metricsData?.data?.metrics || []

  // Prepare chart data
  const prepareChartData = (metric: any) => {
    if (!metric.history || metric.history.length === 0) return []

    return metric.history.map((point: any) => ({
      time: new Date(point.timestamp * 1000).toLocaleTimeString(),
      timestamp: point.timestamp,
      value: parseFloat(point.value) || 0,
    }))
  }

  // Filter metrics by search
  const filteredMetrics = selectedMetric
    ? metrics.filter((m: any) => m.name.toLowerCase().includes(selectedMetric.toLowerCase()) || m.key.toLowerCase().includes(selectedMetric.toLowerCase()))
    : metrics

  const selectedDeviceName = devices.find((d: any) => d.hostid === selectedDevice)?.display_name || 'Select Device'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Zabbix Metrics</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            View all metrics sent via Zabbix sender
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Device
              </label>
              <Select
                value={selectedDevice}
                onChange={(e) => setSelectedDevice(e.target.value)}
                options={[
                  { value: '', label: 'Select Device...' },
                  ...devices.map((d: any) => ({
                    value: d.hostid,
                    label: d.display_name || d.hostname || d.ip,
                  })),
                ]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Range
              </label>
              <Select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value as any)}
                options={[
                  { value: '1h', label: 'Last Hour' },
                  { value: '24h', label: 'Last 24 Hours' },
                  { value: '7d', label: 'Last 7 Days' },
                  { value: '30d', label: 'Last 30 Days' },
                ]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search Metric
              </label>
              <input
                type="text"
                placeholder="Filter metrics..."
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-ward-green focus:border-transparent"
              />
            </div>

            <div className="flex items-end">
              <Button
                onClick={() => {
                  if (!selectedDevice) {
                    toast.error('Please select a device')
                    return
                  }
                  // Refetch metrics
                }}
                className="w-full"
              >
                <Activity className="h-4 w-4 mr-2" />
                Refresh Metrics
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Metrics List */}
      {selectedDevice && (
        <div>
          {metricsLoading ? (
            <Card>
              <CardContent className="p-12 text-center">
                <LoadingSpinner />
                <p className="mt-4 text-gray-500">Loading metrics...</p>
              </CardContent>
            </Card>
          ) : filteredMetrics.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Database className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-500">No metrics found for this device</p>
                <p className="text-sm text-gray-400 mt-2">
                  Ensure Zabbix sender is configured and sending metrics
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredMetrics.map((metric: any) => {
                const chartData = prepareChartData(metric)
                const lastValue = metric.last_value || 'N/A'
                const units = metric.units || ''

                return (
                  <Card key={metric.itemid} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="text-lg">{metric.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {metric.key}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {/* Current Value */}
                      <div className="mb-4">
                        <div className="flex items-baseline gap-2">
                          <span className="text-3xl font-bold text-ward-green">
                            {typeof lastValue === 'number' ? lastValue.toFixed(2) : lastValue}
                          </span>
                          {units && (
                            <span className="text-sm text-gray-500">{units}</span>
                          )}
                        </div>
                        <p className="text-xs text-gray-400 mt-1">
                          Last updated: {metric.history && metric.history.length > 0
                            ? new Date(metric.history[metric.history.length - 1].timestamp * 1000).toLocaleString()
                            : 'Never'}
                        </p>
                      </div>

                      {/* Chart */}
                      {chartData.length > 0 ? (
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                              <XAxis
                                dataKey="time"
                                stroke="#6b7280"
                                fontSize={12}
                                tick={{ fill: '#6b7280' }}
                              />
                              <YAxis
                                stroke="#6b7280"
                                fontSize={12}
                                tick={{ fill: '#6b7280' }}
                              />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: '#fff',
                                  border: '1px solid #e5e7eb',
                                  borderRadius: '8px',
                                }}
                              />
                              <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#5EBBA8"
                                strokeWidth={2}
                                dot={false}
                                name={metric.name}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      ) : (
                        <div className="h-64 flex items-center justify-center text-gray-400">
                          <div className="text-center">
                            <TrendingUp className="h-8 w-8 mx-auto mb-2 opacity-50" />
                            <p className="text-sm">No historical data</p>
                          </div>
                        </div>
                      )}

                      {/* Stats */}
                      {chartData.length > 0 && (
                        <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                          <div>
                            <p className="text-xs text-gray-500">Min</p>
                            <p className="text-sm font-semibold">
                              {Math.min(...chartData.map((d: any) => d.value)).toFixed(2)} {units}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Avg</p>
                            <p className="text-sm font-semibold">
                              {(chartData.reduce((sum: number, d: any) => sum + d.value, 0) / chartData.length).toFixed(2)} {units}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Max</p>
                            <p className="text-sm font-semibold">
                              {Math.max(...chartData.map((d: any) => d.value)).toFixed(2)} {units}
                            </p>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </div>
      )}

      {!selectedDevice && (
        <Card>
          <CardContent className="p-12 text-center">
            <Activity className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">Select a device to view metrics</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
