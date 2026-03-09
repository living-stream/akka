'use client'

import { Sidebar } from '@/components/Sidebar'
import { ChatContainer } from '@/components/chat'

export default function ChatPage() {
  return (
    <Sidebar>
      <div className="flex h-full flex-col">
        <ChatContainer />
      </div>
    </Sidebar>
  )
}
