'use client'

import React, { useEffect, useState } from 'react'
import { NoteCard } from './NoteCard'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { RefreshCw, FolderOpen, AlertCircle } from 'lucide-react'
import { useChatStore } from '@/store/chatStore'
import { getNotes } from '@/lib/api'
import type { Note } from '@/types'

export function NoteList() {
  const { uid } = useChatStore()
  const [notes, setNotes] = useState<Note[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadNotes()
  }, [uid])

  const loadNotes = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const { notes: fetchedNotes } = await getNotes(uid)
      setNotes(fetchedNotes || [])
    } catch (err) {
      console.error('Failed to load notes:', err)
      setError('加载笔记失败，请检查后端服务是否正常运行')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            工作区
          </h2>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            已生成的内容和笔记
          </p>
        </div>
        <Button variant="outline" onClick={loadNotes} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          刷新
        </Button>
      </div>

      {/* Notes Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-400 border-t-transparent dark:border-zinc-500" />
        </div>
      ) : error ? (
        <Card className="py-12 border-red-200 dark:border-red-900">
          <CardContent className="flex flex-col items-center justify-center text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
              <AlertCircle className="h-8 w-8 text-red-500" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
              加载失败
            </h3>
            <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
              {error}
            </p>
            <Button variant="outline" onClick={loadNotes} className="mt-4">
              重试
            </Button>
          </CardContent>
        </Card>
      ) : notes.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {notes.map((note, index) => (
            <NoteCard key={note.path + index} note={note} />
          ))}
        </div>
      ) : (
        <Card className="py-12">
          <CardContent className="flex flex-col items-center justify-center text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800">
              <FolderOpen className="h-8 w-8 text-zinc-400" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
              暂无笔记
            </h3>
            <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
              通过对话生成内容，例如"帮我写一篇关于咖啡的笔记"
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
