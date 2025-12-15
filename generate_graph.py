"""
Generate graph.png - LangGraph Visualization
============================================

This script generates a visual diagram of your LangGraph topology.
Save as: generate_graph.py
Run: python generate_graph.py
"""

# METHOD 1: Try to generate PNG (requires pygraphviz)
def method1_png():
    """Generate actual PNG image"""
    try:
        from main import build_agent_graph
        
        print("Building graph...")
        app = build_agent_graph()
        
        print("Generating PNG...")
        graph_png = app.get_graph().draw_mermaid_png()
        
        with open("graph.png", "wb") as f:
            f.write(graph_png)
        
        print("✓ SUCCESS: graph.png created!")
        print("Check your folder for graph.png")
        return True
        
    except Exception as e:
        print(f"✗ Method 1 failed: {e}")
        return False

# METHOD 2: Generate Mermaid code (always works)
def method2_mermaid():
    """Generate Mermaid code for online visualization"""
    try:
        from main import build_agent_graph
        
        print("\nBuilding graph...")
        app = build_agent_graph()
        
        print("Generating Mermaid code...")
        mermaid_code = app.get_graph().draw_mermaid()
        
        # Save to file
        with open("graph.mmd", "w") as f:
            f.write(mermaid_code)
        
        print("✓ SUCCESS: graph.mmd created!")
        print("\nTo visualize:")
        print("1. Go to: https://mermaid.live")
        print("2. Paste the content of graph.mmd")
        print("3. Export as PNG")
        print("4. Save as graph.png")
        
        # Also print it
        print("\n" + "="*60)
        print("MERMAID CODE (copy this to mermaid.live):")
        print("="*60)
        print(mermaid_code)
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"✗ Method 2 failed: {e}")
        return False

# METHOD 3: Create a simple diagram manually
def method3_simple_diagram():
    """Create a simple text-based diagram"""
    
    diagram = """
    ┌─────────────────────────────────────────────────────────────┐
    │              AI TRAVEL ASSISTANT ARCHITECTURE               │
    └─────────────────────────────────────────────────────────────┘
    
                            USER INPUT
                                │
                                ↓
                        ┌───────────────┐
                        │ Extract City  │
                        └───────┬───────┘
                                │
                                ↓
                    ┌───────────────────────┐
                    │   Check Database      │
                    │   (Decision Node)     │
                    └───────┬───────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
            IN DB?                  NOT IN DB?
                │                       │
                ↓                       ↓
        ┌──────────────┐        ┌──────────────┐
        │  Get from    │        │ Web Search   │
        │  Database    │        │  (Tavily)    │
        └──────┬───────┘        └──────┬───────┘
               │                       │
               └───────────┬───────────┘
                           │
                           ↓
                ┌──────────────────────┐
                │  PARALLEL FETCH      │
                │  ┌────────────────┐  │
                │  │ Weather API    │  │
                │  └────────────────┘  │
                │  ┌────────────────┐  │
                │  │ Image API      │  │
                │  └────────────────┘  │
                └──────────┬───────────┘
                           │
                           ↓
                ┌──────────────────────┐
                │  Combine Results     │
                │  (Structured JSON)   │
                └──────────┬───────────┘
                           │
                           ↓
                ┌──────────────────────┐
                │  STREAMLIT UI        │
                │  - Summary           │
                │  - Weather Chart     │
                │  - Image Gallery     │
                └──────────────────────┘
    
    KEY FEATURES:
    ─────────────
    ★ Intelligent Routing: Database vs Web Search
    ★ Parallel Execution: Weather + Images fetched simultaneously  
    ★ Structured Output: Clean JSON for visualization
    ★ State Management: Full conversation context maintained
    """
    
    # Save as text file
    with open("architecture_diagram.txt", "w") as f:
        f.write(diagram)
    
    print("✓ Created: architecture_diagram.txt")
    print("\nYou can:")
    print("1. Convert this to an image using any tool")
    print("2. Or create graph.png manually based on this structure")
    
    print(diagram)
    return True

# METHOD 4: Create a simple PNG using matplotlib (backup)
def method4_matplotlib():
    """Create diagram using matplotlib"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Title
        ax.text(5, 11.5, 'AI Travel Assistant Architecture', 
                ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Define node positions
        nodes = {
            'User Input': (5, 10),
            'Extract City': (5, 9),
            'Check Database': (5, 7.5),
            'Get Database': (3, 6),
            'Web Search': (7, 6),
            'Parallel Fetch': (5, 4.5),
            'Combine Results': (5, 3),
            'Streamlit UI': (5, 1.5)
        }
        
        # Draw nodes
        for name, (x, y) in nodes.items():
            if name == 'Check Database':
                # Decision node (diamond shape)
                box = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6,
                                    boxstyle="round,pad=0.1",
                                    facecolor='#FFE5B4', 
                                    edgecolor='#FF6B6B', linewidth=2)
            elif name in ['Get Database', 'Web Search']:
                # Data source nodes
                box = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6,
                                    boxstyle="round,pad=0.1",
                                    facecolor='#B4E5FF', 
                                    edgecolor='#4ECDC4', linewidth=2)
            elif name == 'Parallel Fetch':
                # Parallel execution node
                box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8,
                                    boxstyle="round,pad=0.1",
                                    facecolor='#D4FFB4', 
                                    edgecolor='#45B7D1', linewidth=2)
            else:
                # Regular nodes
                box = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6,
                                    boxstyle="round,pad=0.1",
                                    facecolor='#E8E8E8', 
                                    edgecolor='#666', linewidth=2)
            ax.add_patch(box)
            ax.text(x, y, name, ha='center', va='center', 
                   fontsize=10, fontweight='bold')
        
        # Draw arrows
        arrows = [
            (nodes['User Input'], nodes['Extract City']),
            (nodes['Extract City'], nodes['Check Database']),
            (nodes['Check Database'], nodes['Get Database']),
            (nodes['Check Database'], nodes['Web Search']),
            (nodes['Get Database'], nodes['Parallel Fetch']),
            (nodes['Web Search'], nodes['Parallel Fetch']),
            (nodes['Parallel Fetch'], nodes['Combine Results']),
            (nodes['Combine Results'], nodes['Streamlit UI']),
        ]
        
        for (x1, y1), (x2, y2) in arrows:
            arrow = FancyArrowPatch((x1, y1-0.35), (x2, y2+0.35),
                                   arrowstyle='->', mutation_scale=20,
                                   color='#666', linewidth=2)
            ax.add_patch(arrow)
        
        # Add labels
        ax.text(2.5, 6.7, 'Known City', fontsize=8, style='italic', color='#FF6B6B')
        ax.text(7.5, 6.7, 'Unknown City', fontsize=8, style='italic', color='#FF6B6B')
        ax.text(5.8, 4.5, 'Weather +\nImages', fontsize=8, ha='center')
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color='#FFE5B4', label='Decision Point'),
            mpatches.Patch(color='#B4E5FF', label='Data Source'),
            mpatches.Patch(color='#D4FFB4', label='Parallel Execution'),
            mpatches.Patch(color='#E8E8E8', label='Processing Node')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('graph.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print("✓ SUCCESS: graph.png created using matplotlib!")
        print("Check your folder for graph.png")
        return True
        
    except Exception as e:
        print(f"✗ Method 4 failed: {e}")
        return False

# MAIN EXECUTION
if __name__ == "__main__":
    print("="*60)
    print("GRAPH VISUALIZATION GENERATOR")
    print("="*60)
    
    print("\n[1/4] Trying to generate PNG directly...")
    if method1_png():
        print("\n✓ Done! You have graph.png")
        exit(0)
    
    print("\n[2/4] Trying matplotlib method...")
    if method4_matplotlib():
        print("\n✓ Done! You have graph.png")
        exit(0)
    
    print("\n[3/4] Generating Mermaid code...")
    if method2_mermaid():
        print("\n✓ Mermaid code generated!")
        print("Follow the instructions above to create graph.png")
    
    print("\n[4/4] Creating text diagram...")
    method3_simple_diagram()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("graph.mmd created - use mermaid.live to convert to PNG")
    print("OR")
    print("Use the architecture_diagram.txt as reference to draw manually")
    print("="*60)