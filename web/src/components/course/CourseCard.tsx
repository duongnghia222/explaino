import { Link } from "react-router"
import { BookOpen } from "lucide-react"
import type { CourseResponse } from "@/types/course"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface CourseCardProps {
  course: CourseResponse
}

const modeBadgeVariant: Record<string, "default" | "secondary" | "outline"> = {
  kids: "secondary",
  normal: "default",
  advanced: "outline",
}

export function CourseCard({ course }: CourseCardProps) {
  return (
    <Link to={`/courses/${course.id}`} className="block">
      <Card className="transition-shadow hover:shadow-md">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg">{course.title}</CardTitle>
            <Badge variant={modeBadgeVariant[course.mode] ?? "default"}>
              {course.mode}
            </Badge>
          </div>
          <CardDescription className="line-clamp-2">
            {course.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <BookOpen className="h-4 w-4" />
            <span>
              {course.lessons.length}{" "}
              {course.lessons.length === 1 ? "lesson" : "lessons"}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
