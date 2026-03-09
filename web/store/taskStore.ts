import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Task } from '@/types'

interface TaskState {
  tasks: Task[]
  isLoading: boolean

  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (taskId: string, updates: Partial<Task>) => void
  removeTask: (taskId: string) => void
  setLoading: (loading: boolean) => void
}

export const useTaskStore = create<TaskState>()(
  persist(
    (set) => ({
      tasks: [],
      isLoading: false,

      setTasks: (tasks) => set({ tasks }),

      addTask: (task) =>
        set((state) => ({
          tasks: [...state.tasks, task],
        })),

      updateTask: (taskId, updates) =>
        set((state) => ({
          tasks: state.tasks.map((t) =>
            t.task_id === taskId ? { ...t, ...updates } : t
          ),
        })),

      removeTask: (taskId) =>
        set((state) => ({
          tasks: state.tasks.filter((t) => t.task_id !== taskId),
        })),

      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'task-storage',
    }
  )
)
