import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { useExplainStore } from "@/store/useExplainStore"
import { Fragment } from "react"

export function ExplainBreadcrumb() {
  const activeNodeId = useExplainStore((s) => s.activeNodeId)
  const getAncestorPath = useExplainStore((s) => s.getAncestorPath)
  const setActiveNode = useExplainStore((s) => s.setActiveNode)

  if (!activeNodeId) return null

  const ancestors = getAncestorPath(activeNodeId)
  if (!ancestors.length) return null

  const current = ancestors[ancestors.length - 1]
  const parents = ancestors.slice(0, -1)

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {parents.map((node) => (
          <Fragment key={node.id}>
            <BreadcrumbItem>
              <BreadcrumbLink
                className="cursor-pointer"
                onClick={() => setActiveNode(node.id)}
              >
                {node.text}
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
          </Fragment>
        ))}
        {current && (
          <BreadcrumbItem>
            <BreadcrumbPage>{current.text}</BreadcrumbPage>
          </BreadcrumbItem>
        )}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
