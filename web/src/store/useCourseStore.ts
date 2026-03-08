import { create } from "zustand"
import type { CourseResponse, CourseMode } from "@/types/course"
import { postGenerateCourse, getCourses, getCourse } from "@/api/courses"

interface CourseState {
  courses: Record<string, CourseResponse>
  activeCourseId: string | null
  activeLessonId: string | null
  completedLessons: Record<string, Set<string>>
  quizAnswers: Record<string, Record<string, number>>
  loading: boolean
  error: string | null
  generateCourse: (topic: string, mode: CourseMode) => Promise<string>
  loadCourses: () => Promise<void>
  loadCourse: (id: string) => Promise<void>
  setActiveCourse: (id: string) => void
  setActiveLesson: (lessonId: string) => void
  answerQuestion: (courseId: string, questionId: string, answerIndex: number) => void
  markLessonCompleted: (courseId: string, lessonId: string) => void
}

export const useCourseStore = create<CourseState>((set, get) => ({
  courses: {},
  activeCourseId: null,
  activeLessonId: null,
  completedLessons: {},
  quizAnswers: {},
  loading: false,
  error: null,

  generateCourse: async (topic: string, mode: CourseMode) => {
    set({ loading: true, error: null })
    try {
      const res = await postGenerateCourse({ topic, mode })
      set((s) => ({
        courses: { ...s.courses, [res.id]: res },
        activeCourseId: res.id,
        activeLessonId: res.lessons[0]?.id ?? null,
        loading: false,
      }))
      return res.id
    } catch (e) {
      set({ loading: false, error: (e as Error).message })
      throw e
    }
  },

  loadCourses: async () => {
    set({ loading: true, error: null })
    try {
      const list = await getCourses()
      const courses: Record<string, CourseResponse> = {}
      for (const c of list) courses[c.id] = c
      set({ courses, loading: false })
    } catch (e) {
      set({ loading: false, error: (e as Error).message })
      throw e
    }
  },

  loadCourse: async (id: string) => {
    set({ loading: true, error: null })
    try {
      const course = await getCourse(id)
      set((s) => ({
        courses: { ...s.courses, [course.id]: course },
        activeCourseId: course.id,
        activeLessonId: s.activeLessonId ?? course.lessons[0]?.id ?? null,
        loading: false,
      }))
    } catch (e) {
      set({ loading: false, error: (e as Error).message })
      throw e
    }
  },

  setActiveCourse: (id: string) => {
    const course = get().courses[id]
    set({
      activeCourseId: id,
      activeLessonId: course?.lessons[0]?.id ?? null,
    })
  },

  setActiveLesson: (lessonId: string) => {
    set({ activeLessonId: lessonId })
  },

  answerQuestion: (courseId: string, questionId: string, answerIndex: number) => {
    set((s) => ({
      quizAnswers: {
        ...s.quizAnswers,
        [courseId]: { ...s.quizAnswers[courseId], [questionId]: answerIndex },
      },
    }))
  },

  markLessonCompleted: (courseId: string, lessonId: string) => {
    set((s) => {
      const existing = s.completedLessons[courseId] ?? new Set()
      const updated = new Set(existing)
      updated.add(lessonId)
      return { completedLessons: { ...s.completedLessons, [courseId]: updated } }
    })
  },
}))
