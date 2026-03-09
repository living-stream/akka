'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  MessageSquare,
  Clock,
  FolderOpen,
  Settings,
  Menu,
  X,
  Moon,
  Sun,
} from 'lucide-react'
import { useChatStore } from '@/store/chatStore'

interface SidebarProps {
  children: React.ReactNode
}

const navItems = [
  { href: '/chat', icon: MessageSquare, label: '对话' },
  { href: '/tasks', icon: Clock, label: '任务' },
  { href: '/workspace', icon: FolderOpen, label: '工作区' },
  { href: '/settings', icon: Settings, label: '设置' },
]

export function Sidebar({ children }: SidebarProps) {
  const pathname = usePathname()
  const { uid, setUid } = useChatStore()
  const [darkMode, setDarkMode] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <div className="flex h-screen bg-white dark:bg-zinc-950">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-60 flex-col border-r border-zinc-200 dark:border-zinc-800">
        {/* Logo */}
        <div className="flex items-center h-14 px-5 border-b border-zinc-200 dark:border-zinc-800 gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 dark:bg-zinc-100 shrink-0">
            <MessageSquare className="h-4 w-4 text-white dark:text-zinc-900" />
          </div>
          <div className="flex flex-col justify-center">
            <h1 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 leading-tight">AutoVen</h1>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-tight">智能运营助手</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100'
                    : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100'
                )}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* User */}
        <div className="p-3 border-t border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800">
              <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
                {uid.slice(0, 2).toUpperCase()}
              </span>
            </div>
            <Input
              value={uid}
              onChange={(e) => setUid(e.target.value)}
              className="h-8 text-xs"
              placeholder="用户ID"
            />
          </div>
        </div>

        {/* Theme */}
        <div className="p-3 border-t border-zinc-200 dark:border-zinc-800">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleDarkMode}
            className="w-full justify-start text-zinc-600 dark:text-zinc-400"
          >
            {darkMode ? <Sun className="h-4 w-4 mr-2" /> : <Moon className="h-4 w-4 mr-2" />}
            {darkMode ? '浅色模式' : '深色模式'}
          </Button>
        </div>
      </aside>

      {/* Desktop Main Content */}
      <main className="hidden md:flex flex-1 flex-col overflow-hidden">
        {children}
      </main>

      {/* Mobile */}
      <div className="flex flex-col flex-1 overflow-hidden md:hidden">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between h-14 px-4 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 -ml-2"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 dark:bg-zinc-100">
              <MessageSquare className="h-4 w-4 text-white dark:text-zinc-900" />
            </div>
            <span className="font-medium text-zinc-900 dark:text-zinc-100">AutoVen</span>
          </div>
          <button onClick={toggleDarkMode} className="p-2 -mr-2">
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
        </header>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <nav className="md:hidden p-3 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm',
                    isActive
                      ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100'
                      : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100'
                  )}
                >
                  <item.icon className="h-4 w-4 flex-shrink-0" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        )}

        {/* Content */}
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}