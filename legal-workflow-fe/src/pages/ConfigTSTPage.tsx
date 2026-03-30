import { useEffect, useState } from 'react'
import api from '../services/api'

interface TSTNode {
  id: number
  code: string
  name: string
  level: number
  children?: TSTNode[]
}

function TreeItem({ node, depth = 0 }: { node: TSTNode; depth?: number }) {
  const [expanded, setExpanded] = useState(true)
  const hasChildren = node.children && node.children.length > 0

  return (
    <div style={{ marginLeft: depth * 24 }}>
      <div
        className="flex items-center py-2 px-2 hover:bg-gray-50 rounded cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        {hasChildren && (
          <span className="mr-2 text-gray-400 text-xs">{expanded ? '\u25BC' : '\u25B6'}</span>
        )}
        {!hasChildren && <span className="mr-2 w-3" />}
        <span className="font-mono text-sm text-gray-500 mr-2">{node.code}</span>
        <span className="text-sm">{node.name}</span>
        <span className="ml-2 text-xs text-gray-400">L{node.level}</span>
      </div>
      {expanded && hasChildren && node.children!.map((child) => (
        <TreeItem key={child.id} node={child} depth={depth + 1} />
      ))}
    </div>
  )
}

export function ConfigTSTPage() {
  const [tree, setTree] = useState<TSTNode[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/api/legal/config/tst')
      .then((res) => setTree(res.data))
      .catch(() => setTree([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div data-testid="config-tst-page">
      <h2 className="text-2xl font-bold mb-6">Task Structure Tree (TST)</h2>

      {loading ? (
        <div className="text-gray-500">Loading tree...</div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          {tree.length > 0 ? (
            tree.map((node) => <TreeItem key={node.id} node={node} />)
          ) : (
            <p className="text-gray-500">No TST nodes configured</p>
          )}
        </div>
      )}
    </div>
  )
}
