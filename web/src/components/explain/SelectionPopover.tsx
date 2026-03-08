import { useEffect, useState, useCallback, useRef } from "react"
import { Loader2, Sparkles, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useExplainStore } from "@/store/useExplainStore"

interface SelectionPopoverProps {
  containerRef: React.RefObject<HTMLElement | null>
  parentId: string
}

interface PopoverState {
  text: string
  x: number
  y: number
}

export function SelectionPopover({
  containerRef,
  parentId,
}: SelectionPopoverProps) {
  const [popover, setPopover] = useState<PopoverState | null>(null)
  const [loading, setLoading] = useState(false)
  const [question, setQuestion] = useState("")
  const exploreTerm = useExplainStore((s) => s.exploreTerm)
  const popoverRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleMouseUp = useCallback(() => {
    const selection = window.getSelection()
    if (!selection || selection.isCollapsed) return

    const text = selection.toString().trim()
    if (!text || text.length < 2) return

    const range = selection.getRangeAt(0)
    if (!containerRef.current?.contains(range.commonAncestorContainer)) return

    const rect = range.getBoundingClientRect()
    const containerRect = containerRef.current.getBoundingClientRect()

    setQuestion("")
    setPopover({
      text,
      x: rect.left + rect.width / 2 - containerRect.left,
      y: rect.top - containerRect.top - 8,
    })
  }, [containerRef])

  const handleMouseDown = useCallback((e: MouseEvent) => {
    if (popoverRef.current?.contains(e.target as Node)) return
    setPopover(null)
  }, [])

  useEffect(() => {
    document.addEventListener("mouseup", handleMouseUp)
    document.addEventListener("mousedown", handleMouseDown)
    return () => {
      document.removeEventListener("mouseup", handleMouseUp)
      document.removeEventListener("mousedown", handleMouseDown)
    }
  }, [handleMouseUp, handleMouseDown])

  useEffect(() => {
    if (popover) {
      // Small delay so the popover renders first
      requestAnimationFrame(() => inputRef.current?.focus())
    }
  }, [popover])

  const handleSubmit = async (queryText?: string) => {
    if (!popover) return
    const text = queryText ?? popover.text
    setLoading(true)
    try {
      await exploreTerm(text, parentId)
      setPopover(null)
    } finally {
      setLoading(false)
    }
  }

  const handleExplain = () => handleSubmit()

  const handleAsk = () => {
    if (!question.trim() || !popover) return
    handleSubmit(`${question.trim()}: "${popover.text}"`)
  }

  if (!popover) return null

  return (
    <div
      ref={popoverRef}
      className="absolute z-50 -translate-x-1/2 -translate-y-full animate-in fade-in zoom-in-95 duration-150"
      style={{ left: popover.x, top: popover.y }}
    >
      <div className="flex flex-col gap-1.5 rounded-lg border bg-popover p-2 shadow-md w-72">
        <div className="flex gap-1.5">
          <Input
            ref={inputRef}
            placeholder="Ask about this..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleAsk()
            }}
            disabled={loading}
            className="h-8 text-xs"
          />
          <Button
            size="icon"
            variant="ghost"
            className="h-8 w-8 shrink-0"
            onClick={handleAsk}
            disabled={loading || !question.trim()}
          >
            {loading && question.trim() ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Send className="h-3.5 w-3.5" />
            )}
          </Button>
        </div>
        <Button
          size="sm"
          variant="secondary"
          className="w-full text-xs gap-1.5"
          onClick={handleExplain}
          disabled={loading}
        >
          {loading && !question.trim() ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <Sparkles className="h-3 w-3" />
          )}
          Tell me about "{popover.text.length > 30 ? popover.text.slice(0, 30) + "..." : popover.text}"
        </Button>
      </div>
    </div>
  )
}
