import { apiFetch } from "./client"
import type { GenerateCourseRequest, CourseResponse } from "@/types/course"

export function postGenerateCourse(req: GenerateCourseRequest) {
  return apiFetch<CourseResponse>("/api/courses", {
    method: "POST",
    body: JSON.stringify(req),
  })
}

export function getCourses() {
  return apiFetch<CourseResponse[]>("/api/courses")
}

export function getCourse(id: string) {
  return apiFetch<CourseResponse>(`/api/courses/${id}`)
}
