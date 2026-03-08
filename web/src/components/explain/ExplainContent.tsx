import { useRef } from "react"

import type { ExplainNode } from "@/types/explain"
import { SelectionPopover } from "./SelectionPopover"

interface ExplainContentProps {
  node: ExplainNode
}

export function ExplainContent({ node }: ExplainContentProps) {
  const explanationRef = useRef<HTMLDivElement>(null)

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">{node.text}</h2>

      <div ref={explanationRef} className="relative text-base leading-relaxed">
        {node.explanation}
        <SelectionPopover containerRef={explanationRef} parentId={node.id} />
      </div>
    </div>
  )
}
