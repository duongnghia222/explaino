import { useState } from "react"
import { ChevronRight } from "lucide-react"

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

export function ExplainTreeNode({ node, depth = 0 }: ExplainTreeNodeProps) {
  const [open, setOpen] = useState(true)
  const activeNodeId = useExplainStore((s) => s.activeNodeId)
  const setActiveNode = useExplainStore((s) => s.setActiveNode)

  const hasChildren = node.children.length > 0
  const isActive = activeNodeId === node.id

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <div
        className={cn(
          "flex items-center gap-1 rounded-md px-2 py-1 text-sm hover:bg-accent",
          isActive && "bg-secondary"
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        {hasChildren ? (
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
        ) : (
          <span className="w-5 shrink-0" />
        )}

        <button
          className="truncate text-left flex-1"
          onClick={() => setActiveNode(node.id)}
          title={node.text}
        >
          {node.text}
        </button>
      </div>

      {hasChildren && (
        <CollapsibleContent>
          {node.children.map((child) => (
            <ExplainTreeNode
              key={child.id}
              node={child}
              depth={depth + 1}
            />
          ))}
        </CollapsibleContent>
      )}
    </Collapsible>
  )
}
