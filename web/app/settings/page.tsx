'use client'

import { useState, useEffect } from 'react'
import { Sidebar } from '@/components/Sidebar'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { User, Save, FileText, Brain, RefreshCw } from 'lucide-react'
import { useChatStore } from '@/store/chatStore'
import { getUserProfile, updateSoul } from '@/lib/api'

export default function SettingsPage() {
  const { uid, setUid } = useChatStore()
  const [soul, setSoul] = useState('')
  const [memory, setMemory] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    loadProfile()
  }, [uid])

  const loadProfile = async () => {
    setIsLoading(true)
    try {
      const profile = await getUserProfile(uid)
      setSoul(profile.soul || '')
      setMemory(profile.memory || '')
    } catch (error) {
      console.error('Failed to load profile:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveSoul = async () => {
    setIsSaving(true)
    try {
      await updateSoul(uid, soul)
      alert('人设已保存')
    } catch (error) {
      console.error('Failed to save soul:', error)
      alert('保存失败')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Sidebar>
      <div className="h-full overflow-auto p-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Header */}
          <div>
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">设置</h2>
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
              管理你的用户配置和偏好
            </p>
          </div>

          {/* User ID */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5 text-zinc-500 dark:text-zinc-400" />
                用户身份
              </CardTitle>
              <CardDescription>你的唯一标识，用于隔离数据和对话历史</CardDescription>
            </CardHeader>
            <CardContent>
              <Input
                value={uid}
                onChange={(e) => setUid(e.target.value)}
                placeholder="输入用户ID"
              />
            </CardContent>
          </Card>

          {/* Soul */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-zinc-500 dark:text-zinc-400" />
                账号人设
              </CardTitle>
              <CardDescription>定义你的账号定位、风格和目标受众</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin text-zinc-400" />
                </div>
              ) : (
                <>
                  <Textarea
                    value={soul}
                    onChange={(e) => setSoul(e.target.value)}
                    placeholder="描述你的账号定位，例如：&#10;- 赛道：咖啡/生活方式&#10;- 风格：轻松幽默、有温度&#10;- 目标受众：25-35岁都市白领"
                    className="min-h-[200px]"
                  />
                  <div className="flex justify-end">
                    <Button onClick={handleSaveSoul} disabled={isSaving}>
                      <Save className="h-4 w-4 mr-2" />
                      {isSaving ? '保存中...' : '保存人设'}
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Memory */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-zinc-500 dark:text-zinc-400" />
                长期记忆
              </CardTitle>
              <CardDescription>助手会记住这些信息，用于提供更个性化的服务</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin text-zinc-400" />
                </div>
              ) : (
                <div className="rounded-xl bg-zinc-50 dark:bg-zinc-800/50 p-4">
                  <pre className="whitespace-pre-wrap text-sm text-zinc-700 dark:text-zinc-300 font-mono">
                    {memory || '暂无长期记忆'}
                  </pre>
                </div>
              )}
              <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-400">
                长期记忆由助手自动维护，记录你的偏好、重要信息和经验教训
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </Sidebar>
  )
}
