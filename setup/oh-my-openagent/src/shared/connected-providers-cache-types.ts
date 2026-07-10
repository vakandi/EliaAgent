export interface ModelMetadata {
  id: string
  provider?: string
  context?: number
  output?: number
  name?: string
  variants?: Record<string, unknown>
  limit?: {
    context?: number
    input?: number
    output?: number
  }
  modalities?: {
    input?: string[]
    output?: string[]
  }
  capabilities?: Record<string, unknown>
  reasoning?: boolean
  temperature?: boolean
  tool_call?: boolean
  [key: string]: unknown
}

export interface ProviderModelsCache {
  models: Record<string, string[] | ModelMetadata[]>
  connected: string[]
  updatedAt: string
}
