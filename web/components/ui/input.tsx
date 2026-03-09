import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border-2 border-zinc-200 bg-white px-4 py-2 text-sm transition-all duration-200",
          "placeholder:text-zinc-400",
          "focus:border-zinc-400 focus:outline-none focus:ring-4 focus:ring-zinc-400/10",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "dark:border-zinc-700 dark:bg-zinc-900 dark:focus:ring-zinc-400/10",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
