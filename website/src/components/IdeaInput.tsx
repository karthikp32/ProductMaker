import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface IdeaInputProps {
  onSubmit: (idea: string) => void;
  isLoading?: boolean;
}

export function IdeaInput({ onSubmit, isLoading }: IdeaInputProps) {
  const [idea, setIdea] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (idea.trim()) {
      onSubmit(idea.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="relative">
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Describe your idea or customer segment…"
          className="input-chat min-h-[120px] resize-none pr-36"
          rows={3}
          disabled={isLoading}
        />
        <div className="absolute bottom-4 right-4">
          <Button
            type="submit"
            variant="hero"
            size="lg"
            disabled={!idea.trim() || isLoading}
            className="gap-2"
          >
            {isLoading ? (
              <span className="animate-pulse-soft">Starting...</span>
            ) : (
              <>
                Launch Experiment
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </div>
      <p className="mt-4 text-center text-sm text-muted-foreground">
        Press Enter or click to start building with AI agents
      </p>
    </form>
  );
}
