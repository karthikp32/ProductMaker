import React, { useMemo, useState, useEffect } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

const AGENT_SEQUENCE = [
  { id: "pm", name: "Product Manager" },
  { id: "ui", name: "UI Designer" },
  { id: "architect", name: "Architect" },
  { id: "frontend", name: "Frontend Engineer" },
  { id: "backend", name: "Backend Engineer" },
  { id: "marketing", name: "Marketing" },
  { id: "sales", name: "Sales" },
  { id: "analytics", name: "Data Analytics" }
];

const DEFAULT_PLAN = (agentName) => `Plan for ${agentName}:
1. Review requirements and constraints.
2. Propose solution approach.
3. Execute implementation tasks.
4. Validate outputs and handoff.`;

const initialAgentState = AGENT_SEQUENCE.reduce((acc, agent) => {
  acc[agent.id] = {
    status: "needs_plan",
    plan: "",
    approved: false,
    output: ""
  };
  return acc;
}, {});

const mockFiles = [
  {
    name: "product-brief.md",
    type: "file"
  },
  {
    name: "designs",
    type: "folder",
    children: [
      { name: "ui-wireframe.fig", type: "file" },
      { name: "brand-guidelines.md", type: "file" }
    ]
  },
  {
    name: "architecture",
    type: "folder",
    children: [
      { name: "system-diagram.png", type: "file" },
      { name: "service-map.md", type: "file" }
    ]
  },
  {
    name: "frontend",
    type: "folder",
    children: [
      { name: "App.jsx", type: "file" },
      { name: "styles.css", type: "file" }
    ]
  }
];

const starterEditor = `// App.jsx\nimport React from "react";\n\nexport default function ProductMakerApp() {\n  return (\n    <main>\n      <h1>ProductMaker</h1>\n      <p>Ship your product with agentic precision.</p>\n    </main>\n  );\n}\n`;

function fileNode(node, depth = 0) {
  const padding = { paddingLeft: `${depth * 12}px` };
  if (node.type === "folder") {
    return (
      <div key={node.name} className="file-node">
        <div className="file-row" style={padding}>
          <span className="file-icon">▸</span>
          <span className="file-name">{node.name}</span>
        </div>
        <div className="file-children">
          {node.children.map((child) => fileNode(child, depth + 1))}
        </div>
      </div>
    );
  }

  return (
    <div key={node.name} className="file-row" style={padding}>
      <span className="file-icon">•</span>
      <span className="file-name">{node.name}</span>
    </div>
  );
}

export default function App() {
  const [agentState, setAgentState] = useState(initialAgentState);
  const [selectedAgent, setSelectedAgent] = useState("pm");
  const [messages, setMessages] = useState([
    { from: "assistant", text: "Welcome back! Share the product idea and I will coordinate the crew." },
    { from: "user", text: "We need a workflow builder for growth teams." }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [editorValue, setEditorValue] = useState(starterEditor);
  const [desiredUrl, setDesiredUrl] = useState("productmaker.com/abc123");
  const [deployStatus, setDeployStatus] = useState("Not deployed");
  const [user, setUser] = useState(null);
  const [billing, setBilling] = useState({ paid: false, remaining: 5 });
  const [authError, setAuthError] = useState("");
  const [usageBusy, setUsageBusy] = useState(false);
  const [billingBusy, setBillingBusy] = useState(false);
  const [deployBusy, setDeployBusy] = useState(false);
  const [authToken, setAuthToken] = useState(() =>
    typeof window !== "undefined" ? window.localStorage.getItem("pm_token") : null
  );

  const progress = useMemo(() => {
    const doneCount = Object.values(agentState).filter((agent) => agent.status === "complete").length;
    return Math.round((doneCount / AGENT_SEQUENCE.length) * 100);
  }, [agentState]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const newToken = params.get("token");
    const error = params.get("error");
    if (newToken) {
      window.localStorage.setItem("pm_token", newToken);
      setAuthToken(newToken);
      params.delete("token");
      window.history.replaceState({}, "", window.location.pathname);
    }
    if (error) {
      setAuthError(error);
      params.delete("error");
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, []);

  useEffect(() => {
    if (!authToken) {
      setUser(null);
      return;
    }

    const fetchUser = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${authToken}` }
        });
        if (!res.ok) {
          setUser(null);
          return;
        }
        const payload = await res.json();
        setUser(payload.user);
        setBilling({ paid: payload.user.paid, remaining: payload.user.remaining });
      } catch (err) {
        setUser(null);
      }
    };

    fetchUser();
  }, [authToken]);

  const handleChatSend = () => {
    if (!chatInput.trim()) {
      return;
    }
    setMessages((prev) => [...prev, { from: "user", text: chatInput.trim() }]);
    setChatInput("");
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { from: "assistant", text: "Got it. I will feed this into the next agent plan." }
      ]);
    }, 400);
  };

  const updateAgent = (agentId, updates) => {
    setAgentState((prev) => ({
      ...prev,
      [agentId]: {
        ...prev[agentId],
        ...updates
      }
    }));
  };

  const handleGeneratePlan = (agentId) => {
    const agent = AGENT_SEQUENCE.find((entry) => entry.id === agentId);
    updateAgent(agentId, {
      status: "awaiting_approval",
      plan: DEFAULT_PLAN(agent?.name || agentId),
      approved: false
    });
  };

  const handleApprovePlan = (agentId) => {
    updateAgent(agentId, { approved: true, status: "ready_to_run" });
  };

  const handleImplement = (agentId) => {
    updateAgent(agentId, { status: "running" });
    setTimeout(() => {
      updateAgent(agentId, {
        status: "complete",
        output: "Implementation complete. Deliverables attached in workspace." }
      );
    }, 600);
  };

  const handleLogin = (provider) => {
    setAuthError("");
    window.location.href = `${API_BASE_URL}/auth/login/${provider}`;
  };

  const handleUsage = async () => {
    if (!authToken) {
      setAuthError("Please sign in to use the workspace.");
      return;
    }
    setUsageBusy(true);
    try {
      const res = await fetch(`${API_BASE_URL}/usage/consume`, {
        method: "POST",
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (res.ok) {
        const payload = await res.json();
        setBilling({ paid: payload.paid, remaining: payload.remaining });
      }
    } finally {
      setUsageBusy(false);
    }
  };

  const handleCheckout = async () => {
    if (!authToken) {
      setAuthError("Please sign in to upgrade.");
      return;
    }
    setBillingBusy(true);
    try {
      const res = await fetch(`${API_BASE_URL}/billing/checkout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (!res.ok) {
        setAuthError("Unable to start checkout. Check Stripe settings.");
        return;
      }
      const payload = await res.json();
      if (payload.url) {
        window.location.href = payload.url;
      }
    } finally {
      setBillingBusy(false);
    }
  };

  const handleDeploy = async () => {
    if (!authToken) {
      setAuthError("Please sign in to deploy.");
      return;
    }
    setDeployBusy(true);
    try {
      const res = await fetch(`${API_BASE_URL}/deploy`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify({ desired_url: desiredUrl })
      });
      if (res.ok) {
        const payload = await res.json();
        setDeployStatus(`Deployed to ${payload.url}`);
      }
    } finally {
      setDeployBusy(false);
    }
  };

  const activeAgent = agentState[selectedAgent];

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <div className="logo">PM</div>
          <div>
            <div className="brand-title">ProductMaker</div>
            <div className="brand-subtitle">Agentic product studio</div>
          </div>
        </div>
        <div className="topbar-actions">
          <div className="status-pill">
            <span>Workflow</span>
            <strong>{progress}%</strong>
          </div>
          <div className="status-pill">
            <span>Free Usage</span>
            <strong>{billing.paid ? "Unlimited" : `${billing.remaining} left`}</strong>
          </div>
          <button className="ghost" onClick={() => handleLogin("google")}>Sign in with Google</button>
          <button className="ghost" onClick={() => handleLogin("github")}>Sign in with GitHub</button>
        </div>
      </header>

      <main className="workspace">
        <section className="panel column-left">
          <div className="panel-header">
            <h2>Workspace</h2>
            <button className="primary" onClick={handleUsage} disabled={usageBusy}>
              {usageBusy ? "Processing..." : "Consume Usage"}
            </button>
          </div>
          <div className="auth-card">
            <div>
              <div className="label">Signed in as</div>
              <div className="value">{user ? user.name : "Guest"}</div>
            </div>
            <div>
              <div className="label">Plan</div>
              <div className="value">{billing.paid ? "Pro" : "Free"}</div>
            </div>
          </div>
          {authError && <div className="error">{authError}</div>}

          <div className="section-title">Folders</div>
          <div className="file-tree">
            {mockFiles.map((node) => fileNode(node))}
          </div>

          <div className="section-title">Deploy</div>
          <div className="deploy-card">
            <input
              value={desiredUrl}
              onChange={(event) => setDesiredUrl(event.target.value)}
              placeholder="productmaker.com/abc123"
            />
            <button className="primary" onClick={handleDeploy} disabled={deployBusy}>
              {deployBusy ? "Deploying..." : "Publish"}
            </button>
            <div className="deploy-status">{deployStatus}</div>
          </div>

          <div className="section-title">Billing</div>
          <div className="billing-card">
            <div>
              <div className="label">Upgrade to Pro</div>
              <div className="value">Unlock unlimited usage & deploys.</div>
            </div>
            <button className="primary" onClick={handleCheckout} disabled={billingBusy}>
              {billingBusy ? "Starting..." : "Stripe Checkout"}
            </button>
          </div>
        </section>

        <section className="panel column-center">
          <div className="panel-header">
            <h2>Agent Workflow</h2>
            <div className="progress-bar">
              <div className="progress" style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="agent-grid">
            {AGENT_SEQUENCE.map((agent) => {
              const state = agentState[agent.id];
              return (
                <button
                  key={agent.id}
                  className={`agent-card ${selectedAgent === agent.id ? "active" : ""}`}
                  onClick={() => setSelectedAgent(agent.id)}
                >
                  <div className="agent-name">{agent.name}</div>
                  <div className={`agent-status status-${state.status}`}>{state.status.replace(/_/g, " ")}</div>
                </button>
              );
            })}
          </div>

          <div className="agent-detail">
            <div className="agent-detail-header">
              <h3>{AGENT_SEQUENCE.find((agent) => agent.id === selectedAgent)?.name}</h3>
              <div className={`agent-status status-${activeAgent.status}`}>{activeAgent.status.replace(/_/g, " ")}</div>
            </div>
            <textarea
              className="plan-text"
              readOnly
              value={activeAgent.plan || "No plan yet. Generate one to get started."}
            />
            <div className="agent-actions">
              <button className="ghost" onClick={() => handleGeneratePlan(selectedAgent)}>
                Generate plan
              </button>
              <button
                className="ghost"
                disabled={activeAgent.status !== "awaiting_approval"}
                onClick={() => handleApprovePlan(selectedAgent)}
              >
                Approve plan
              </button>
              <button
                className="primary"
                disabled={activeAgent.status !== "ready_to_run"}
                onClick={() => handleImplement(selectedAgent)}
              >
                Implement
              </button>
            </div>
            <div className="agent-output">
              <div className="label">Output</div>
              <div className="value">{activeAgent.output || "Waiting on implementation."}</div>
            </div>
          </div>
        </section>

        <section className="panel column-right">
          <div className="panel-header">
            <h2>Editor</h2>
            <div className="tag">Live</div>
          </div>
          <textarea
            className="editor"
            value={editorValue}
            onChange={(event) => setEditorValue(event.target.value)}
          />

          <div className="panel-header">
            <h2>App Viewer</h2>
            <div className="tag">Preview</div>
          </div>
          <div className="app-viewer">
            <div className="app-preview">
              <div className="preview-header">
                <div className="preview-pill" />
                <div className="preview-pill" />
                <div className="preview-pill" />
              </div>
              <div className="preview-body">
                <h4>Growth Workflow Builder</h4>
                <p>Auto-assemble onboarding, activation, and monetization flows.</p>
                <button>Launch Demo</button>
              </div>
            </div>
          </div>

          <div className="panel-header">
            <h2>Chatbot</h2>
            <div className="tag">Agent Assist</div>
          </div>
          <div className="chatbot">
            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={`${msg.from}-${index}`} className={`chat-message ${msg.from}`}>
                  {msg.text}
                </div>
              ))}
            </div>
            <div className="chat-input">
              <input
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                placeholder="Ask an agent anything..."
              />
              <button className="primary" onClick={handleChatSend}>Send</button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
