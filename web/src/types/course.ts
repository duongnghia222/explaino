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

export interface ImageBlock {
  id: string
  url: string | null
  alt_text: string
  prompt: string
  placeholder: boolean
}

export interface Citation {
  id: string
  title: string
  url: string
  snippet: string
}

export interface ContentBlock {
  type: "text" | "image"
  text?: string | null
  image?: ImageBlock | null
}

export interface LessonResponse {
  id: string
  title: string
  content: string
  content_blocks: ContentBlock[]
  citations: Citation[]
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