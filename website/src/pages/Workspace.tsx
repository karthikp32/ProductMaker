import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { ProgressTracker, agents, type AgentStage } from "@/components/ProgressTracker";
import { ChatPanel, type ChatMessage } from "@/components/ChatPanel";
import { ContentPanel, type AgentOutput } from "@/components/ContentPanel";
import { Button } from "@/components/ui/button";
import { ArrowLeft, PanelLeftClose, PanelLeft } from "lucide-react";

// Simulated agent outputs
const generateAgentOutput = (agentId: AgentStage, idea: string): AgentOutput => {
  const outputs: Record<AgentStage, () => AgentOutput> = {
    "product-manager": () => ({
      agentId,
      title: "Product Definition",
      items: [
        { label: "Problem Statement", value: `Users struggle with ${idea.toLowerCase()}. Current solutions are fragmented and inefficient.` },
        { label: "Target User", value: "Tech-savvy professionals aged 25-45 who value automation and efficiency." },
        { label: "MVP Scope", value: "Core workflow automation, simple dashboard, basic integrations with popular tools." },
      ],
      isComplete: true,
    }),
    "financial-analyst": () => ({
      agentId,
      title: "Financial Analysis",
      items: [
        { label: "Pricing Strategy", value: "Freemium model with $29/mo Pro tier and $99/mo Team tier." },
        { label: "Unit Economics", value: "CAC: $45, LTV: $580, LTV/CAC ratio: 12.9x (healthy)" },
        { label: "Revenue Projection", value: "Year 1: $120K ARR, Year 2: $480K ARR with 15% MoM growth." },
      ],
      isComplete: true,
    }),
    "ui-designer": () => ({
      agentId,
      title: "Design Direction",
      items: [
        { label: "Visual Style", value: "Clean, minimal interface with soft shadows and generous whitespace. Primary blue accents." },
        { label: "Key Screens", value: "Dashboard, Workflow Builder, Settings, and Onboarding flow." },
        { label: "Design Principles", value: "Clarity over cleverness. Progressive disclosure. Delightful micro-interactions." },
      ],
      isComplete: true,
    }),
    "frontend-engineer": () => ({
      agentId,
      title: "Frontend Architecture",
      items: [
        { label: "Tech Stack", value: "React 18, TypeScript, TailwindCSS, Zustand for state, React Query for data." },
        { label: "Key Components", value: "WorkflowCanvas, NodeEditor, DashboardGrid, OnboardingWizard" },
        { label: "Performance", value: "Code splitting, lazy loading, optimistic updates for instant feel." },
      ],
      isComplete: true,
    }),
    "backend-engineer": () => ({
      agentId,
      title: "Backend Architecture",
      items: [
        { label: "Infrastructure", value: "Serverless on AWS Lambda with PostgreSQL (RDS) and Redis caching." },
        { label: "API Design", value: "REST API with OpenAPI spec. WebSocket for real-time workflow updates." },
        { label: "Security", value: "JWT auth, row-level security, encrypted secrets, SOC 2 compliance path." },
      ],
      isComplete: true,
    }),
    "marketing": () => ({
      agentId,
      title: "Go-to-Market Strategy",
      items: [
        { label: "Positioning", value: `The simplest way to ${idea.toLowerCase()}. Built for teams who move fast.` },
        { label: "Launch Channels", value: "Product Hunt, Hacker News, Twitter/X, targeted LinkedIn ads." },
        { label: "Content Strategy", value: "Weekly blog posts, YouTube tutorials, case studies with early adopters." },
      ],
      isComplete: true,
    }),
    "sales": () => ({
      agentId,
      title: "Sales Strategy",
      items: [
        { label: "ICP", value: "Series A-C startups, 20-200 employees, product or engineering led." },
        { label: "Sales Motion", value: "Product-led growth with self-serve. Sales-assist for Team tier." },
        { label: "Outreach", value: "Personalized cold email sequences, demo request follow-ups within 2 hours." },
      ],
      isComplete: true,
    }),
  };

  return outputs[agentId]();
};

export default function Workspace() {
  const navigate = useNavigate();
  const [idea] = useState(() => sessionStorage.getItem("productIdea") || "Build a productivity app");
  const [currentStage, setCurrentStage] = useState(0);
  const [outputs, setOutputs] = useState<AgentOutput[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showChat, setShowChat] = useState(true);

  // Initialize with user's idea
  useEffect(() => {
    setMessages([
      {
        id: "1",
        role: "user",
        content: idea,
        timestamp: new Date(),
      },
      {
        id: "2",
        role: "assistant",
        content: `Great idea! I'm launching an experiment to explore "${idea}". Our AI agents will analyze the market, define the product, design the experience, and create a go-to-market strategy.\n\nWatch the progress bar above to see each agent complete their work.`,
        timestamp: new Date(),
      },
    ]);
  }, [idea]);

  // Simulate agent progression
  useEffect(() => {
    if (currentStage >= agents.length) return;

    const timer = setTimeout(() => {
      const agent = agents[currentStage];
      const output = generateAgentOutput(agent.id, idea);
      setOutputs((prev) => [...prev, output]);

      // Add chat message
      setIsTyping(true);
      setTimeout(() => {
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: "assistant",
            content: `✅ ${agent.name} has completed their analysis. Check out the ${output.title.toLowerCase()} in the main panel.`,
            timestamp: new Date(),
          },
        ]);
        setCurrentStage((prev) => prev + 1);
      }, 1000);
    }, 3000 + Math.random() * 2000);

    return () => clearTimeout(timer);
  }, [currentStage, idea]);

  const handleSendMessage = useCallback((content: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        role: "user",
        content,
        timestamp: new Date(),
      },
    ]);

    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "I'm currently focused on running your experiment. Once all agents complete, I can help you dive deeper into any specific area. Feel free to ask questions!",
          timestamp: new Date(),
        },
      ]);
    }, 1500);
  }, []);

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Top Bar */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-card px-4">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="hidden sm:inline">Back</span>
          </Button>
          <Logo />
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowChat(!showChat)}
          className="gap-2"
        >
          {showChat ? (
            <>
              <PanelLeftClose className="h-4 w-4" />
              <span className="hidden sm:inline">Hide Chat</span>
            </>
          ) : (
            <>
              <PanelLeft className="h-4 w-4" />
              <span className="hidden sm:inline">Show Chat</span>
            </>
          )}
        </Button>
      </header>

      {/* Progress Tracker */}
      <ProgressTracker currentStage={currentStage} />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat Panel */}
        {showChat && (
          <div className="w-80 shrink-0 border-r border-border lg:w-96">
            <ChatPanel
              messages={messages}
              onSendMessage={handleSendMessage}
              isTyping={isTyping}
              className="h-full"
            />
          </div>
        )}

        {/* Content Panel */}
        <ContentPanel
          outputs={outputs}
          currentStage={currentStage}
          className="bg-secondary/30"
        />
      </div>
    </div>
  );
}
