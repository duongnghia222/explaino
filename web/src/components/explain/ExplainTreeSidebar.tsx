import { useNavigate } from "react-router"
import { Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useExplainStore } from "@/store/useExplainStore"
import { ExplainTreeNode } from "./ExplainTreeNode"

export function ExplainTreeSidebar() {
  const tree = useExplainStore((s) => s.tree)
  const navigate = useNavigate()

  const handleNew = () => {
    useExplainStore.getState().reset()
    navigate("/explain")
  }

  return (
    <aside className="w-72 border-r flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-sm font-semibold">Explorer</h2>
        <Button variant="ghost" size="sm" onClick={handleNew}>
          <Plus className="h-4 w-4" />
          New
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          {tree ? (
            <ExplainTreeNode node={tree} />
          ) : (
            <p className="px-2 py-4 text-sm text-muted-foreground text-center">
              Ask a question to get started.
            </p>
          )}
        </div>
      </ScrollArea>
    </aside>
  )
}
