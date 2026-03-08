import { useEffect } from "react"
import { useCourseStore } from "@/store/useCourseStore"
import { CourseGeneratorForm } from "@/components/course/CourseGeneratorForm"
import { CourseList } from "@/components/course/CourseList"

export function CoursesPage() {
  const { loadCourses } = useCourseStore()

  useEffect(() => {
    loadCourses().catch(() => {})
  }, [loadCourses])

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Course Generator</h1>
        <p className="text-muted-foreground mt-1">Generate AI-powered courses on any topic</p>
      </div>
      <CourseGeneratorForm />
      <CourseList />
    </div>
  )
}
