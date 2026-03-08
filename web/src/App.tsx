import { BrowserRouter, Routes, Route } from "react-router"
import { RootLayout } from "@/components/layout/RootLayout"
import { HomePage } from "@/pages/HomePage"
import { ExplainPage } from "@/pages/ExplainPage"
import { CoursesPage } from "@/pages/CoursesPage"
import { CourseViewerPage } from "@/pages/CourseViewerPage"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<RootLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/explain" element={<ExplainPage />} />
          <Route path="/explain/:nodeId" element={<ExplainPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/courses/:courseId" element={<CourseViewerPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
