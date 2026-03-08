export type CourseMode = "kids" | "normal" | "advanced"

export interface GenerateCourseRequest {
  topic: string
  mode: CourseMode
}

export interface QuizQuestion {
  id: string
  question: string
  options: string[]
  correct_index: number
  explanation: string
}

export interface LessonResponse {
  id: string
  title: string
  content: string
  key_points: string[]
  quiz: QuizQuestion[]
}

export interface CourseResponse {
  id: string
  topic: string
  mode: CourseMode
  title: string
  description: string
  lessons: LessonResponse[]
  created_at: string
}
