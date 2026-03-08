import { ExternalLink } from "lucide-react"
import type { Citation } from "@/types/course"

interface CitationListProps {
  citations: Citation[]
}

export function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) return null

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">References</h3>
      <ol className="list-decimal space-y-2 pl-6 text-sm">
        {citations.map((c) => (
          <li key={c.id}>
            <a
              href={c.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-primary hover:underline"
            >
              {c.title}
              <ExternalLink className="h-3 w-3" />
            </a>
            {c.snippet && (
              <p className="text-muted-foreground mt-0.5 line-clamp-2">
                {c.snippet}
              </p>
            )}
          </li>
        ))}
      </ol>
    </div>
  )
}
