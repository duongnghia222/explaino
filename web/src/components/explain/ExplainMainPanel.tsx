import { Skeleton } from "@/components/ui/skeleton"
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

  const activeNode = activeNodeId ? nodes[activeNodeId] : null

  // No tree yet — show centered input
  if (!activeNodeId && !tree) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <ExplainInputBar />
      </div>
    )
  }

  // Loading state
  if (loading) {
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
  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <p className="text-destructive">{error}</p>
      </div>
    )
  }

  // Active node content
  if (activeNode) {
    return (
      <div className="flex-1 p-8 space-y-4 overflow-auto">
        <ExplainBreadcrumb />
        <ExplainContent node={activeNode} />
      </div>
    )
  }

  return null
}
