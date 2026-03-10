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

  const isRootSource = !node.parent_id && (node.input_type === "file" || node.input_type === "url")

  return (
    <div className={isActive ? "space-y-4" : "space-y-4 opacity-80"}>
      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold text-muted-foreground">{node.text}</h2>
        {isRootSource && (
          <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
            {node.input_type === "file" ? "File" : "URL"}
          </span>
        )}
      </div>

      <div ref={explanationRef} className="relative text-base leading-relaxed">
        <Markdown>{node.explanation}</Markdown>
        {isActive && (
          <SelectionPopover containerRef={explanationRef} parentId={node.id} />
        )}
      </div>
    </div>
  )
}
