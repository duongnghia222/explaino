import { CheckCircle2 } from "lucide-react"
import type { CourseResponse } from "@/types/course"
import { useCourseStore } from "@/store/useCourseStore"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Markdown } from "@/components/ui/markdown"
import { LessonQuiz } from "./LessonQuiz"

interface LessonContentProps {
  course: CourseResponse
}

export function LessonContent({ course }: LessonContentProps) {
  const { activeLessonId, completedLessons, markLessonCompleted } =
    useCourseStore()

  const lesson = course.lessons.find((l) => l.id === activeLessonId)

  if (!lesson) {
    return (
      <div className="flex flex-1 items-center justify-center text-muted-foreground">
        Select a lesson to get started.
      </div>
    )
  }

  const completed = completedLessons[course.id]?.has(lesson.id) ?? false

  return (
    <ScrollArea className="flex-1">
      <div className="mx-auto max-w-3xl space-y-8 p-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{lesson.title}</h1>
        </div>

        <Markdown>{lesson.content}</Markdown>

        {lesson.key_points.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-xl font-semibold">Key Points</h2>
            <ul className="list-disc space-y-1.5 pl-6">
              {lesson.key_points.map((point, i) => (
                <li key={i} className="leading-7">
                  <Markdown className="inline">{point}</Markdown>
                </li>
              ))}
            </ul>
          </div>
        )}

        {lesson.quiz.length > 0 && (
          <>
            <Separator />
            <LessonQuiz questions={lesson.quiz} courseId={course.id} />
          </>
        )}

        <Separator />

        <div className="flex justify-end pb-8">
          <Button
            onClick={() => markLessonCompleted(course.id, lesson.id)}
            disabled={completed}
            variant={completed ? "secondary" : "default"}
          >
            {completed ? (
              <>
                <CheckCircle2 className="text-green-600" />
                Completed
              </>
            ) : (
              "Mark as Complete"
            )}
          </Button>
        </div>
      </div>
    </ScrollArea>
  )
}
