import { create } from "zustand"
import type { ExplainNode } from "@/types/explain"
import { postExplain, getExplanationTree } from "@/api/explain"

interface ExplainState {
  nodes: Record<string, ExplainNode>
  rootId: string | null
  activeNodeId: string | null
  tree: ExplainNode | null
  loading: boolean
  error: string | null
  startNewExplanation: (text: string) => Promise<string>
  exploreTerm: (term: string, parentId: string) => Promise<string>
  setActiveNode: (id: string) => void
  loadTree: (nodeId: string) => Promise<void>
  getAncestorPath: (nodeId: string) => ExplainNode[]
  reset: () => void
}

function flattenTree(node: ExplainNode, map: Record<string, ExplainNode>) {
  map[node.id] = node
  for (const child of node.children) {
    flattenTree(child, map)
  }
}

export const useExplainStore = create<ExplainState>((set, get) => ({
  nodes: {},
  rootId: null,
  activeNodeId: null,
  tree: null,
  loading: false,
  error: null,

  startNewExplanation: async (text: string) => {
    set({ loading: true, error: null })
    try {
      const res = await postExplain({ text })
      const node: ExplainNode = {
        id: res.id,
        text: res.text,
        explanation: res.explanation,
        key_terms: res.key_terms,
        parent_id: null,
        children: [],
        depth: 0,
      }
      set({
        nodes: { [res.id]: node },
        rootId: res.id,
        activeNodeId: res.id,
        tree: node,
        loading: false,
      })
      return res.id
    } catch (e) {
      set({ loading: false, error: (e as Error).message })
      throw e
    }
  },

  exploreTerm: async (term: string, parentId: string) => {
    set({ loading: true, error: null })
    try {
      const parent = get().nodes[parentId]
      const res = await postExplain({
        text: term,
        context: parent?.explanation,
        parent_id: parentId,
      })
      // Reload the full tree
      const rootId = get().rootId!
      const tree = await getExplanationTree(rootId)
      const nodes: Record<string, ExplainNode> = {}
      flattenTree(tree, nodes)
      set({
        nodes,
        tree,
        activeNodeId: res.id,
        loading: false,
      })
      return res.id
    } catch (e) {
      set({ loading: false, error: (e as Error).message })
      throw e
    }
  },

  setActiveNode: (id: string) => {
    set({ activeNodeId: id })
  },

  loadTree: async (nodeId: string) => {
    set({ loading: true, error: null })
    try {
      const tree = await getExplanationTree(nodeId)
      const nodes: Record<string, ExplainNode> = {}
      flattenTree(tree, nodes)
      set({
        nodes,
        tree,
        rootId: tree.id,
        activeNodeId: nodeId,
        loading: false,
      })
    } catch (e) {
      set({ loading: false, error: (e as Error).message })
      throw e
    }
  },

  reset: () => {
    set({ nodes: {}, rootId: null, activeNodeId: null, tree: null, loading: false, error: null })
  },

  getAncestorPath: (nodeId: string) => {
    const { nodes } = get()
    const path: ExplainNode[] = []
    let current = nodes[nodeId]
    while (current) {
      path.unshift(current)
      current = current.parent_id ? nodes[current.parent_id] : undefined!
    }
    return path
  },
}))
