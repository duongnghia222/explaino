import type { Citation } from "@/types/course"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface CitationLinkProps {
  citation: Citation
  index: number
}

export function CitationLink({ citation, index }: CitationLinkProps) {
  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary hover:bg-primary/20 no-underline"
          >
            {index}
          </a>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          <p className="font-medium text-sm">{citation.title}</p>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {citation.snippet}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
