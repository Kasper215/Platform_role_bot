import { type ReactNode, type CSSProperties } from 'react';

type BadgeVariant = 'nsfw' | 'safe' | 'public' | 'featured' | 'tag' | 'default';

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

const variantStyles: Record<BadgeVariant, CSSProperties> = {
  nsfw: { background: 'rgba(244,63,94,0.15)', color: '#f43f5e', borderColor: 'rgba(244,63,94,0.25)' },
  safe: { background: 'rgba(16,185,129,0.14)', color: '#10b981', borderColor: 'rgba(16,185,129,0.25)' },
  public: { background: 'rgba(139,92,246,0.14)', color: '#a78bfa', borderColor: 'rgba(139,92,246,0.25)' },
  featured: { background: 'rgba(245,158,11,0.14)', color: '#f59e0b', borderColor: 'rgba(245,158,11,0.25)' },
  tag: { background: 'var(--surface-2)', color: 'var(--text-sec)', borderColor: 'var(--border)' },
  default: { background: 'var(--accent-soft)', color: 'var(--accent-1)', borderColor: 'rgba(139,92,246,0.2)' },
};

// 1. Именованный экспорт (для импортов вида: import { Badge } from ...)
export function Badge({ variant = 'default', children, className = '', onClick }: BadgeProps) {
  return (
    <span
      className={className}
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.25rem',
        padding: '2px 9px',
        fontSize: '0.72rem',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        borderRadius: 'var(--radius-xs)',
        border: '1px solid',
        whiteSpace: 'nowrap',
        cursor: onClick ? 'pointer' : undefined,
        transition: 'opacity 0.15s ease',
        ...variantStyles[variant],
      }}
    >
      {children}
    </span>
  );
}

// 2. Дефолтный экспорт (для импортов вида: import Badge from ...)
export default Badge;