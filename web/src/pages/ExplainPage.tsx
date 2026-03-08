import { useEffect, useRef } from "react"
import { useParams, useNavigate } from "react-router"
import { useExplainStore } from "@/store/useExplainStore"
import { ExplainTreeSidebar } from "@/components/explain/ExplainTreeSidebar"
import { ExplainMainPanel } from "@/components/explain/ExplainMainPanel"

export function ExplainPage() {
  const { nodeId } = useParams()
  const navigate = useNavigate()
  const { activeNodeId, loadTree, setActiveNode } = useExplainStore()
  const prevNodeIdRef = useRef(nodeId)
  const initialLoadDone = useRef(false)

  // Respond to URL-driven changes only
  useEffect(() => {
    const isUrlChange = nodeId !== prevNodeIdRef.current
    prevNodeIdRef.current = nodeId

    if (!nodeId) {
      useExplainStore.getState().reset()
      initialLoadDone.current = false
      return
    }

    if (isUrlChange || !initialLoadDone.current) {
      initialLoadDone.current = true
      const { tree, nodes } = useExplainStore.getState()
      if (tree && nodes[nodeId]) {
        setActiveNode(nodeId)
      } else {
        loadTree(nodeId)
      }
    }
  }, [nodeId, setActiveNode, loadTree])

  // Sync URL when activeNodeId changes (e.g. sidebar click)
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
