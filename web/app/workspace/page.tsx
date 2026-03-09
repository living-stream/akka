'use client'

import { Sidebar } from '@/components/Sidebar'
import { NoteList } from '@/components/workspace'

export default function WorkspacePage() {
  return (
    <Sidebar>
      <div className="h-full overflow-auto p-6">
        <NoteList />
      </div>
    </Sidebar>
  )
}
