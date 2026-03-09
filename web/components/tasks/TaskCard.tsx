'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Clock, Trash2, Repeat, Calendar, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'
import type { Task } from '@/types'

interface TaskCardProps {
  task: Task
  onCancel?: (taskId: string) => void
}

const statusConfig = {
  pending: {
    icon: Clock,
    color: 'text-zinc-600 dark:text-zinc-400',
    bg: 'bg-zinc-100 dark:bg-zinc-800',
    label: '待执行',
  },
  running: {
    icon: Loader2,
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    label: '运行中',
    animate: true,
  },
  completed: {
    icon: CheckCircle,
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-50 dark:bg-green-950/30',
    label: '已完成',
  },
  cancelled: {
    icon: XCircle,
    color: 'text-zinc-400',
    bg: 'bg-zinc-50 dark:bg-zinc-950/30',
    label: '已取消',
  },
  failed: {
    icon: AlertCircle,
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-50 dark:bg-red-950/30',
    label: '失败',
  },
}

const repeatConfig = {
  none: '一次性',
  daily: '每天',
  weekly: '每周',
  monthly: '每月',
}

export function TaskCard({ task, onCancel }: TaskCardProps) {
  const status = statusConfig[task.status]
  const StatusIcon = status.icon

  return (
    <Card className="group overflow-hidden transition-all hover:shadow-lg hover:border-zinc-300 dark:hover:border-zinc-700">
      <CardContent className="p-0">
        {/* Header with gradient */}
        <div className={cn('px-5 py-3', status.bg)}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <StatusIcon className={cn('h-4 w-4', status.color, status.animate && 'animate-spin')} />
              <span className={cn('text-sm font-medium', status.color)}>
                {status.label}
              </span>
            </div>
            {task.repeat !== 'none' && (
              <div className="flex items-center gap-1 text-xs text-zinc-500 dark:text-zinc-400">
                <Repeat className="h-3 w-3" />
                {repeatConfig[task.repeat as keyof typeof repeatConfig]}
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-5">
          <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
            {task.task_name}
          </h3>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400 line-clamp-2">
            {task.task_instruction}
          </p>

          {/* Time */}
          <div className="mt-4 flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400">
            <Calendar className="h-4 w-4" />
            <span>{task.scheduled_time}</span>
          </div>

          {/* Actions */}
          {task.status === 'pending' && onCancel && (
            <div className="mt-4 flex justify-end">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onCancel(task.task_id)}
                className="text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-zinc-300 dark:hover:bg-zinc-800"
              >
                <Trash2 className="h-4 w-4 mr-1" />
                取消任务
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

import { cn } from '@/lib/utils'
