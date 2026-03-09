'use client'

import React, { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface HumanAssistModalProps {
  isOpen: boolean
  question: string
  onResolve: (response: string) => void
  onSkip: () => void
}

export function HumanAssistModal({ isOpen, question, onResolve, onSkip }: HumanAssistModalProps) {
  const [response, setResponse] = useState('')

  const handleSubmit = () => {
    onResolve(response || '已完成')
    setResponse('')
  }

  const handleSkip = () => {
    onSkip()
    setResponse('')
  }

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md" onPointerDownOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span className="text-2xl">🤖</span>
            Agent 请求人工协助
          </DialogTitle>
        </DialogHeader>
        
        <div className="py-4">
          <div className="rounded-lg bg-muted p-4 mb-4">
            <p className="text-sm font-medium text-muted-foreground mb-2">问题：</p>
            <p className="text-base">{question}</p>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">请输入您的响应：</p>
            <Textarea
              value={response}
              onChange={(e) => setResponse(e.target.value)}
              placeholder="输入信息或直接点击确认..."
              rows={4}
              className="resize-none"
            />
          </div>
        </div>
        
        <DialogFooter className="flex gap-2 sm:gap-2">
          <Button variant="outline" onClick={handleSkip}>
            跳过
          </Button>
          <Button onClick={handleSubmit}>
            确认提交
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
