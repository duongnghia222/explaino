import { useState } from "react"
import { useNavigate } from "react-router"
import { Loader2, Baby, User, Microscope } from "lucide-react"
import type { CourseMode } from "@/types/course"
import { useCourseStore } from "@/store/useCourseStore"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"

const modes: {
  value: CourseMode
  label: string
  icon: typeof Baby
  description: string
}[] = [
  {
    value: "kids",
    label: "Kids",
    icon: Baby,
    description: "Visual storybook style with lots of images",
  },
  {
    value: "normal",
    label: "Normal",
    icon: User,
    description: "University-level with occasional illustrations",
  },
  {
    value: "advanced",
    label: "Advanced",
    icon: Microscope,
    description: "Deep research with citations and sources",
  },
]

export function CourseGeneratorForm() {
  const [topic, setTopic] = useState("")
  const [mode, setMode] = useState<CourseMode>("normal")
  const { generateCourse, loading } = useCourseStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim() || loading) return
    const id = await generateCourse(topic.trim(), mode)
    navigate(`/courses/${id}`)
  }

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle className="text-2xl">Generate a Course</CardTitle>
        <CardDescription>
          Enter a topic and choose a difficulty level to generate a personalized
          course.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="topic" className="text-sm font-medium">
              Topic
            </label>
            <Input
              id="topic"
              placeholder="e.g. Quantum Physics, World War II, Machine Learning"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Mode</label>
            <div className="grid grid-cols-3 gap-2">
              {modes.map(({ value, label, icon: Icon, description }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setMode(value)}
                  className={cn(
                    "flex flex-col items-center gap-1.5 rounded-lg border p-3 text-sm font-medium transition-colors",
                    mode === value
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-input bg-background hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {label}
                  <span className="text-[10px] font-normal text-muted-foreground text-center leading-tight">
                    {description}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={loading || !topic.trim()}>
            {loading ? (
              <>
                <Loader2 className="animate-spin" />
                Generating...
              </>
            ) : (
              "Generate Course"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
