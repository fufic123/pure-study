interface ToastProps {
  message: string
}

export default function Toast({ message }: ToastProps) {
  return (
    <div className="toast">
      <span className="toast-dot" />
      <span>{message}</span>
    </div>
  )
}
