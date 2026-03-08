import { Link } from "react-router"
import { ArrowRight, BookOpen, Lightbulb, GraduationCap, GitBranch, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export function HomePage() {
  return (
    <div className="container mx-auto max-w-6xl px-4">
      {/* Hero */}
      <section className="flex flex-col items-center text-center py-20 gap-6">
        <div className="flex items-center gap-2 text-muted-foreground text-sm font-medium">
          <BookOpen className="h-4 w-4" />
          AI-powered learning
        </div>
        <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
          Learn anything, deeply
        </h1>
        <p className="text-lg text-muted-foreground max-w-[600px]">
          Explore topics through branching explanations or generate structured
          courses tailored to your level. Powered by AI, designed for curiosity.
        </p>
        <div className="flex gap-3 mt-2">
          <Button asChild size="lg">
            <Link to="/explain">
              Start Exploring
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link to="/courses">Browse Courses</Link>
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="grid md:grid-cols-2 gap-6 pb-20">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 mb-2">
              <div className="rounded-md bg-primary/10 p-2">
                <Lightbulb className="h-5 w-5 text-primary" />
              </div>
              <GitBranch className="h-4 w-4 text-muted-foreground" />
            </div>
            <CardTitle>Explanation Explorer</CardTitle>
            <CardDescription>
              Dive into any topic and branch out through related concepts. Each
              explanation links to deeper sub-topics, creating a DFS-like
              exploration tree you control.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="text-sm text-muted-foreground space-y-1.5">
              <li>Branching, depth-first exploration</li>
              <li>Follow-up questions at every node</li>
              <li>Visual tree sidebar for navigation</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 mb-2">
              <div className="rounded-md bg-primary/10 p-2">
                <GraduationCap className="h-5 w-5 text-primary" />
              </div>
              <Users className="h-4 w-4 text-muted-foreground" />
            </div>
            <CardTitle>Course Generator</CardTitle>
            <CardDescription>
              Generate full courses on any subject, tailored for three audience
              modes: beginner, intermediate, or expert. Each course comes with
              structured lessons and clear progression.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="text-sm text-muted-foreground space-y-1.5">
              <li>3 audience levels to choose from</li>
              <li>AI-generated lesson outlines</li>
              <li>Structured, progressive learning</li>
            </ul>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
