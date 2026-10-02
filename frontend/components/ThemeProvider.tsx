"use client";
import { ThemeProvider as Next } from "next-themes";
import { ReactNode } from "react";
export default function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <Next attribute="class" defaultTheme="dark" enableSystem={false}>
      {children}
    </Next>
  );
}
