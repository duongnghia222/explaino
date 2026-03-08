import type { ContentBlock } from "@/types/course"
import { Markdown } from "@/components/ui/markdown"
import { ImagePlaceholder } from "./ImagePlaceholder"

interface ContentBlockRendererProps {
  blocks: ContentBlock[]
  imageClassName?: string
}

export function ContentBlockRenderer({
  blocks,
  imageClassName,
}: ContentBlockRendererProps) {
  return (
    <div className="space-y-6">
      {blocks.map((block, i) => {
        if (block.type === "text" && block.text) {
          return <Markdown key={i}>{block.text}</Markdown>
        }

        if (block.type === "image" && block.image) {
          if (block.image.placeholder || !block.image.url) {
            return <ImagePlaceholder key={i} image={block.image} />
          }
          return (
            <figure key={i} className="space-y-2">
              <img
                src={block.image.url}
                alt={block.image.alt_text}
                className={
                  imageClassName ??
                  "w-full max-w-xl rounded-lg mx-auto"
                }
              />
              {block.image.alt_text && (
                <figcaption className="text-center text-sm text-muted-foreground">
                  {block.image.alt_text}
                </figcaption>
              )}
            </figure>
          )
        }

        return null
      })}
    </div>
  )
}
