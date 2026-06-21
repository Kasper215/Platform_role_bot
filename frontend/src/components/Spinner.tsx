// Строка "import React from 'react';" удалена, чтобы не вызывать предупреждение о неиспользуемом импорте

export function Spinner() {
  return <div className="spinner" />;
}

export default Spinner;

export function CenteredSpinner({ text }: { text?: string }) {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      gap: '0.75rem', 
      padding: '3rem', 
      color: 'var(--text-sec)' 
    }}>
      <div className="spinner centered" />
      {text && <p>{text}</p>}
    </div>
  );
}