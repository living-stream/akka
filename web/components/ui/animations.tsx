"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface SparklesCoreProps {
  id?: string;
  className?: string;
  background?: string;
  minSize?: number;
  maxSize?: number;
  particleDensity?: number;
  particleColor?: string;
}

export const SparklesCore = ({
  className,
  background = "transparent",
  minSize = 0.4,
  maxSize = 1,
  particleDensity = 50,
  particleColor = "#a855f7",
}: SparklesCoreProps) => {
  const [particles, setParticles] = useState<Array<{
    id: number;
    x: number;
    y: number;
    size: number;
    duration: number;
    delay: number;
  }>>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: particleDensity }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * (maxSize - minSize) + minSize,
      duration: Math.random() * 2 + 1.5,
      delay: Math.random() * 2,
    }));
    setParticles(newParticles);
  }, [particleDensity, minSize, maxSize]);

  return (
    <div
      className={cn("relative overflow-hidden", className)}
      style={{ background }}
    >
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size * 4,
            height: particle.size * 4,
            background: particleColor,
            boxShadow: `0 0 ${particle.size * 6}px ${particleColor}`,
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1, 0],
          }}
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};

export const TextGenerateEffect = ({
  words,
  className,
  filter = true,
  duration = 0.5,
}: {
  words: string;
  className?: string;
  filter?: boolean;
  duration?: number;
}) => {
  const [displayedText, setDisplayedText] = useState("");
  const wordsArray = words.split(" ");

  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < wordsArray.length) {
        setDisplayedText(wordsArray.slice(0, currentIndex + 1).join(" "));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, duration * 1000);

    return () => clearInterval(interval);
  }, [wordsArray, duration]);

  return (
    <motion.div
      className={cn("font-bold", className)}
      initial={{ opacity: 0, filter: filter ? "blur(10px)" : "none" }}
      animate={{ opacity: 1, filter: filter ? "blur(0px)" : "none" }}
      transition={{ duration: 0.5 }}
    >
      {displayedText}
    </motion.div>
  );
};

export const MovingBorder = ({
  children,
  className,
  containerClassName,
  duration = 4000,
  borderColor = "linear-gradient(90deg, #7c3aed, #2563eb, #7c3aed)",
  borderSize = 2,
}: {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
  duration?: number;
  borderColor?: string;
  borderSize?: number;
}) => {
  return (
    <div
      className={cn(
        "relative rounded-xl overflow-hidden p-[2px]",
        containerClassName
      )}
    >
      <motion.div
        className="absolute inset-0"
        style={{
          background: borderColor,
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
      <div
        className={cn(
          "relative bg-white dark:bg-zinc-900 rounded-xl",
          className
        )}
      >
        {children}
      </div>
    </div>
  );
};

export const BackgroundGradient = ({
  children,
  className,
  containerClassName,
}: {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
}) => {
  return (
    <div className={cn("relative group", containerClassName)}>
      <motion.div
        className="absolute -inset-0.5 rounded-xl opacity-0 group-hover:opacity-75 blur-xl transition duration-500"
        style={{
          background: "linear-gradient(to right, #7c3aed, #2563eb)",
        }}
      />
      <div className={cn("relative", className)}>{children}</div>
    </div>
  );
};

export const FadeIn = ({
  children,
  className,
  delay = 0,
  direction = "up",
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  direction?: "up" | "down" | "left" | "right";
}) => {
  const directions = {
    up: { y: 20, x: 0 },
    down: { y: -20, x: 0 },
    left: { x: 20, y: 0 },
    right: { x: -20, y: 0 },
  };

  return (
    <motion.div
      initial={{ opacity: 0, ...directions[direction] }}
      whileInView={{ opacity: 1, y: 0, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

export const StaggerContainer = ({
  children,
  className,
  staggerDelay = 0.1,
}: {
  children: React.ReactNode;
  className?: string;
  staggerDelay?: number;
}) => {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      variants={{
        visible: { transition: { staggerChildren: staggerDelay } },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};
