'use client'

import { useChatStore } from '@/store/chatStore'
import { streamChat } from '@/lib/api'
import { useCallback } from 'react'

export function useChat() {
  const {
    messages,
    isStreaming,
    uid,
    addUserMessage,
    startAssistantMessage,
    appendToMessage,
    completeStream,
    clearMessages,
  } = useChatStore()

  const send = useCallback(
    async (content: string) => {
      addUserMessage(content)
      startAssistantMessage()

      await streamChat(
        uid,
        content,
        (chunk) => appendToMessage(chunk),
        (error) => {
          appendToMessage(`\n\n❌ 发生错误: ${error.message}`)
          completeStream()
        },
        () => completeStream()
      )
    },
    [uid, addUserMessage, startAssistantMessage, appendToMessage, completeStream]
  )

  return {
    messages,
    isStreaming,
    send,
    clear: clearMessages,
    uid,
  }
}
