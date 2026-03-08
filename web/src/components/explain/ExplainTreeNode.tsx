import { useState } from "react"
import { ChevronRight, MessageSquare } from "lucide-react"

import type { ExplainNode } from "@/types/explain"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { useExplainStore } from "@/store/useExplainStore"
import { cn } from "@/lib/utils"

interface ExplainTreeNodeProps {
  node: ExplainNode
  depth?: number
}

/**
 * Collect the linear follow-up chain starting from a node.
 * Returns [node, followUp1, followUp2, ...] and the remaining branch children
 * at each step.
 */
function collectLinearChain(node: ExplainNode) {
  const chain: ExplainNode[] = [node]
  const branchChildren: ExplainNode[][] = []

  let current = node
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const followUps = current.children.filter((c) => c.is_follow_up)
    const branches = current.children.filter((c) => !c.is_follow_up)
    branchChildren.push(branches)

    if (followUps.length === 1 && branches.length === 0) {
      // Pure linear continuation
      chain.push(followUps[0])
      current = followUps[0]
    } else {
      // If there are multiple follow-ups or mixed, treat remaining follow-ups
      // as branches too (edge case)
      if (followUps.length > 0) {
        branchChildren[branchChildren.length - 1] = [
          ...branches,
          ...followUps,
        ]
      }
      break
    }
  }

  return { chain, branchChildren }
}

export function ExplainTreeNode({ node, depth = 0 }: ExplainTreeNodeProps) {
  const [open, setOpen] = useState(true)
  const activeNodeId = useExplainStore((s) => s.activeNodeId)
  const setActiveNode = useExplainStore((s) => s.setActiveNode)

  const { chain, branchChildren } = collectLinearChain(node)
  const hasContent = chain.length > 1 || branchChildren.some((b) => b.length > 0)

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      {/* Render each node in the linear chain at the same depth */}
      {chain.map((item, i) => {
        const isActive = activeNodeId === item.id
        const isFirst = i === 0
        const branches = branchChildren[i] || []

        return (
          <div key={item.id}>
            <div
              className={cn(
                "flex items-center gap-1 rounded-md px-2 py-1 text-sm hover:bg-accent",
                isActive && "bg-secondary"
              )}
              style={{ paddingLeft: `${depth * 12 + 8}px` }}
            >
              {isFirst && hasContent ? (
                <CollapsibleTrigger asChild>
                  <button className="shrink-0 p-0.5 rounded-sm hover:bg-accent">
                    <ChevronRight
                      className={cn(
                        "h-4 w-4 transition-transform",
                        open && "rotate-90"
                      )}
                    />
                  </button>
                </CollapsibleTrigger>
              ) : isFirst ? (
                <span className="w-5 shrink-0" />
              ) : (
                <MessageSquare className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
              )}

              <button
                className="truncate text-left flex-1"
                onClick={() => setActiveNode(item.id)}
                title={item.text}
              >
                {item.text}
              </button>
            </div>

            {/* Render branch children nested under the node they belong to */}
            {open && branches.length > 0 && (
              <CollapsibleContent forceMount>
                {branches.map((child) => (
                  <ExplainTreeNode
                    key={child.id}
                    node={child}
                    depth={depth + 1}
                  />
                ))}
              </CollapsibleContent>
            )}
          </div>
        )
      })}
    </Collapsible>
  )
}
