const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface RunRequest {
  uid: string
  brief: string
}

export interface ScheduleRequest {
  uid: string
  task_name: string
  task_instruction: string
  scheduled_time: string
  repeat?: string
}

export interface Task {
  task_id: string
  task_name: string
  task_instruction: string
  scheduled_time: string
  repeat: string
  status: 'pending' | 'completed' | 'cancelled' | 'failed'
  created_at: string
  completed_at?: string
  error?: string
}

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface Conversation {
  created_at: string
  updated_at: string
  messages: Message[]
}

export interface Note {
  path: string
  title: string
  modified: string
  has_images: boolean
  images: string[]
  content_preview?: string
}

export function getNoteImageUrl(uid: string, noteFolder: string, imageName: string): string {
  return `${API_BASE}/workspace/${uid}/images/${noteFolder}/${imageName}`
}

// 流式聊天
export function streamChat(
  uid: string,
  message: string,
  onChunk: (chunk: string) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): { promise: Promise<void>; abort: () => void } {
  const controller = new AbortController()
  
  const promise = async () => {
    try {
      const response = await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid, brief: message }),
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No response body')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        
        // 按行分割，处理完整的 JSON 行
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''  // 保留最后一个不完整的行
        
        for (const line of lines) {
          if (line.trim()) {
            onChunk(line)
          }
        }
      }
      
      // 处理剩余的 buffer
      if (buffer.trim()) {
        onChunk(buffer)
      }

      onComplete?.()
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        console.log('Request aborted by user')
        onComplete?.()
      } else {
        onError?.(error as Error)
      }
    }
  }
  
  return {
    promise: promise(),
    abort: () => controller.abort()
  }
}

// 获取对话历史
export async function getConversation(uid: string): Promise<Conversation> {
  const response = await fetch(`${API_BASE}/conversation/${uid}`)
  if (!response.ok) {
    return { created_at: '', updated_at: '', messages: [] }
  }
  return response.json()
}

// 获取定时任务列表
export async function getTasks(uid: string): Promise<{ tasks: Task[] }> {
  const response = await fetch(`${API_BASE}/tasks/${uid}`)
  return response.json()
}

// 创建定时任务
export async function createTask(request: ScheduleRequest): Promise<{ task_id: string; message: string }> {
  const response = await fetch(`${API_BASE}/schedule`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  return response.json()
}

// 取消定时任务
export async function cancelTask(uid: string, taskId: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/tasks/${uid}/${taskId}`, {
    method: 'DELETE',
  })
  return response.json()
}

// 获取工作区笔记
export async function getNotes(uid: string): Promise<{ notes: Note[] }> {
  try {
    const response = await fetch(`${API_BASE}/workspace/${uid}`)
    if (!response.ok) {
      return { notes: [] }
    }
    return response.json()
  } catch {
    return { notes: [] }
  }
}

// 获取笔记完整内容
export async function getNoteContent(uid: string, noteFolder: string): Promise<{ content: string }> {
  try {
    const response = await fetch(`${API_BASE}/workspace/${uid}/notes/${noteFolder}/copywriting.md`)
    if (!response.ok) {
      return { content: '' }
    }
    return response.json()
  } catch {
    return { content: '' }
  }
}

// 获取用户配置
export async function getUserProfile(uid: string): Promise<{ soul: string; memory: string }> {
  const response = await fetch(`${API_BASE}/user/${uid}/profile`)
  return response.json()
}

// 更新用户人设
export async function updateSoul(uid: string, content: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/user/${uid}/soul`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return response.json()
}

// 健康检查
export async function healthCheck(): Promise<{ status: string; scheduler_running: boolean }> {
  const response = await fetch(`${API_BASE}/health`)
  return response.json()
}
