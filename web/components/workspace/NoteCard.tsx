'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { FileText, Folder, Loader2 } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'
import { getNoteImageUrl, getNoteContent } from '@/lib/api'
import { useChatStore } from '@/store/chatStore'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import type { Note } from '@/types'

interface NoteCardProps {
  note: Note
}

export function NoteCard({ note }: NoteCardProps) {
  const { uid } = useChatStore()
  const [isOpen, setIsOpen] = useState(false)
  const [fullContent, setFullContent] = useState('')
  const [isLoadingContent, setIsLoadingContent] = useState(false)
  const noteFolder = note.path.split('/').pop() || ''
  const displayImages = note.images?.slice(0, 3) || []
  const hasImages = displayImages.length > 0

  useEffect(() => {
    if (isOpen && !fullContent) {
      setIsLoadingContent(true)
      getNoteContent(uid, noteFolder)
        .then((data) => setFullContent(data.content || ''))
        .finally(() => setIsLoadingContent(false))
    }
  }, [isOpen, uid, noteFolder])

  return (
    <>
      <Card
        className="group cursor-pointer overflow-hidden transition-all hover:shadow-lg hover:border-zinc-300 dark:hover:border-zinc-700"
        onClick={() => setIsOpen(true)}
      >
        <CardContent className="p-0">
          {hasImages ? (
            <div className="relative h-40 bg-zinc-100 dark:bg-zinc-800">
              {displayImages.length === 1 ? (
                <img
                  src={getNoteImageUrl(uid, noteFolder, displayImages[0])}
                  alt={note.title}
                  className="w-full h-full object-cover"
                />
              ) : displayImages.length === 2 ? (
                <div className="grid grid-cols-2 h-full">
                  {displayImages.map((img, idx) => (
                    <img
                      key={idx}
                      src={getNoteImageUrl(uid, noteFolder, img)}
                      alt={`${note.title} - ${idx + 1}`}
                      className="w-full h-full object-cover"
                    />
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-3 h-full">
                  {displayImages.map((img, idx) => (
                    <img
                      key={idx}
                      src={getNoteImageUrl(uid, noteFolder, img)}
                      alt={`${note.title} - ${idx + 1}`}
                      className="w-full h-full object-cover"
                    />
                  ))}
                </div>
              )}
              {note.images.length > 3 && (
                <div className="absolute right-2 top-2 rounded-full bg-black/60 px-2 py-1 text-xs text-white">
                  +{note.images.length - 3}
                </div>
              )}
            </div>
          ) : (
            <div className="relative h-32 bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800 dark:to-zinc-900">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white/80 dark:bg-zinc-800/80 shadow-lg">
                  <FileText className="h-7 w-7 text-zinc-500 dark:text-zinc-400" />
                </div>
              </div>
            </div>
          )}

          <div className="p-4">
            <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 line-clamp-1 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors">
              {note.title}
            </h3>
            
            {note.content_preview && (
              <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400 line-clamp-2">
                {note.content_preview}
              </p>
            )}
            
            <div className="mt-3 flex items-center justify-between text-xs text-zinc-400 dark:text-zinc-500">
              <div className="flex items-center gap-1">
                <Folder className="h-3 w-3" />
                <span className="truncate max-w-[100px]">{noteFolder}</span>
              </div>
              <span>{formatRelativeTime(note.modified)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl">{note.title}</DialogTitle>
            <div className="flex items-center gap-4 text-sm text-zinc-500 dark:text-zinc-400">
              <div className="flex items-center gap-1">
                <Folder className="h-4 w-4" />
                <span>{noteFolder}</span>
              </div>
              <span>修改于 {formatRelativeTime(note.modified)}</span>
            </div>
          </DialogHeader>

          {note.images && note.images.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-3">
                图片 ({note.images.length})
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {note.images.map((img, idx) => (
                  <div
                    key={idx}
                    className="relative aspect-square rounded-lg overflow-hidden bg-zinc-100 dark:bg-zinc-800"
                  >
                    <img
                      src={getNoteImageUrl(uid, noteFolder, img)}
                      alt={`${note.title} - ${idx + 1}`}
                      className="w-full h-full object-cover hover:scale-105 transition-transform cursor-pointer"
                      onClick={() => window.open(getNoteImageUrl(uid, noteFolder, img), '_blank')}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4">
            <h4 className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-3">
              内容
            </h4>
            <div className="bg-zinc-50 dark:bg-zinc-900 rounded-lg p-4">
              {isLoadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-zinc-400" />
                </div>
              ) : (
                <pre className="whitespace-pre-wrap text-sm text-zinc-700 dark:text-zinc-300 font-sans">
                  {fullContent || note.content_preview || '暂无内容'}
                </pre>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
