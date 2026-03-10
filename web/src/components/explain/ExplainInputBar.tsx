import { useState, useRef } from "react"
import { useNavigate } from "react-router"
import { Loader2, Send, FileText, Globe, Type } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useExplainStore } from "@/store/useExplainStore"
import { cn } from "@/lib/utils"
import type { InputType } from "@/types/explain"

const MAX_CHARS = 30000

const tabs: { value: InputType; label: string; icon: typeof Type }[] = [
  { value: "text", label: "Text", icon: Type },
  { value: "file", label: "File", icon: FileText },
  { value: "url", label: "URL", icon: Globe },
]

interface ExplainInputBarProps {
  className?: string
}

export function ExplainInputBar({ className }: ExplainInputBarProps) {
  const [inputType, setInputType] = useState<InputType>("text")
  const [text, setText] = useState("")
  const [url, setUrl] = useState("")
  const [fileContent, setFileContent] = useState("")
  const [fileName, setFileName] = useState("")
  const [fileError, setFileError] = useState("")
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const startNewExplanation = useExplainStore((s) => s.startNewExplanation)
  const navigate = useNavigate()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setFileError("")
    setFileName(file.name)

    const reader = new FileReader()
    reader.onload = () => {
      const content = reader.result as string
      if (content.length > MAX_CHARS) {
        setFileError(`File exceeds ${MAX_CHARS.toLocaleString()} character limit (${content.length.toLocaleString()} chars)`)
        setFileContent("")
        return
      }
      setFileContent(content)
    }
    reader.readAsText(file)
  }

  const canSubmit = () => {
    if (loading) return false
    switch (inputType) {
      case "text":
        return text.trim().length > 0
      case "file":
        return fileContent.length > 0 && !fileError
      case "url":
        return url.trim().startsWith("http://") || url.trim().startsWith("https://")
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!canSubmit()) return

    setLoading(true)
    try {
      let id: string
      switch (inputType) {
        case "text": {
          id = await startNewExplanation({ text: text.trim(), input_type: "text" })
          break
        }
        case "file": {
          id = await startNewExplanation({ text: fileContent, input_type: "file" })
          break
        }
        case "url": {
          id = await startNewExplanation({ text: "", url: url.trim(), input_type: "url" })
          break
        }
      }
      navigate(`/explain/${id}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={cn("flex w-full max-w-lg flex-col gap-3", className)}>
      <div className="flex gap-1 rounded-lg bg-muted p-1">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.value}
              type="button"
              onClick={() => setInputType(tab.value)}
              className={cn(
                "flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                inputType === tab.value
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Icon className="h-3.5 w-3.5" />
              {tab.label}
            </button>
          )
        })}
      </div>

      <form onSubmit={handleSubmit} className="flex w-full items-center gap-2">
        {inputType === "text" && (
          <Input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Ask anything..."
            disabled={loading}
          />
        )}

        {inputType === "file" && (
          <div className="flex flex-1 flex-col gap-1">
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.md,.csv,.log,.json,.xml"
              onChange={handleFileChange}
              className="text-sm file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-primary-foreground hover:file:bg-primary/90"
              disabled={loading}
            />
            {fileName && !fileError && (
              <span className="text-xs text-muted-foreground">
                {fileName} — {fileContent.length.toLocaleString()} / {MAX_CHARS.toLocaleString()} chars
              </span>
            )}
            {fileError && (
              <span className="text-xs text-destructive">{fileError}</span>
            )}
          </div>
        )}

        {inputType === "url" && (
          <Input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            disabled={loading}
          />
        )}

        <Button type="submit" disabled={!canSubmit()}>
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          {loading && inputType === "url" ? "Crawling..." : "Go"}
        </Button>
      </form>
    </div>
  )
}
