import { ImageOff } from "lucide-react"
import type { ImageBlock } from "@/types/course"

interface ImagePlaceholderProps {
  image: ImageBlock
}

export function ImagePlaceholder({ image }: ImagePlaceholderProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-muted-foreground/30 bg-muted/30 p-8 text-center">
      <ImageOff className="h-8 w-8 text-muted-foreground/50" />
      <p className="text-sm text-muted-foreground">{image.alt_text}</p>
      <p className="text-xs text-muted-foreground/60">
        Image generation API not configured
      </p>
    </div>
  )
}
