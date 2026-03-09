export interface BrowserStep {
  step: number
  goal: string
  memory: string
  actions: any[]
  preview_url: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  thinking?: string
  browserSteps?: BrowserStep[]
  timestamp: number
  isStreaming?: boolean
}

export interface Task {
  task_id: string
  task_name: string
  task_instruction: string
  scheduled_time: string
  repeat: string
  status: 'pending' | 'running' | 'completed' | 'cancelled' | 'failed'
  created_at: string
  completed_at?: string
  error?: string
}

export interface Note {
  path: string
  title: string
  modified: string
  has_images: boolean
  images: string[]
  content_preview?: string
}

export interface UserProfile {
  soul: string
  memory: string
}
