import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { IdeaInput } from "@/components/IdeaInput";
import { Button } from "@/components/ui/button";
import { Sparkles, Zap, BarChart3, Github, ShieldCheck } from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Agents",
    description: "Seven specialized agents work together to build your product",
  },
  {
    icon: Zap,
    title: "Instant Execution",
    description: "From idea to actionable artifacts in minutes, not months",
  },
  {
    icon: BarChart3,
    title: "Real Validation",
    description: "Learn what users want before writing a single line of code",
  },
];

export default function Home() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const isProd = import.meta.env.PROD;
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

  const handleLaunch = (idea: string) => {
    setIsLoading(true);
    // Store idea and navigate to workspace
    sessionStorage.setItem("productIdea", idea);
    setTimeout(() => {
      navigate("/workspace");
    }, 500);
  };

  const handleOAuth = (provider: "google" | "github") => {
    window.location.href = `${apiBaseUrl}/auth/login/${provider}`;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Logo />
          <div className="flex items-center gap-3">
            <a
              href="#how-it-works"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              How it works
            </a>
            {isProd && (
              <div className="hidden items-center gap-2 md:flex">
                <Button variant="outline" size="sm" onClick={() => handleOAuth("google")}>
                  <ShieldCheck className="h-4 w-4" />
                  Sign in with Google
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleOAuth("github")}>
                  <Github className="h-4 w-4" />
                  Sign in with GitHub
                </Button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex min-h-screen flex-col items-center justify-center px-6 pt-16">
        <div className="stagger-children mx-auto max-w-4xl text-center">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
            <Sparkles className="h-4 w-4" />
            Autonomous Product Development
          </div>

          {/* Headline */}
          <h1 className="mb-6 text-5xl font-bold leading-tight tracking-tight text-foreground md:text-6xl lg:text-7xl">
            Turn ideas into
            <br />
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              real products
            </span>
          </h1>

          {/* Subheadline */}
          <p className="mx-auto mb-12 max-w-xl text-lg text-muted-foreground md:text-xl">
            Describe what you want to build. Our AI agents handle product
            management, design, engineering, marketing, and sales — automatically.
          </p>

          {/* Input */}
          <div className="flex justify-center">
            <IdeaInput onSubmit={handleLaunch} isLoading={isLoading} />
          </div>
          {isProd && (
            <div className="mt-6 flex flex-col items-center gap-3 md:hidden">
              <Button variant="outline" onClick={() => handleOAuth("google")}>
                <ShieldCheck className="h-4 w-4" />
                Sign in with Google
              </Button>
              <Button variant="outline" onClick={() => handleOAuth("github")}>
                <Github className="h-4 w-4" />
                Sign in with GitHub
              </Button>
            </div>
          )}
        </div>
      </main>

      {/* Features Section */}
      <section id="how-it-works" className="border-t border-border bg-secondary/30 py-24">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-4 text-center text-3xl font-bold tracking-tight text-foreground">
            How it works
          </h2>
          <p className="mx-auto mb-16 max-w-xl text-center text-muted-foreground">
            Seven AI agents collaborate to transform your idea into a validated product concept
          </p>

          <div className="grid gap-8 md:grid-cols-3">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="content-card text-center transition-all duration-300 hover:-translate-y-1"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
                  <feature.icon className="h-7 w-7 text-primary" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="mx-auto max-w-6xl px-6 text-center text-sm text-muted-foreground">
          © 2025 ProductMaker. Build what matters.
        </div>
      </footer>
    </div>
  );
}
