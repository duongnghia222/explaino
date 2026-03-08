import { useState } from "react"
import { useNavigate } from "react-router"
import { Loader2, Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useExplainStore } from "@/store/useExplainStore"
import { cn } from "@/lib/utils"

interface ExplainInputBarProps {
  className?: string
}

export function ExplainInputBar({ className }: ExplainInputBarProps) {
  const [text, setText] = useState("")
  const [loading, setLoading] = useState(false)
  const startNewExplanation = useExplainStore((s) => s.startNewExplanation)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return

    setLoading(true)
    try {
      const id = await startNewExplanation(trimmed)
      navigate(`/explain/${id}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={cn("flex w-full max-w-lg items-center gap-2", className)}
    >
      <Input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask anything..."
        disabled={loading}
      />
      <Button type="submit" disabled={loading || !text.trim()}>
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
        Ask
      </Button>
    </form>
  )
}
