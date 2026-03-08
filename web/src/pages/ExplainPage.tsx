import { useEffect } from "react"
import { useParams, useNavigate } from "react-router"
import { useExplainStore } from "@/store/useExplainStore"
import { ExplainTreeSidebar } from "@/components/explain/ExplainTreeSidebar"
import { ExplainMainPanel } from "@/components/explain/ExplainMainPanel"

export function ExplainPage() {
  const { nodeId } = useParams()
  const navigate = useNavigate()
  const { activeNodeId, tree, loadTree, setActiveNode } = useExplainStore()

  useEffect(() => {
    if (nodeId && nodeId !== activeNodeId) {
      if (tree) {
        setActiveNode(nodeId)
      } else {
        loadTree(nodeId)
      }
    }
  }, [nodeId, activeNodeId, tree, loadTree, setActiveNode])

  // Sync URL when activeNodeId changes
  useEffect(() => {
    if (activeNodeId && activeNodeId !== nodeId) {
      navigate(`/explain/${activeNodeId}`, { replace: true })
    }
  }, [activeNodeId, nodeId, navigate])

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <ExplainTreeSidebar />
      <ExplainMainPanel />
    </div>
  )
}
