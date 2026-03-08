import { useState, useEffect, useRef } from "react"
import { Loader2, Send } from "lucide-react"

import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useExplainStore } from "@/store/useExplainStore"
import { ExplainBreadcrumb } from "./ExplainBreadcrumb"
import { ExplainContent } from "./ExplainContent"
import { ExplainInputBar } from "./ExplainInputBar"

export function ExplainMainPanel() {
  const activeNodeId = useExplainStore((s) => s.activeNodeId)
  const nodes = useExplainStore((s) => s.nodes)
  const tree = useExplainStore((s) => s.tree)
  const loading = useExplainStore((s) => s.loading)
  const error = useExplainStore((s) => s.error)
  const getAncestorPath = useExplainStore((s) => s.getAncestorPath)
  const exploreTerm = useExplainStore((s) => s.exploreTerm)

  const [followUp, setFollowUp] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const activeNode = activeNodeId ? nodes[activeNodeId] : null
  const thread = activeNodeId ? getAncestorPath(activeNodeId) : []

  // Scroll to bottom when thread grows
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [activeNodeId])

  const handleFollowUp = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = followUp.trim()
    if (!trimmed || !activeNodeId) return

    setSubmitting(true)
    try {
      await exploreTerm(trimmed, activeNodeId, true)
      setFollowUp("")
    } finally {
      setSubmitting(false)
    }
  }

  // No tree yet — show centered input
  if (!activeNodeId && !tree) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <ExplainInputBar />
      </div>
    )
  }

  // Loading state (initial load only)
  if (loading && thread.length === 0) {
    return (
      <div className="flex-1 p-8 space-y-4">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    )
  }

  // Error state
  if (error && thread.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <p className="text-destructive">{error}</p>
      </div>
    )
  }

  // Thread view
  if (activeNode && thread.length > 0) {
    return (
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-auto p-8 space-y-6">
          <ExplainBreadcrumb />

          {thread.map((node, i) => (
            <div key={node.id}>
              {i > 0 && <hr className="mb-6" />}
              <ExplainContent
                node={node}
                isActive={node.id === activeNodeId}
              />
            </div>
          ))}

          {submitting && (
            <div className="space-y-3 pt-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="border-t p-4">
          <form onSubmit={handleFollowUp} className="flex items-center gap-2 max-w-3xl mx-auto">
            <Input
              value={followUp}
              onChange={(e) => setFollowUp(e.target.value)}
              placeholder="Ask a follow-up..."
              disabled={submitting}
            />
            <Button type="submit" size="icon" disabled={submitting || !followUp.trim()}>
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
    )
  }

  return null
}
