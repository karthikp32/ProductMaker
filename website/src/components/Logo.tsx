import { Sparkles } from "lucide-react";

interface LogoProps {
  className?: string;
}

export function Logo({ className }: LogoProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary">
        <Sparkles className="h-5 w-5 text-primary-foreground" />
      </div>
      <span className="text-xl font-semibold tracking-tight text-foreground">
        ProductMaker
      </span>
    </div>
  );
}
