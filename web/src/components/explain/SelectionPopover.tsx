import { useEffect, useState, useCallback, useRef, useLayoutEffect } from "react"
import { createPortal } from "react-dom"
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
  // Viewport-relative coordinates
  x: number
  y: number
}

const POPOVER_WIDTH = 288 // w-72
const POPOVER_MARGIN = 8

export function SelectionPopover({
  containerRef,
  parentId,
}: SelectionPopoverProps) {
  const [popover, setPopover] = useState<PopoverState | null>(null)
  const [loading, setLoading] = useState(false)
  const [question, setQuestion] = useState("")
  const [clamped, setClamped] = useState<{ left: number; top: number } | null>(null)
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

    setQuestion("")
    setPopover({
      text,
      x: rect.left + rect.width / 2,
      y: rect.top,
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

  // Clamp popover position to viewport after it renders
  useLayoutEffect(() => {
    if (!popover || !popoverRef.current) {
      setClamped(null)
      return
    }

    const el = popoverRef.current
    const popoverHeight = el.offsetHeight

    // Center horizontally, then clamp to viewport
    let left = popover.x - POPOVER_WIDTH / 2
    left = Math.max(POPOVER_MARGIN, Math.min(left, window.innerWidth - POPOVER_WIDTH - POPOVER_MARGIN))

    // Position above selection, flip below if not enough space
    let top = popover.y - popoverHeight - POPOVER_MARGIN
    if (top < POPOVER_MARGIN) {
      // Not enough space above — show below the selection
      const selection = window.getSelection()
      if (selection && !selection.isCollapsed) {
        const rect = selection.getRangeAt(0).getBoundingClientRect()
        top = rect.bottom + POPOVER_MARGIN
      } else {
        top = popover.y + POPOVER_MARGIN
      }
    }

    setClamped({ left, top })
  }, [popover])

  useEffect(() => {
    if (popover && clamped) {
      requestAnimationFrame(() => inputRef.current?.focus())
    }
  }, [popover, clamped])

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

  return createPortal(
    <div
      ref={popoverRef}
      className="fixed z-50 animate-in fade-in zoom-in-95 duration-150"
      style={{
        left: clamped?.left ?? -9999,
        top: clamped?.top ?? -9999,
        width: POPOVER_WIDTH,
        // Hide until clamped position is calculated
        visibility: clamped ? "visible" : "hidden",
      }}
      onMouseDown={(e) => e.stopPropagation()}
    >
      <div className="flex flex-col gap-1.5 rounded-lg border bg-popover p-2 shadow-md">
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
    </div>,
    document.body
  )
}
