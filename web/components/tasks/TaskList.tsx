'use client'

import React, { useEffect, useState } from 'react'
import { TaskCard } from './TaskCard'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Clock, Plus, Calendar, Sparkles } from 'lucide-react'
import { useTaskStore } from '@/store/taskStore'
import { getTasks, cancelTask } from '@/lib/api'
import { useChatStore } from '@/store/chatStore'

export function TaskList() {
  const { tasks, setTasks, removeTask, isLoading, setLoading } = useTaskStore()
  const { uid } = useChatStore()
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    loadTasks()
  }, [uid])

  const loadTasks = async () => {
    setLoading(true)
    try {
      const { tasks: fetchedTasks } = await getTasks(uid)
      setTasks(fetchedTasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (taskId: string) => {
    try {
      await cancelTask(uid, taskId)
      removeTask(taskId)
    } catch (error) {
      console.error('Failed to cancel task:', error)
    }
  }

  const pendingTasks = tasks.filter((t) => t.status === 'pending')
  const completedTasks = tasks.filter((t) => t.status !== 'pending')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            定时任务
          </h2>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            管理你的计划任务
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          创建任务
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-100 dark:bg-zinc-800">
              <Clock className="h-6 w-6 text-zinc-600 dark:text-zinc-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                {pendingTasks.length}
              </p>
              <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">待执行</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-100 dark:bg-zinc-800">
              <Sparkles className="h-6 w-6 text-zinc-600 dark:text-zinc-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                {completedTasks.length}
              </p>
              <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">已完成</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-100 dark:bg-zinc-800">
              <Calendar className="h-6 w-6 text-zinc-600 dark:text-zinc-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                {tasks.length}
              </p>
              <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">总任务</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Task Lists */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-400 border-t-transparent dark:border-zinc-500" />
        </div>
      ) : (
        <>
          {pendingTasks.length > 0 && (
            <div>
              <h3 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                待执行任务
              </h3>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {pendingTasks.map((task) => (
                  <TaskCard key={task.task_id} task={task} onCancel={handleCancel} />
                ))}
              </div>
            </div>
          )}

          {completedTasks.length > 0 && (
            <div>
              <h3 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                历史任务
              </h3>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {completedTasks.map((task) => (
                  <TaskCard key={task.task_id} task={task} />
                ))}
              </div>
            </div>
          )}

          {tasks.length === 0 && (
            <Card className="py-12">
              <CardContent className="flex flex-col items-center justify-center text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800">
                  <Clock className="h-8 w-8 text-zinc-400" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                  暂无定时任务
                </h3>
                <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                  通过对话告诉助手创建定时任务，例如"明天早上9点发布笔记"
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
