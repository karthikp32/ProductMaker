import { agents, type AgentStage } from "./ProgressTracker";
import { cn } from "@/lib/utils";
import {
  FileText,
  DollarSign,
  Layout,
  Code,
  Database,
  Target,
  UserCheck,
} from "lucide-react";

export interface AgentOutput {
  agentId: AgentStage;
  title: string;
  items: { label: string; value: string }[];
  isComplete: boolean;
}

interface ContentPanelProps {
  outputs: AgentOutput[];
  currentStage: number;
  className?: string;
}

const outputIcons: Record<AgentStage, React.ElementType> = {
  "product-manager": FileText,
  "financial-analyst": DollarSign,
  "ui-designer": Layout,
  "frontend-engineer": Code,
  "backend-engineer": Database,
  "marketing": Target,
  "sales": UserCheck,
};

export function ContentPanel({ outputs, currentStage, className }: ContentPanelProps) {
  const currentAgent = agents[currentStage];

  return (
    <div className={cn("flex-1 overflow-y-auto p-6", className)}>
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Current Agent Banner */}
        {currentAgent && currentStage < agents.length && (
          <div className="content-card border-primary/20 bg-primary/5 animate-fade-in">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground animate-pulse-soft">
                <currentAgent.icon className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-semibold text-foreground">
                  {currentAgent.name} is working...
                </h2>
                <p className="text-sm text-muted-foreground">
                  Analyzing your idea and generating insights
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Agent Outputs */}
        {outputs.map((output, index) => {
          const agent = agents.find((a) => a.id === output.agentId);
          const OutputIcon = outputIcons[output.agentId];

          return (
            <div
              key={output.agentId}
              className="content-card animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="mb-4 flex items-center gap-3">
                <div
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-xl",
                    output.isComplete ? "bg-success/10" : "bg-secondary"
                  )}
                >
                  <OutputIcon
                    className={cn(
                      "h-5 w-5",
                      output.isComplete ? "text-success" : "text-muted-foreground"
                    )}
                  />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{output.title}</h3>
                  <p className="text-xs text-muted-foreground">
                    by {agent?.name}
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {output.items.map((item, itemIndex) => (
                  <div
                    key={itemIndex}
                    className="rounded-lg bg-secondary/50 p-3"
                  >
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-1">
                      {item.label}
                    </p>
                    <p className="text-sm text-foreground">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {/* Empty State */}
        {outputs.length === 0 && currentStage === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-secondary">
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold text-foreground">
              Getting started...
            </h3>
            <p className="max-w-sm text-sm text-muted-foreground">
              Our AI agents are preparing to analyze your idea. Results will appear here as each agent completes their work.
            </p>
          </div>
        )}

        {/* Completion State */}
        {currentStage >= agents.length && (
          <div className="content-card border-success/20 bg-success/5 text-center animate-fade-in">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-success">
              <UserCheck className="h-7 w-7 text-success-foreground" />
            </div>
            <h2 className="mb-2 text-xl font-bold text-foreground">
              Experiment Complete!
            </h2>
            <p className="text-muted-foreground">
              All agents have finished their analysis. Review the outputs above to see your product blueprint.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
