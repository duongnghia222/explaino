import { CheckCircle2 } from "lucide-react"
import type { CourseResponse } from "@/types/course"
import { useCourseStore } from "@/store/useCourseStore"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent } from "@/components/ui/card"
import { Markdown } from "@/components/ui/markdown"
import { ContentBlockRenderer } from "./ContentBlockRenderer"
import { cn } from "@/lib/utils"

interface KidsLessonContentProps {
  course: CourseResponse
}

const pastelGradients = [
  "from-pink-100 to-purple-100 dark:from-pink-950/30 dark:to-purple-950/30",
  "from-blue-100 to-cyan-100 dark:from-blue-950/30 dark:to-cyan-950/30",
  "from-green-100 to-emerald-100 dark:from-green-950/30 dark:to-emerald-950/30",
  "from-yellow-100 to-orange-100 dark:from-yellow-950/30 dark:to-orange-950/30",
  "from-violet-100 to-fuchsia-100 dark:from-violet-950/30 dark:to-fuchsia-950/30",
]

export function KidsLessonContent({ course }: KidsLessonContentProps) {
  const {
    activeLessonId,
    completedLessons,
    markLessonCompleted,
    quizAnswers,
    answerQuestion,
    setActiveLesson,
  } = useCourseStore()

  const lessonIndex = course.lessons.findIndex((l) => l.id === activeLessonId)
  const lesson = lessonIndex >= 0 ? course.lessons[lessonIndex] : undefined

  if (!lesson) {
    return (
      <div className="flex flex-1 items-center justify-center text-muted-foreground text-xl">
        Pick a lesson to start your adventure!
      </div>
    )
  }

  const completed = completedLessons[course.id]?.has(lesson.id) ?? false
  const gradient = pastelGradients[lessonIndex % pastelGradients.length]

  const hasContentBlocks = lesson.content_blocks.length > 0

  const hasPrev = lessonIndex > 0
  const hasNext = lessonIndex < course.lessons.length - 1

  return (
    <ScrollArea className="flex-1">
      <div className={cn("min-h-full bg-gradient-to-b p-6 md:p-10", gradient)}>
        <div className="mx-auto max-w-2xl space-y-8">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-center">
            {lesson.title}
          </h1>

          {hasContentBlocks ? (
            <ContentBlockRenderer
              blocks={lesson.content_blocks}
              imageClassName="w-full rounded-2xl shadow-md"
            />
          ) : (
            <div className="text-lg leading-relaxed">
              <Markdown>{lesson.content}</Markdown>
            </div>
          )}

          {lesson.key_points.length > 0 && (
            <Card className="border-2 border-dashed">
              <CardContent className="pt-6 space-y-2">
                <h2 className="text-xl font-bold">What did we learn?</h2>
                <ul className="space-y-2">
                  {lesson.key_points.map((point, i) => (
                    <li key={i} className="flex items-start gap-2 text-lg">
                      <span className="text-xl">✨</span>
                      <Markdown className="inline">{point}</Markdown>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {lesson.quiz.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-center">Quiz Time!</h2>
              {lesson.quiz.map((q) => {
                const selected = quizAnswers[course.id]?.[q.id]
                const hasAnswered = selected !== undefined
                const isCorrect = selected === q.correct_index

                return (
                  <Card key={q.id} className="overflow-hidden">
                    <CardContent className="pt-6 space-y-4">
                      <p className="text-lg font-medium">
                        <Markdown>{q.question}</Markdown>
                      </p>
                      <div className="grid gap-2">
                        {q.options.map((option, idx) => {
                          const isSelected = selected === idx
                          const isCorrectOption = idx === q.correct_index

                          return (
                            <button
                              key={idx}
                              onClick={() => {
                                if (!hasAnswered) answerQuestion(course.id, q.id, idx)
                              }}
                              disabled={hasAnswered}
                              className={cn(
                                "rounded-xl border-2 p-4 text-left text-lg font-medium transition-all",
                                !hasAnswered && "hover:border-primary hover:bg-primary/5 cursor-pointer",
                                hasAnswered && isCorrectOption && "border-green-500 bg-green-50 dark:bg-green-950/30",
                                hasAnswered && isSelected && !isCorrect && "border-red-500 bg-red-50 dark:bg-red-950/30",
                                hasAnswered && !isSelected && !isCorrectOption && "opacity-50",
                              )}
                            >
                              {option}
                            </button>
                          )
                        })}
                      </div>
                      {hasAnswered && (
                        <div
                          className={cn(
                            "rounded-xl p-4 text-base",
                            isCorrect
                              ? "bg-green-50 text-green-800 dark:bg-green-950/30 dark:text-green-300"
                              : "bg-red-50 text-red-800 dark:bg-red-950/30 dark:text-red-300"
                          )}
                        >
                          <span className="font-bold">
                            {isCorrect ? "Great job! 🎉" : "Not quite! 🤔"}
                          </span>{" "}
                          <Markdown>{q.explanation}</Markdown>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}

          <div className="flex items-center justify-between gap-4 pb-8">
            <Button
              variant="outline"
              size="lg"
              onClick={() => {
                if (hasPrev) setActiveLesson(course.lessons[lessonIndex - 1].id)
              }}
              disabled={!hasPrev}
              className="rounded-xl text-lg"
            >
              Previous
            </Button>

            <Button
              onClick={() => markLessonCompleted(course.id, lesson.id)}
              disabled={completed}
              variant={completed ? "secondary" : "default"}
              size="lg"
              className="rounded-xl text-lg"
            >
              {completed ? (
                <>
                  <CheckCircle2 className="text-green-600" />
                  Done!
                </>
              ) : (
                "I Got It!"
              )}
            </Button>

            <Button
              variant="outline"
              size="lg"
              onClick={() => {
                if (hasNext) setActiveLesson(course.lessons[lessonIndex + 1].id)
              }}
              disabled={!hasNext}
              className="rounded-xl text-lg"
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </ScrollArea>
  )
}
