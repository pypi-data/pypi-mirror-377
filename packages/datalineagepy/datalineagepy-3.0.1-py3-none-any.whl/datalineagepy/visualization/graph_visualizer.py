"""
Graph visualization for data lineage using Plotly and NetworkX.
"""

import plotly.graph_objects as go
import plotly.offline as pyo
import networkx as nx
from typing import Dict, List, Optional, Tuple, Any
import base64
import io
import json

from ..core.tracker import LineageTracker


class GraphVisualizer:
    """
    Visualizes data lineage graphs using various formats (HTML, PNG).
    """

    def __init__(self, tracker: LineageTracker):
        """
        Initialize the graph visualizer.

        Args:
            tracker: LineageTracker instance to visualize
        """
        self.tracker = tracker
        self.graph = None
        self._build_graph()

    def _build_graph(self):
        """Build NetworkX graph from tracker data."""
        self.graph = nx.DiGraph()

        # Add nodes
        for node_id, node in self.tracker.nodes.items():
            self.graph.add_node(
                node_id,
                name=node.name,
                node_type=getattr(node, 'node_type', 'data'),
                metadata=node.metadata
            )

        # Add edges
        for edge in self.tracker.edges:
            self.graph.add_edge(
                edge.source_id,
                edge.target_id,
                operation=edge.operation.operation_type if edge.operation else 'unknown',
                metadata=edge.metadata
            )

    def generate_html(self,
                      output_file: Optional[str] = None,
                      width: int = 1200,
                      height: int = 800,
                      show_labels: bool = True) -> str:
        """
        Generate HTML visualization of the lineage graph.

        Args:
            output_file: Optional file path to save HTML
            width: Width of the visualization
            height: Height of the visualization
            show_labels: Whether to show node labels

        Returns:
            HTML string of the visualization
        """
        if not self.graph.nodes():
            return "<html><body><h2>No lineage data to visualize</h2></body></html>"

        # Calculate layout
        pos = nx.spring_layout(self.graph, k=3, iterations=50)

        # Prepare node traces
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text' if show_labels else 'markers',
            hoverinfo='text',
            marker=dict(
                size=20,
                color=[],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    thickness=15,
                    len=0.5,
                    x=1.02,
                    title="Node Type"
                )
            ),
            textposition="middle center"
        )

        # Color mapping for node types
        node_colors = {'data': 0, 'file': 1, 'database': 2}

        for node_id in self.graph.nodes():
            x, y = pos[node_id]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])

            node_info = self.graph.nodes[node_id]
            node_type = node_info.get('node_type', 'data')
            node_name = node_info.get('name', node_id)

            node_trace['text'] += tuple([node_name[:15] +
                                        '...' if len(node_name) > 15 else node_name])
            node_trace['marker']['color'] += tuple(
                [node_colors.get(node_type, 0)])

        # Prepare edge traces
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])

        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text=f'Data Lineage Graph - {self.tracker.name}',
                    font=dict(size=16)
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        text="DataLineagePy Visualization",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor="left", yanchor="bottom",
                        font=dict(color="gray", size=12)
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False,
                           showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False,
                           showticklabels=False),
                width=width,
                height=height
            )
        )

        # Generate HTML
        html_str = pyo.plot(fig, output_type='div', include_plotlyjs=True)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_str)

        return html_str

    def generate_png(self,
                     output_file: str,
                     width: int = 1200,
                     height: int = 800,
                     dpi: int = 300) -> bytes:
        """
        Generate PNG image of the lineage graph.

        Args:
            output_file: File path to save PNG
            width: Width of the image
            height: Height of the image
            dpi: DPI for the image

        Returns:
            PNG image as bytes
        """
        if not self.graph.nodes():
            # Create simple error image with PIL
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (width, height), color='white')
                draw = ImageDraw.Draw(img)
                text = "No lineage data to visualize"
                try:
                    draw.text((width//2, height//2), text,
                              fill='black', anchor='mm')
                except:
                    # Fallback for older PIL versions
                    draw.text((width//2 - 100, height//2), text, fill='black')

                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                png_bytes = buffer.getvalue()

                with open(output_file, 'wb') as f:
                    f.write(png_bytes)

                return png_bytes
            except ImportError:
                # Create minimal byte array
                png_bytes = b''
                with open(output_file, 'wb') as f:
                    f.write(png_bytes)
                return png_bytes

        # Use matplotlib for PNG generation
        try:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=dpi)

            # Calculate layout
            pos = nx.spring_layout(self.graph, k=3, iterations=50)

            # Draw edges
            nx.draw_networkx_edges(
                self.graph, pos, ax=ax,
                edge_color='gray', arrows=True,
                arrowsize=20, arrowstyle='->'
            )

            # Draw nodes with different colors for different types
            node_colors = []
            for node_id in self.graph.nodes():
                node_type = self.graph.nodes[node_id].get('node_type', 'data')
                if node_type == 'file':
                    node_colors.append('lightblue')
                elif node_type == 'database':
                    node_colors.append('lightgreen')
                else:
                    node_colors.append('lightcoral')

            nx.draw_networkx_nodes(
                self.graph, pos, ax=ax,
                node_color=node_colors, node_size=1000
            )

            # Draw labels
            labels = {}
            for node_id in self.graph.nodes():
                name = self.graph.nodes[node_id].get('name', node_id)
                labels[node_id] = name[:10] + '...' if len(name) > 10 else name

            nx.draw_networkx_labels(
                self.graph, pos, labels, ax=ax, font_size=8)

            ax.set_title(
                f'Data Lineage Graph - {self.tracker.name}', fontsize=16)
            ax.axis('off')

            plt.tight_layout()

            # Save to bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='PNG', dpi=dpi, bbox_inches='tight')
            png_bytes = buffer.getvalue()

            # Save to file
            with open(output_file, 'wb') as f:
                f.write(png_bytes)

            plt.close()
            return png_bytes

        except ImportError:
            # Fallback: create simple image with PIL if available
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (width, height), color='white')
                draw = ImageDraw.Draw(img)

                # Simple text-based visualization
                y_offset = 50
                draw.text(
                    (20, 20), f"Data Lineage Graph - {self.tracker.name}", fill='black')

                for i, (node_id, node_data) in enumerate(self.graph.nodes(data=True)):
                    name = node_data.get('name', node_id)
                    draw.text((20, y_offset + i * 30),
                              f"• {name}", fill='blue')

                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                png_bytes = buffer.getvalue()

                with open(output_file, 'wb') as f:
                    f.write(png_bytes)

                return png_bytes
            except ImportError:
                # Final fallback
                png_bytes = b''
                with open(output_file, 'wb') as f:
                    f.write(png_bytes)
                return png_bytes

    def export_to_dot(self, output_file: str) -> str:
        """
        Export lineage graph to DOT format for Graphviz.

        Args:
            output_file: File path to save DOT file

        Returns:
            DOT format string
        """
        dot_lines = ['digraph lineage {']
        dot_lines.append('  rankdir=TB;')
        dot_lines.append('  node [shape=box, style=filled];')

        # Add nodes
        for node_id, node_data in self.graph.nodes(data=True):
            name = node_data.get('name', node_id)
            node_type = node_data.get('node_type', 'data')

            color = 'lightblue' if node_type == 'file' else 'lightgreen' if node_type == 'database' else 'lightcoral'

            dot_lines.append(
                f'  "{node_id}" [label="{name}", fillcolor={color}];')

        # Add edges
        for edge in self.graph.edges(data=True):
            operation = edge[2].get('operation', 'unknown')
            dot_lines.append(
                f'  "{edge[0]}" -> "{edge[1]}" [label="{operation}"];')

        dot_lines.append('}')

        dot_content = '\n'.join(dot_lines)

        with open(output_file, 'w') as f:
            f.write(dot_content)

        return dot_content

    def export_to_json(self, output_file: str) -> Dict[str, Any]:
        """
        Export lineage graph to JSON format.

        Args:
            output_file: File path to save JSON file

        Returns:
            Dictionary representation of the graph
        """
        graph_data = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'tracker_name': self.tracker.name,
                'tracker_id': self.tracker.id,
                'created_at': self.tracker.created_at.isoformat(),
                'stats': self.get_graph_stats()
            }
        }

        # Add nodes
        for node_id, node_data in self.graph.nodes(data=True):
            graph_data['nodes'].append({
                'id': node_id,
                'name': node_data.get('name', node_id),
                'type': node_data.get('node_type', 'data'),
                'metadata': node_data.get('metadata', {})
            })

        # Add edges
        for edge in self.graph.edges(data=True):
            graph_data['edges'].append({
                'source': edge[0],
                'target': edge[1],
                'operation': edge[2].get('operation', 'unknown'),
                'metadata': edge[2].get('metadata', {})
            })

        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)

        return graph_data

    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the lineage graph.

        Returns:
            Dictionary containing graph statistics
        """
        if not self.graph or self.graph.number_of_nodes() == 0:
            return {
                'nodes': 0,
                'edges': 0,
                'connected_components': 0,
                'average_degree': 0,
                'node_types': {},
                'is_dag': True,
                'longest_path': 0
            }

        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'connected_components': nx.number_weakly_connected_components(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            'node_types': self._count_node_types(),
            'is_dag': nx.is_directed_acyclic_graph(self.graph),
            'longest_path': len(nx.dag_longest_path(self.graph)) if nx.is_directed_acyclic_graph(self.graph) else None
        }

    def _count_node_types(self) -> Dict[str, int]:
        """Count nodes by type."""
        counts = {}
        for node_id, node_data in self.graph.nodes(data=True):
            node_type = node_data.get('node_type', 'data')
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts
