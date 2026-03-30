import { useAuthStore } from '../../stores/auth.store'

interface SecGuardProps {
  /** Minimum SEC level required (SEC1=lowest, SEC4=highest) */
  minLevel?: string
  /** Specific role_legal required */
  roleLegal?: string
  children: React.ReactNode
  fallback?: React.ReactNode
}

const SEC_ORDER = ['SEC1', 'SEC2', 'SEC3', 'SEC4']

export function SecGuard({ minLevel, roleLegal, children, fallback = null }: SecGuardProps) {
  const user = useAuthStore((s) => s.user)

  if (!user) return <>{fallback}</>

  if (minLevel) {
    const userIdx = SEC_ORDER.indexOf(user.empsec || 'SEC1')
    const requiredIdx = SEC_ORDER.indexOf(minLevel)
    if (userIdx < requiredIdx) return <>{fallback}</>
  }

  if (roleLegal && user.role_legal !== roleLegal) return <>{fallback}</>

  return <>{children}</>
}
