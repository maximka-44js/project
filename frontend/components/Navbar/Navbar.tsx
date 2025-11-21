'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { User, LogOut } from 'lucide-react'

export default function Navbar() {
  const { user, isLoading, isAuthenticated, logout } = useAuth()

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/" className="text-xl font-bold text-primary">
            Анализ зарплат
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          {!isLoading && (
            <>
              {isAuthenticated && user ? (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4" />
                    <span className="text-sm text-muted-foreground">
                      {user.full_name}
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={logout}
                    className="flex items-center space-x-2"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Выйти</span>
                  </Button>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" asChild>
                    <Link href="/login">Войти</Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link href="/register">Регистрация</Link>
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
