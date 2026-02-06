import {
  Briefcase,
  Calculator,
  Palette,
  Code2,
  Server,
  Megaphone,
  Users,
  Check,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type AgentStage =
  | "product-manager"
  | "financial-analyst"
  | "ui-designer"
  | "frontend-engineer"
  | "backend-engineer"
  | "marketing"
  | "sales";

export interface Agent {
  id: AgentStage;
  name: string;
  shortName: string;
  icon: React.ElementType;
  colorClass: string;
}

export const agents: Agent[] = [
  {
    id: "product-manager",
    name: "Product Manager",
    shortName: "PM",
    icon: Briefcase,
    colorClass: "text-agent-pm",
  },
  {
    id: "financial-analyst",
    name: "Financial Analyst",
    shortName: "Finance",
    icon: Calculator,
    colorClass: "text-agent-finance",
  },
  {
    id: "ui-designer",
    name: "UI Designer",
    shortName: "Design",
    icon: Palette,
    colorClass: "text-agent-design",
  },
  {
    id: "frontend-engineer",
    name: "Frontend Engineer",
    shortName: "Frontend",
    icon: Code2,
    colorClass: "text-agent-frontend",
  },
  {
    id: "backend-engineer",
    name: "Backend Engineer",
    shortName: "Backend",
    icon: Server,
    colorClass: "text-agent-backend",
  },
  {
    id: "marketing",
    name: "Marketing Agent",
    shortName: "Marketing",
    icon: Megaphone,
    colorClass: "text-agent-marketing",
  },
  {
    id: "sales",
    name: "Sales Agent",
    shortName: "Sales",
    icon: Users,
    colorClass: "text-agent-sales",
  },
];

interface ProgressTrackerProps {
  currentStage: number;
  className?: string;
}

export function ProgressTracker({ currentStage, className }: ProgressTrackerProps) {
  return (
    <div className={cn("w-full bg-card border-b border-border", className)}>
      <div className="mx-auto max-w-5xl px-4 py-4">
        <div className="flex items-center justify-between">
          {agents.map((agent, index) => {
            const isComplete = index < currentStage;
            const isActive = index === currentStage;
            const isPending = index > currentStage;
            const Icon = agent.icon;

            return (
              <div key={agent.id} className="flex flex-1 items-center">
                {/* Agent Node */}
                <div className="flex flex-col items-center gap-2">
                  <div
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-full transition-all duration-500 md:h-12 md:w-12",
                      isComplete && "bg-success text-success-foreground",
                      isActive && "bg-primary text-primary-foreground shadow-soft-lg animate-pulse-soft",
                      isPending && "bg-secondary text-muted-foreground"
                    )}
                  >
                    {isComplete ? (
                      <Check className="h-5 w-5" />
                    ) : isActive ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <span
                    className={cn(
                      "text-xs font-medium transition-colors duration-300 hidden md:block",
                      isComplete && "text-success",
                      isActive && "text-primary",
                      isPending && "text-muted-foreground"
                    )}
                  >
                    {agent.shortName}
                  </span>
                </div>

                {/* Connector Line */}
                {index < agents.length - 1 && (
                  <div
                    className={cn(
                      "mx-2 h-0.5 flex-1 rounded-full transition-all duration-500",
                      index < currentStage ? "bg-success" : "bg-border"
                    )}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
