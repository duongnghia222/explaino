import { BookOpen } from "lucide-react"
import { useCourseStore } from "@/store/useCourseStore"
import { CourseCard } from "./CourseCard"

export function CourseList() {
  const { courses } = useCourseStore()
  const courseList = Object.values(courses)

  if (courseList.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
        <BookOpen className="h-12 w-12" />
        <p className="text-lg font-medium">No courses yet</p>
        <p className="text-sm">Generate your first course to get started.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      {courseList.map((course) => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  )
}
