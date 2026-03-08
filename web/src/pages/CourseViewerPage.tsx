import { useEffect } from "react"
import { useParams } from "react-router"
import { useCourseStore } from "@/store/useCourseStore"
import { LessonSidebar } from "@/components/course/LessonSidebar"
import { LessonContent } from "@/components/course/LessonContent"
import { Skeleton } from "@/components/ui/skeleton"

export function CourseViewerPage() {
  const { courseId } = useParams()
  const { courses, loadCourse, loading } = useCourseStore()
  const course = courseId ? courses[courseId] : undefined

  useEffect(() => {
    if (courseId && !course) {
      loadCourse(courseId).catch(() => {})
    }
  }, [courseId, course, loadCourse])

  if (loading && !course) {
    return (
      <div className="flex h-[calc(100vh-3.5rem)]">
        <div className="w-64 border-r p-4 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
        <div className="flex-1 p-8 space-y-4">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <p className="text-muted-foreground">Course not found</p>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <LessonSidebar course={course} />
      <LessonContent course={course} />
    </div>
  )
}
