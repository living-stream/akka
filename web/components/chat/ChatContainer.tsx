'use client'

import React, { useCallback, useRef, useEffect } from 'react'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { HumanAssistModal } from './HumanAssistModal'
import { useChatStore } from '@/store/chatStore'
import { streamChat, getConversation } from '@/lib/api'
import { generateId } from '@/lib/utils'
import { useHumanAssist } from '@/hooks/useHumanAssist'

export function ChatContainer() {
  const {
    messages,
    isStreaming,
    uid,
    addUserMessage,
    startAssistantMessage,
    appendToMessage,
    completeStream,
    loadMessages,
  } = useChatStore()
  
  const abortRef = useRef<(() => void) | null>(null)
  
  const {
    currentRequest,
    setCurrentRequest,
    resolveRequest,
  } = useHumanAssist()

  // 从后端加载对话历史
  useEffect(() => {
    async function loadConversation() {
      try {
        const conv = await getConversation(uid)
        if (conv.messages && conv.messages.length > 0) {
          loadMessages(conv.messages.map((m: any) => ({
            id: m.id || generateId(),
            role: m.role,
            content: m.content || '',
            thinking: m.thinking,
            browserSteps: m.browserSteps,
            timestamp: m.timestamp || Date.now(),
          })))
        }
      } catch (error) {
        console.error('Failed to load conversation:', error)
      }
    }
    loadConversation()
  }, [uid])

  const handleSend = useCallback(
    async (content: string) => {
      addUserMessage(content)
      startAssistantMessage()

      const { promise, abort } = streamChat(
        uid,
        content,
        (chunk) => {
          appendToMessage(chunk)
        },
        (error) => {
          console.error('Chat error:', error)
          appendToMessage(`\n\n❌ 发生错误: ${error.message}`)
          completeStream()
        },
        () => {
          completeStream()
          abortRef.current = null
        }
      )
      
      abortRef.current = abort
      await promise
    },
    [uid, addUserMessage, startAssistantMessage, appendToMessage, completeStream]
  )

  const handleStop = useCallback(() => {
    if (abortRef.current) {
      abortRef.current()
      abortRef.current = null
    }
    completeStream()
  }, [completeStream])

  return (
    <div className="flex h-full flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} isStreaming={isStreaming} />
      </div>

      {/* Input */}
      <div className="shrink-0 p-4 pt-0">
        <MessageInput onSend={handleSend} isStreaming={isStreaming} onStop={handleStop} />
      </div>

      {/* Human Assist Modal */}
      <HumanAssistModal
        isOpen={!!currentRequest}
        question={currentRequest?.question || ''}
        onResolve={(response) => {
          if (currentRequest) {
            resolveRequest(currentRequest.request_id, response)
          }
        }}
        onSkip={() => setCurrentRequest(null)}
      />
    </div>
  )
}
