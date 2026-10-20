/**
 * Workflow and component type definitions
 */

export type NodeType = 'data-source' | 'transform' | 'ml-model' | 'output';

export type NodeStatus = 'idle' | 'running' | 'completed' | 'failed';

export interface ComponentConfig {
  type: NodeType;
  label: string;
  icon: string;
  description: string;
  inputs: {
    name: string;
    type: string;
    required: boolean;
  }[];
  outputs: {
    name: string;
    type: string;
  }[];
  parameters: {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select';
    label: string;
    default?: any;
    options?: string[];
  }[];
}

export interface WorkflowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: {
    label: string;
    config: ComponentConfig;
    parameters: Record<string, any>;
    status?: NodeStatus;
    result?: any;
    error?: string;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}
