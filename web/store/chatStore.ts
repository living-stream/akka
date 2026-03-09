import { create } from 'zustand'
import { Message } from '@/types'
import { generateId } from '@/lib/utils'

interface ChatState {
  messages: Message[]
  isStreaming: boolean
  uid: string

  // Actions
  setUid: (uid: string) => void
  addUserMessage: (content: string) => void
  startAssistantMessage: () => void
  appendToMessage: (chunk: string) => void
  completeStream: () => void
  clearMessages: () => void
  loadMessages: (messages: Message[]) => void
}

export const useChatStore = create<ChatState>()((set, get) => ({
  messages: [],
  isStreaming: false,
  uid: 'default_user',

  setUid: (uid) => set({ uid }),

  addUserMessage: (content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: generateId(),
          role: 'user',
          content,
          timestamp: Date.now(),
        },
      ],
      isStreaming: true,
    })),

  startAssistantMessage: () =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: generateId(),
          role: 'assistant',
          content: '',
          timestamp: Date.now(),
        },
      ],
    })),

      appendToMessage: (chunk) =>
        set((state) => {
          const messages = [...state.messages]
          const lastMessage = messages[messages.length - 1]

          if (lastMessage?.role === 'assistant') {
            const currentContent = lastMessage.content
            const currentThinking = lastMessage.thinking || ''
            const currentBrowserSteps = (lastMessage as any).browserSteps || []

            let newContent = currentContent
            let newThinking = currentThinking
            let newBrowserSteps = currentBrowserSteps

            // 解析 JSON 格式的 chunk
            try {
              const data = JSON.parse(chunk.trim())
              if (data.type === 'thinking') {
                newThinking += data.content
              } else if (data.type === 'content') {
                newContent += data.content
              } else if (data.type === 'browser') {
                // 添加浏览器步骤
                newBrowserSteps = [...currentBrowserSteps, {
                  step: data.step,
                  goal: data.goal,
                  memory: data.memory,
                  actions: data.actions,
                  preview_url: data.preview_url
                }]
              }
            } catch (e) {
              // 如果不是 JSON 格式，当作普通文本处理
              newContent += chunk
            }

            messages[messages.length - 1] = {
              ...lastMessage,
              content: newContent,
              thinking: newThinking,
              browserSteps: newBrowserSteps,
              isStreaming: true,
            }
          }

          return { messages }
        }),

      completeStream: () =>
        set((state) => ({
          isStreaming: false,
          messages: state.messages.map((m) => {
            const { _buffer, ...rest } = m as any
            return { ...rest, isStreaming: false }
          }),
        })),

      clearMessages: () => set({ messages: [], isStreaming: false }),

      loadMessages: (messages) => set({ messages }),
}))

