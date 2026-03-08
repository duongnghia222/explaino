import { Check } from "lucide-react"
import type { CourseResponse } from "@/types/course"
import { useCourseStore } from "@/store/useCourseStore"
import { cn } from "@/lib/utils"
import { Separator } from "@/components/ui/separator"

interface LessonSidebarProps {
  course: CourseResponse
}

export function LessonSidebar({ course }: LessonSidebarProps) {
  const { activeLessonId, setActiveLesson, completedLessons } =
    useCourseStore()
  const completed = completedLessons[course.id] ?? new Set<string>()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-background">
      <div className="p-4">
        <h2 className="text-lg font-semibold leading-tight">{course.title}</h2>
      </div>
      <Separator />
      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-1">
          {course.lessons.map((lesson, index) => {
            const isActive = activeLessonId === lesson.id
            const isCompleted = completed.has(lesson.id)

            return (
              <li key={lesson.id}>
                <button
                  onClick={() => setActiveLesson(lesson.id)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors",
                    isActive
                      ? "bg-secondary font-medium text-secondary-foreground"
                      : "hover:bg-muted"
                  )}
                >
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs">
                    {isCompleted ? (
                      <Check className="h-3.5 w-3.5 text-green-600" />
                    ) : (
                      index + 1
                    )}
                  </span>
                  <span className="truncate">{lesson.title}</span>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>
    </div>
  )
}
