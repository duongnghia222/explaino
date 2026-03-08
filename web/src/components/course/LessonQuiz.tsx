import type { QuizQuestion as QuizQuestionType } from "@/types/course"
import { QuizQuestion } from "./QuizQuestion"

interface LessonQuizProps {
  questions: QuizQuestionType[]
  courseId: string
}

export function LessonQuiz({ questions, courseId }: LessonQuizProps) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Quiz</h2>
      <div className="space-y-4">
        {questions.map((question) => (
          <QuizQuestion
            key={question.id}
            question={question}
            courseId={courseId}
          />
        ))}
      </div>
    </div>
  )
}
