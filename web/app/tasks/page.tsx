'use client'

import { Sidebar } from '@/components/Sidebar'
import { TaskList } from '@/components/tasks'

export default function TasksPage() {
  return (
    <Sidebar>
      <div className="h-full overflow-auto p-6">
        <TaskList />
      </div>
    </Sidebar>
  )
}
