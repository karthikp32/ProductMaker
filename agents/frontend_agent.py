import os
import json
import logging
from typing import Dict, Any, List
from core.base_agent import BaseAgent
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

class FrontendAgent(BaseAgent):
    """
    Frontend SWE Agent: Owns the 'Interaction'.
    Reads design JSONs and generates a React + TypeScript application.
    """
    def __init__(self, name: str, event_bus: EventBus):
        super().__init__(name, event_bus)

    @property
    def role(self) -> str:
        return "Frontend Engineer: UX/UI design and implementation."

    @property
    def functions(self) -> list:
        return []

    def handle_instruction(self, instruction: str, context: Dict[str, Any]):
        """
        Handles explicit instructions to build the frontend.
        """
        if "build" in instruction.lower() and "industry" in context:
             self.generate_code_from_designs(context["industry"])

    def generate_code_from_designs(self, industry: str):
        """
        Reads designs from output/{industry}/designs/ and generates a React app.
        """
        design_dir = os.path.abspath(f"output/{industry}/designs")
        output_dir = os.path.abspath(f"output/{industry}/frontend")

        if not os.path.exists(design_dir):
            logger.error(f"Design directory not found: {design_dir}")
            print(f"Error: Design directory not found: {design_dir}")
            return

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # 1. Scaffolding (package.json, tsconfig, etc.)
        self._create_scaffolding(output_dir, industry)

        # 2. Read designs and generate pages/components
        design_files = [f for f in os.listdir(design_dir) if f.endswith(".json")]
        if not design_files:
            logger.warning("No design files found.")
            print("Warning: No design files found.")
            return

        for design_file in design_files:
            with open(os.path.join(design_dir, design_file), 'r') as f:
                try:
                    design_data = json.load(f)
                    self._generate_from_design(output_dir, design_data)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse {design_file}")

        print(f"Frontend successfully built in {output_dir}")

    def _create_scaffolding(self, output_dir: str, app_name: str):
        """
        Creates the basic file structure for a Vite + React + TS app.
        """
        # package.json
        package_json = {
            "name": app_name.lower().replace(" ", "-"),
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.66",
                "@types/react-dom": "^18.2.22",
                "@vitejs/plugin-react": "^4.2.1",
                "typescript": "^5.2.2",
                "vite": "^5.2.0"
            }
        }
        self._write_file(output_dir, "package.json", json.dumps(package_json, indent=2))

        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }
        self._write_file(output_dir, "tsconfig.json", json.dumps(tsconfig, indent=2))
        
        # tsconfig.node.json
        tsconfig_node = {
            "compilerOptions": {
                "composite": True,
                "skipLibCheck": True,
                "module": "ESNext",
                "moduleResolution": "bundler",
                "allowSyntheticDefaultImports": True
            },
            "include": ["vite.config.ts"]
        }
        self._write_file(output_dir, "tsconfig.node.json", json.dumps(tsconfig_node, indent=2))

        # vite.config.ts
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
})
"""
        self._write_file(output_dir, "vite.config.ts", vite_config)

        # index.html
        index_html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
        self._write_file(output_dir, "index.html", index_html)

        # src directory
        src_dir = os.path.join(output_dir, "src")
        os.makedirs(src_dir, exist_ok=True)

        # src/main.tsx
        main_tsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
        self._write_file(src_dir, "main.tsx", main_tsx)

        # src/index.css
        self._write_file(src_dir, "index.css", "/* Global styles */\nbody { font-family: sans-serif; margin: 0; padding: 0; }")

        # src/App.tsx (Initial placeholder)
        app_tsx = """import React from 'react';

function App() {
  return (
    <div>
      <h1>Welcome to {app_name}</h1>
    </div>
  );
}

export default App;
"""
        self._write_file(src_dir, "App.tsx", app_tsx)


    def _generate_from_design(self, output_dir: str, design: Dict[str, Any]):
        """
        Parses design JSON and generates components.
        Expected JSON structure (example):
        {
            "pages": [
                {
                    "name": "Home",
                    "components": [
                        {"name": "Hero", "props": {...}},
                        {"name": "Features", "props": {...}}
                    ]
                }
            ]
        }
        """
        src_dir = os.path.join(output_dir, "src")
        components_dir = os.path.join(src_dir, "components")
        os.makedirs(components_dir, exist_ok=True)

        pages = design.get("pages", [])
        
        # Keep track of created components to export them
        created_components = []

        for page in pages:
            page_name = page.get("name", "UnknownPage")
            components = page.get("components", [])
            
            # Generate Component files
            for comp in components:
                comp_name = comp.get("name", "UnnamedComponent")
                if comp_name not in created_components:
                    self._create_component(components_dir, comp_name, comp)
                    created_components.append(comp_name)

            # Update App.tsx or create Page component (Simplification: updating App.tsx for single page or creating routes)
            # For this MVP, let's just create a Page component and have App render the first one.
            self._create_page(src_dir, page_name, components)

        # Update App.tsx to render the pages (Rudimentary routing or just showing the first page)
        if pages:
            first_page = pages[0].get("name", "Home")
            app_tsx = f"""import React from 'react';
import {{ {first_page} }} from './{first_page}';

function App() {{
  return (
    <div>
      <{first_page} />
    </div>
  );
}}

export default App;
"""
            self._write_file(src_dir, "App.tsx", app_tsx)


    def _create_component(self, target_dir: str, name: str, details: Dict[str, Any]):
        """
        Creates a basic React component file.
        """
        description = details.get("description", "A component")
        
        # Very basic template
        content = f"""import React from 'react';

interface {name}Props {{
  // Define props here based on usage
}}

/**
 * {description}
 */
export const {name}: React.FC<{name}Props> = (props) => {{
  return (
    <div className="{name.lower()}-container" style={{{{border: '1px solid #ccc', padding: '1rem', margin: '1rem'}}}}>
      <h2>{name}</h2>
      <p>{description}</p>
    </div>
  );
}};
"""
        self._write_file(target_dir, f"{name}.tsx", content)

    def _create_page(self, target_dir: str, name: str, components: List[Dict[str, Any]]):
        """
        Creates a Page component which aggregates other components.
        """
        imports = ""
        jsx_elements = ""
        
        for comp in components:
            comp_name = comp.get("name")
            imports += f"import {{ {comp_name} }} from './components/{comp_name}';\n"
            jsx_elements += f"      <{comp_name} />\n"

        content = f"""import React from 'react';
{imports}

export const {name}: React.FC = () => {{
  return (
    <div className="page-{name.lower()}">
      <h1>{name}</h1>
      {jsx_elements}
    </div>
  );
}};
"""
        self._write_file(target_dir, f"{name}.tsx", content)

    def _write_file(self, directory: str, filename: str, content: str):
        with open(os.path.join(directory, filename), 'w') as f:
            f.write(content)
        logger.info(f"Wrote {filename} to {directory}")
