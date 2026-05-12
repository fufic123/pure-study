interface MarkdownProps {
  text: string
  inline?: boolean
}

function inlineMd(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(
      /^- (.+)$/gm,
      "<span style='display:block; padding-left: 14px; position:relative;'><span style='position:absolute; left:0; color:var(--text-mute);'>·</span>$1</span>",
    )
    .replace(/\n/g, '<br>')
}

export default function Markdown({ text, inline = false }: MarkdownProps) {
  if (!text) return null
  const parts = inline ? [text] : text.split(/\n\n+/)
  return (
    <>
      {parts.map((p, i) => {
        const html = inlineMd(p)
        if (inline) {
          return <span key={i} dangerouslySetInnerHTML={{ __html: html }} />
        }
        return <p key={i} dangerouslySetInnerHTML={{ __html: html }} />
      })}
    </>
  )
}
