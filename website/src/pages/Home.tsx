import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { IdeaInput } from "@/components/IdeaInput";
import { Button } from "@/components/ui/button";
import { Sparkles, Zap, BarChart3, Github, ShieldCheck, Rocket, CircleDollarSign } from "lucide-react";

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

const pricingPlans = [
  {
    name: "Free Gift",
    price: "$0",
    cadence: "",
    credits: "10 Credits",
    outcome: "Full Market Research & MVP Scope (Image 2 PM Stage)",
    highlight: false,
  },
  {
    name: "Founder",
    price: "$29",
    cadence: "/ mo",
    credits: "40 Credits",
    outcome: "Weekly iteration on product strategy and Finance ROI.",
    highlight: true,
    planId: "founder",
  },
  {
    name: "Growth",
    price: "$99",
    cadence: "/ mo",
    credits: "150 Credits",
    outcome: "One \"Full Run\" (Idea to Launch) + extra for refinements.",
    highlight: false,
    planId: "growth",
  },
  {
    name: "Foundry Pack",
    price: "$79",
    cadence: "one-time",
    credits: "130 Credits",
    outcome: "A single, high-intent \"Experiment Launch\" (Image 1 CTA).",
    highlight: false,
    planId: "foundry-pack",
  },
];

const valueTable = [
  {
    agent: "Product Manager",
    action: "Problem ID & MVP Scope",
    productMaker: "$10.00",
    alternative: "$2,000 (Freelance PM)",
  },
  {
    agent: "Finance",
    action: "ROI & Revenue Model",
    productMaker: "$5.00",
    alternative: "$1,500 (Financial Analyst)",
  },
  {
    agent: "UI Designer",
    action: "Architecture & Design System",
    productMaker: "$15.00",
    alternative: "$3,000 (Design Agency)",
  },
  {
    agent: "Engineering (FE/BE)",
    action: "Production Code & API",
    productMaker: "$60.00",
    alternative: "$15,000+ (Contract Devs)",
  },
  {
    agent: "Marketing & Sales",
    action: "Launch Plan & Outreach",
    productMaker: "$21.00",
    alternative: "$3,500/mo (AI SDR Tiers)",
  },
];

export default function Home() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const isProd = import.meta.env.PROD;
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";
  const isCheckoutEnabled = Boolean(import.meta.env.VITE_STRIPE_CHECKOUT_ENABLED);
  const [credits, setCredits] = useState(10);

  useEffect(() => {
    const token = window.localStorage.getItem("pm_token");
    if (!token) {
      return;
    }
    const loadCredits = async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          return;
        }
        const payload = await res.json();
        if (typeof payload?.user?.credits === "number") {
          setCredits(payload.user.credits);
        }
      } catch (err) {
        return;
      }
    };
    loadCredits();
  }, [apiBaseUrl]);

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

  const handleCheckout = async (planId?: string) => {
    if (!planId) return;
    const token = window.localStorage.getItem("pm_token");
    if (!token) {
      alert("Please sign in before checking out.");
      return;
    }
    const res = await fetch(`${apiBaseUrl}/billing/checkout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ plan: planId }),
    });
    if (!res.ok) {
      alert("Checkout could not be started. Please try again.");
      return;
    }
    const payload = await res.json();
    if (payload.url) {
      window.location.href = payload.url;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Logo />
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-border bg-secondary/40 px-3 py-1 text-xs font-semibold text-foreground md:flex">
              Credits: <span className="text-primary">{credits}</span>
            </div>
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
              <div className="flex items-center gap-2 rounded-full border border-border bg-secondary/40 px-3 py-1 text-xs font-semibold text-foreground">
                Credits: <span className="text-primary">{credits}</span>
              </div>
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

      {/* Pricing Section */}
      <section id="pricing" className="border-t border-border bg-background py-24">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mb-12 text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
              <CircleDollarSign className="h-4 w-4" />
              Foundry Plans
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Choose your credits</h2>
            <p className="mx-auto mt-3 max-w-2xl text-muted-foreground">
              Move from idea to launch without friction. Pick the credit pack that matches your build velocity.
            </p>
          </div>

          <div className="grid gap-6 lg:grid-cols-4">
            {pricingPlans.map((plan) => (
              <div
                key={plan.name}
                className={`content-card flex h-full flex-col justify-between ${
                  plan.highlight ? "border-primary shadow-soft-lg" : ""
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-foreground">{plan.name}</h3>
                    {plan.highlight && (
                      <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                        Popular
                      </span>
                    )}
                  </div>
                  <div className="mt-4 flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-foreground">{plan.price}</span>
                    <span className="text-sm text-muted-foreground">{plan.cadence}</span>
                  </div>
                  <div className="mt-4 text-sm font-semibold text-primary">{plan.credits}</div>
                  <p className="mt-4 text-sm text-muted-foreground">{plan.outcome}</p>
                </div>
                <div className="mt-6">
                  {plan.planId ? (
                    <Button
                      className="w-full"
                      variant={plan.highlight ? "hero" : "outline"}
                      onClick={() => handleCheckout(plan.planId)}
                      disabled={!isCheckoutEnabled}
                    >
                      {isCheckoutEnabled ? "Start checkout" : "Checkout soon"}
                    </Button>
                  ) : (
                    <Button className="w-full" variant="soft">
                      Start free
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Value Section */}
      <section className="border-t border-border bg-secondary/40 py-24">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mb-10 text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
              <Rocket className="h-4 w-4" />
              Agent Value vs Alternatives
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground">
              Replace a $25,000+ workflow with one autonomous run
            </h2>
            <p className="mx-auto mt-3 max-w-2xl text-muted-foreground">
              ProductMaker compresses a fragmented human/SaaS stack into a single credit-based execution pipeline.
            </p>
          </div>

          <div className="overflow-hidden rounded-2xl border border-border bg-background">
            <div className="grid grid-cols-4 gap-0 border-b border-border bg-secondary/40 px-6 py-3 text-sm font-semibold text-muted-foreground">
              <div>Agent</div>
              <div>Action Performed</div>
              <div>ProductMaker Cost</div>
              <div>Alternative Cost</div>
            </div>
            {valueTable.map((row) => (
              <div
                key={row.agent}
                className="grid grid-cols-4 gap-0 border-b border-border px-6 py-4 text-sm text-foreground last:border-b-0"
              >
                <div className="font-semibold">{row.agent}</div>
                <div className="text-muted-foreground">{row.action}</div>
                <div className="font-semibold text-primary">{row.productMaker}</div>
                <div className="text-muted-foreground">{row.alternative}</div>
              </div>
            ))}
          </div>
          <div className="mt-6 flex flex-col items-center gap-3 text-center text-sm text-muted-foreground">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-primary">
              Full Run: Launched Business — $79.00 vs $25,000 - $50,000+
            </div>
            <span>Foundry Pack is designed for one high-intent experiment launch.</span>
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
