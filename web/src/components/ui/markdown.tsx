import ReactMarkdown from "react-markdown"
import { cn } from "@/lib/utils"

interface MarkdownProps {
  children: string
  className?: string
}

export function Markdown({ children, className }: MarkdownProps) {
  return (
    <div className={cn("prose dark:prose-invert max-w-none", className)}>
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  )
}
