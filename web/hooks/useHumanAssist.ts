import { useState, useEffect, useCallback } from 'react'

interface HumanAssistRequest {
  request_id: string
  question: string
  created_at: string
}

export function useHumanAssist() {
  const [pendingRequests, setPendingRequests] = useState<HumanAssistRequest[]>([])
  const [currentRequest, setCurrentRequest] = useState<HumanAssistRequest | null>(null)

  const fetchPendingRequests = useCallback(async () => {
    try {
      const response = await fetch('/api/human-assist/pending')
      const data = await response.json()
      setPendingRequests(data.requests || [])
      
      if (data.requests?.length > 0 && !currentRequest) {
        setCurrentRequest(data.requests[0])
      }
    } catch (error) {
      console.error('Failed to fetch pending requests:', error)
    }
  }, [currentRequest])

  const resolveRequest = useCallback(async (requestId: string, response: string) => {
    try {
      const res = await fetch(`/api/human-assist/${requestId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response }),
      })
      
      if (res.ok) {
        setCurrentRequest(null)
        setPendingRequests(prev => prev.filter(r => r.request_id !== requestId))
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to resolve request:', error)
      return false
    }
  }, [])

  useEffect(() => {
    const interval = setInterval(fetchPendingRequests, 2000)
    return () => clearInterval(interval)
  }, [fetchPendingRequests])

  return {
    pendingRequests,
    currentRequest,
    setCurrentRequest,
    resolveRequest,
  }
}
