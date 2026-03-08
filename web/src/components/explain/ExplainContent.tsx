import { useRef } from "react"

import type { ExplainNode } from "@/types/explain"
import { Markdown } from "@/components/ui/markdown"
import { SelectionPopover } from "./SelectionPopover"

interface ExplainContentProps {
  node: ExplainNode
  isActive?: boolean
}

export function ExplainContent({ node, isActive }: ExplainContentProps) {
  const explanationRef = useRef<HTMLDivElement>(null)

  return (
    <div className={isActive ? "space-y-4" : "space-y-4 opacity-80"}>
      <h2 className="text-lg font-semibold text-muted-foreground">{node.text}</h2>

      <div ref={explanationRef} className="relative text-base leading-relaxed">
        <Markdown>{node.explanation}</Markdown>
        {isActive && (
          <SelectionPopover containerRef={explanationRef} parentId={node.id} />
        )}
      </div>
    </div>
  )
}
