'use client'

import React, { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Send, Square } from 'lucide-react'

interface MessageInputProps {
  onSend: (message: string) => void
  isStreaming: boolean
  onStop?: () => void
}

export function MessageInput({ onSend, isStreaming, onStop }: MessageInputProps) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (input.trim() && !isStreaming) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="p-4 border-t border-zinc-200 dark:border-zinc-800">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-end gap-2">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入你的需求..."
            className="flex-1 min-h-[40px] max-h-32 resize-none"
            disabled={isStreaming}
          />
          {isStreaming ? (
            <Button onClick={onStop} variant="secondary" className="h-10">
              <Square className="h-4 w-4 mr-1.5" />
              停止
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={!input.trim()} className="h-10">
              <Send className="h-4 w-4 mr-1.5" />
              发送
            </Button>
          )}
        </div>
        <div className="text-xs text-zinc-400 mt-2 text-center">
          Enter 发送 · Shift+Enter 换行
        </div>
      </div>
    </div>
  )
}
