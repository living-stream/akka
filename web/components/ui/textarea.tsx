import * as React from "react"
import { cn } from "@/lib/utils"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[120px] w-full rounded-xl border-2 border-zinc-200 bg-white px-4 py-3 text-sm transition-all duration-200",
          "placeholder:text-zinc-400",
          "focus:border-zinc-400 focus:outline-none focus:ring-4 focus:ring-zinc-400/10",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "resize-none",
          "dark:border-zinc-700 dark:bg-zinc-900 dark:focus:ring-zinc-400/10",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }
