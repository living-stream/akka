'use client'

import React, { useRef, useEffect } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { MessageItem } from './MessageItem'
import { MessageSquare } from 'lucide-react'
import type { Message } from '@/types'

interface MessageListProps {
  messages: Message[]
  isStreaming: boolean
}

export function MessageList({ messages, isStreaming }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center px-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800">
          <MessageSquare className="h-6 w-6 text-zinc-600 dark:text-zinc-400" />
        </div>
        <h2 className="text-xl font-medium text-zinc-900 dark:text-zinc-100 mb-4">
          开始对话
        </h2>
        <p className="mt-3 max-w-sm text-zinc-500 text-center max-w-xs mb-8">
          智能运营助手，帮你完成内容创作与运营工作
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {['写一篇咖啡笔记', '分析竞品账号', '定时发布任务'].map((text) => (
            <button
              key={text}
              className="px-3 py-1.5 text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
            >
              {text}
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <ScrollArea className="h-full" ref={scrollRef}>
      <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
      </div>
    </ScrollArea>
  )
}
