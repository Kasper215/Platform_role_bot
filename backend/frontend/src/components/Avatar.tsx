import { type CSSProperties } from 'react';

interface AvatarProps {
  src: string | null;
  name: string;
  size?: number;
  radius?: string;
  className?: string;
}

const COLORS = ['#8b5cf6', '#6366f1', '#ec4899', '#f43f5e', '#06b6d4', '#10b981', '#f59e0b'];

// 1. Именованный экспорт (для импортов вида: import { Avatar } from ...)
export function Avatar({ src, name, size = 40, radius = '50%', className = '' }: AvatarProps) {
  const initials = name.slice(0, 2).toUpperCase();
  const color = COLORS[name.split('').reduce((a, c) => a + c.charCodeAt(0), 0) % COLORS.length];

  const style: CSSProperties = {
    width: size,
    height: size,
    borderRadius: radius,
    flexShrink: 0,
    overflow: 'hidden',
    background: src ? undefined : color,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: size * 0.38,
    fontWeight: 700,
    color: '#fff',
  };

  if (src) {
    return <img src={src} alt={name} className={className} style={style} />;
  }
  return <div className={className} style={style}>{initials}</div>;
}

// 2. Дефолтный экспорт (для импортов вида: import Avatar from ...)
export default Avatar;