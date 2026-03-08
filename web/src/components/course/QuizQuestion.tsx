import { CheckCircle2, XCircle } from "lucide-react"
import type { QuizQuestion as QuizQuestionType } from "@/types/course"
import { useCourseStore } from "@/store/useCourseStore"
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { cn } from "@/lib/utils"

interface QuizQuestionProps {
  question: QuizQuestionType
  courseId: string
}

export function QuizQuestion({ question, courseId }: QuizQuestionProps) {
  const { quizAnswers, answerQuestion } = useCourseStore()

  const selectedAnswer = quizAnswers[courseId]?.[question.id]
  const hasAnswered = selectedAnswer !== undefined
  const isCorrect = selectedAnswer === question.correct_index

  const handleAnswer = (value: string) => {
    if (hasAnswered) return
    answerQuestion(courseId, question.id, Number(value))
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-medium">
          {question.question}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <RadioGroup
          value={hasAnswered ? String(selectedAnswer) : undefined}
          onValueChange={handleAnswer}
          disabled={hasAnswered}
        >
          {question.options.map((option, index) => {
            const isSelected = selectedAnswer === index
            const isCorrectOption = index === question.correct_index

            return (
              <label
                key={index}
                className={cn(
                  "flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors",
                  hasAnswered && isCorrectOption && "border-green-500 bg-green-50 dark:bg-green-950/20",
                  hasAnswered && isSelected && !isCorrect && "border-red-500 bg-red-50 dark:bg-red-950/20",
                  !hasAnswered && "hover:bg-muted"
                )}
              >
                <RadioGroupItem value={String(index)} />
                <span className="flex-1 text-sm">{option}</span>
                {hasAnswered && isCorrectOption && (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                )}
                {hasAnswered && isSelected && !isCorrect && (
                  <XCircle className="h-4 w-4 text-red-600" />
                )}
              </label>
            )
          })}
        </RadioGroup>

        {hasAnswered && (
          <div
            className={cn(
              "rounded-lg p-3 text-sm",
              isCorrect
                ? "bg-green-50 text-green-800 dark:bg-green-950/20 dark:text-green-300"
                : "bg-red-50 text-red-800 dark:bg-red-950/20 dark:text-red-300"
            )}
          >
            <span className="font-medium">
              {isCorrect ? "Correct!" : "Incorrect."}
            </span>{" "}
            {question.explanation}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
