'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const router = useRouter()

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = () => {
    try {
      const token = localStorage.getItem('access_token')
      const userData = localStorage.getItem('user_data')
      
      if (token && userData) {
        const parsedUser = JSON.parse(userData)
        setUser(parsedUser)
        setIsAuthenticated(true)
      } else {
        setIsAuthenticated(false)
        setUser(null)
      }
    } catch (error) {
      console.error('Error checking auth status:', error)
      setIsAuthenticated(false)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = (userData: User, tokens: { access_token: string; refresh_token: string }) => {
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    localStorage.setItem('user_data', JSON.stringify(userData))
    
    setUser(userData)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
    
    setUser(null)
    setIsAuthenticated(false)
    
    router.push('/login')
  }

  const redirectIfAuthenticated = (redirectTo: string = '/') => {
    if (isAuthenticated && !isLoading) {
      router.push(redirectTo)
      return true
    }
    return false
  }

  const redirectIfNotAuthenticated = (redirectTo: string = '/login') => {
    if (!isAuthenticated && !isLoading) {
      router.push(redirectTo)
      return true
    }
    return false
  }

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    checkAuthStatus,
    redirectIfAuthenticated,
    redirectIfNotAuthenticated
  }
}