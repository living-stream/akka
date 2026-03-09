---
name: aceternity-ui
description: Use Aceternity UI components to add beautiful animations and effects. Install components via CLI or copy code. Use for hero sections, backgrounds, cards, text effects, and navigation.
---

# Aceternity UI Skill

Aceternity UI 是一个高质量的 React 组件库，提供 200+ 动画组件，基于 Tailwind CSS + Framer Motion。

## 快速开始

### 安装依赖
```bash
npm install motion clsx tailwind-merge
```

### 工具函数 (`lib/utils.ts`)
```typescript
import { ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### CLI 安装组件
```bash
# 安装单个组件
npx shadcn@latest add @aceternity/card-spotlight
npx shadcn@latest add @aceternity/background-beams
npx shadcn@latest add @aceternity/text-generate-effect
```

## 常用组件代码

### 1. Sparkles 背景 (适合聊天界面)
```tsx
"use client";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";

export const SparklesCore = (props: {
  id?: string;
  className?: string;
  background?: string;
  minSize?: number;
  maxSize?: number;
  particleDensity?: number;
  particleColor?: string;
}) => {
  const {
    id,
    className,
    background = "transparent",
    minSize = 1,
    maxSize = 3,
    particleDensity = 100,
    particleColor = "#FFF",
  } = props;
  // ... 完整实现见官网
  return (
    <div className={cn("relative", className)}>
      {/* Sparkles particles */}
    </div>
  );
};
```

### 2. Text Generate Effect (打字机效果)
```tsx
"use client";
import { useEffect, useRef, useState } from "react";
import { motion, useAnimationFrame } from "motion/react";
import { cn } from "@/lib/utils";

export const TextGenerateEffect = ({
  words,
  className,
}: {
  words: string;
  className?: string;
}) => {
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < words.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(words.slice(0, currentIndex + 1));
        setCurrentIndex(currentIndex + 1);
      }, 30);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, words]);

  return (
    <motion.span className={cn(className)}>
      {displayedText}
    </motion.span>
  );
};
```

### 3. Background Beams (光线背景)
```tsx
"use client";
import { cn } from "@/lib/utils";
import { motion } from "motion/react";

export const BackgroundBeams = ({ className }: { className?: string }) => {
  return (
    <div className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      <svg className="absolute h-full w-full">
        {/* Beams SVG */}
      </svg>
    </div>
  );
};
```

### 4. Moving Border (流动边框)
```tsx
"use client";
import React from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

export const MovingBorder = ({
  children,
  className,
  containerClassName,
  borderClassName,
  duration = 2000,
}: {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
  borderClassName?: string;
  duration?: number;
}) => {
  return (
    <div className={cn("relative p-[1px] overflow-hidden", containerClassName)}>
      <motion.div
        className={cn("absolute inset-0", borderClassName)}
        style={{
          background: "linear-gradient(90deg, #7c3aed, #2563eb, #7c3aed)",
        }}
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: duration / 1000,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <div className={cn("relative bg-white dark:bg-zinc-900 rounded-xl", className)}>
        {children}
      </div>
    </div>
  );
};
```

### 5. 3D Card Effect
```tsx
"use client";
import React, { useState } from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

export const CardContainer = ({
  children,
  className,
  containerClassName,
}: {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
}) => {
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    setRotateX((y - centerY) / 10);
    setRotateY((centerX - x) / 10);
  };

  const handleMouseLeave = () => {
    setRotateX(0);
    setRotateY(0);
  };

  return (
    <motion.div
      className={cn("perspective-1000", containerClassName)}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ transformStyle: "preserve-3d" }}
      animate={{ rotateX, rotateY }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <div className={cn("", className)}>{children}</div>
    </motion.div>
  );
};
```

### 6. Aurora Background (极光背景)
```tsx
"use client";
import { cn } from "@/lib/utils";
import { motion } from "motion/react";

export const AuroraBackground = ({
  children,
  className,
  showRadialGradient = true,
}: {
  children?: React.ReactNode;
  className?: string;
  showRadialGradient?: boolean;
}) => {
  return (
    <div className={cn("relative flex flex-col min-h-screen", className)}>
      <motion.div
        initial={{ opacity: 0.5 }}
        whileHover={{ opacity: 1 }}
        className="absolute inset-0 overflow-hidden"
      >
        <div
          className={cn(
            "pointer-events-none absolute -inset-[10px] opacity-50",
            "[background-image:repeating-linear-gradient(100deg,#7c3aed_10%,#2563eb_15%,#7c3aed_20%,#2563eb_25%,#7c3aed_30%)]",
            "[background-size:300%_300%]",
            "[background-position:50%_50%]",
            "blur-[100px] animate-aurora"
          )}
        />
      </motion.div>
      {children}
    </div>
  );
};
```

## Tailwind 配置扩展

```javascript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      animation: {
        aurora: "aurora 60s linear infinite",
        shimmer: "shimmer 2s linear infinite",
      },
      keyframes: {
        aurora: {
          from: { backgroundPosition: "50% 50%", transform: "rotate(0deg)" },
          to: { backgroundPosition: "350% 50%", transform: "rotate(360deg)" },
        },
        shimmer: {
          from: { backgroundPosition: "0 0" },
          to: { backgroundPosition: "-200% 0" },
        },
      },
    },
  },
};
```

## 应用场景

| 组件 | 适用场景 |
|------|----------|
| Sparkles | 聊天界面背景、登录页 |
| Text Generate | AI 回复打字效果 |
| Moving Border | 重要按钮、卡片 |
| 3D Card | 作品展示、产品卡片 |
| Aurora | 首页 Hero 区域 |
| Background Beams | 全屏背景装饰 |

## 官网资源

- 组件库: https://ui.aceternity.com
- GitHub: https://github.com/aceternity/ui
- 免费组件: 200+
- Pro 版本: $199 终身访问

## 使用建议

1. 优先使用 CLI 安装: `npx shadcn@latest add @aceternity/<component>`
2. 确保项目已安装 `motion` 和 `clsx`
3. 组件需要 `"use client"` 指令
4. 配合 Tailwind 的 `darkMode: "class"` 使用
