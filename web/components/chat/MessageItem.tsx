'use client'

import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'
import { User, Bot, ChevronDown } from 'lucide-react'
import type { Message } from '@/types'

interface MessageItemProps {
  message: Message
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user'
  const hasThinking = message.thinking && message.thinking.length > 0
  const hasBrowserSteps = message.browserSteps && message.browserSteps.length > 0
  const [showThinking, setShowThinking] = useState(false)

  return (
    <div
      className={cn(
        'py-5 px-6',
        !isUser && 'bg-zinc-50/80 dark:bg-zinc-900/50'
      )}
    >
      <div className="flex gap-4 max-w-2xl mx-auto">
        <div
          className={cn(
            'flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium',
            isUser ? 'bg-zinc-900 dark:bg-zinc-100' : 'bg-zinc-100 dark:bg-zinc-800'
          )}
        >
          {isUser ? (
            <User className="h-3.5 w-3.5 text-white dark:text-zinc-900" />
          ) : (
            <Bot className="h-3.5 w-3.5 text-zinc-600 dark:text-zinc-400" />
          )}
        </div>

        <div className="flex-1 min-w-0 -mt-0.5 flex flex-col gap-3">
          <div className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
            {isUser ? '你' : 'AutoVen'}
          </div>

          {hasThinking && (
            <details className="group/details">
              <summary 
                className="cursor-pointer text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-1 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors"
                onClick={() => setShowThinking(!showThinking)}
              >
                <ChevronDown className={cn(
                  'w-3.5 h-3.5 transition-transform',
                  showThinking && 'rotate-180'
                )} />
                <span>思考过程</span>
              </summary>
              {showThinking && (
                <div className="mt-2 pl-3 border-l-2 border-zinc-300 dark:border-zinc-600">
                  <pre className="text-xs text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap font-mono leading-relaxed">
                    {message.thinking}
                  </pre>
                </div>
              )}
            </details>
          )}

          {hasBrowserSteps && (
            <details className="group/details" open={message.isStreaming}>
              <summary className="cursor-pointer text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-1 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors">
                <ChevronDown className="w-3.5 h-3.5 transition-transform group-open/details:rotate-180" />
                <span>浏览器执行步骤 ({message.browserSteps!.length}步)</span>
              </summary>
              <div className="mt-2 space-y-2">
                {message.browserSteps!.map((step, index) => (
                  <div key={index} className="pl-3 border-l-2 border-blue-300 dark:border-blue-600">
                    <div className="text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                      Step {step.step}: {step.goal}
                    </div>
                    {step.memory && step.memory !== 'N/A' && (
                      <div className="text-xs text-zinc-600 dark:text-zinc-400 mb-1">
                        <span className="font-medium">记忆:</span> {step.memory}
                      </div>
                    )}
                    {step.actions && step.actions.length > 0 && (
                      <div className="text-xs text-zinc-600 dark:text-zinc-400">
                        <span className="font-medium">动作:</span>
                        <ul className="list-none ml-2 space-y-1 mt-1">
                          {step.actions.map((action: any, i) => (
                            <li key={i} className="font-mono bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded text-zinc-700 dark:text-zinc-300 break-all">
                              {typeof action === 'string' ? action : Object.keys(action).map(key => (
                                <span key={key}>
                                  <span className="text-blue-600 dark:text-blue-400 font-semibold">{key}</span>
                                  <span className="mx-1">:</span>
                                  <span>{typeof action[key] === 'object' ? JSON.stringify(action[key]) : String(action[key])}</span>
                                </span>
                              ))}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {step.preview_url && (
                      <div className="mt-1">
                        <a 
                          href={step.preview_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-red-600 dark:text-red-400 hover:underline"
                        >
                          🔴 需要人工操作 - 点击操作远端浏览器
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </details>
          )}

          <div className="prose prose-sm prose-zinc dark:prose-invert max-w-none prose-p:my-0 prose-p:leading-relaxed">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || ''}
            </ReactMarkdown>
          </div>

          {message.isStreaming && !message.content && !message.thinking && !message.browserSteps && (
            <div className="flex items-center gap-1 text-zinc-400">
              <span className="text-xs">正在思考...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
