"use client"

import { useToast } from "@/lib/hooks/useToast"
import { ToastContainer } from "@/components/ui/toast"

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const { toasts, toast } = useToast()

  return (
    <>
      {children}
      <ToastContainer 
        toasts={toasts} 
        onDismiss={(id) => toast.dismiss(id)} 
      />
    </>
  )
}