import { Link, useLocation } from "react-router"
import { BookOpen, GraduationCap, Lightbulb } from "lucide-react"
import { cn } from "@/lib/utils"

export function Navbar() {
  const location = useLocation()
  const links = [
    { to: "/explain", label: "Explain", icon: Lightbulb },
    { to: "/courses", label: "Courses", icon: GraduationCap },
  ]
  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center px-4 mx-auto max-w-6xl">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg mr-8">
          <BookOpen className="h-5 w-5" />
          Explaino
        </Link>
        <nav className="flex items-center gap-1">
          {links.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                location.pathname.startsWith(to)
                  ? "bg-secondary text-secondary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  )
}
