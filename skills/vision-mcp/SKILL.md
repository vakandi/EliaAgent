---
name: vision-mcp
description: Multi-provider image analysis MCP (Mistral + OpenRouter :free models). Best models tested for product images.
---

# Vision-MCP Skill

Multi-provider image analysis using Mistral and OpenRouter free models.

## ⚠️ CRITICAL: Best Models for Product Images

Based on testing with e-commerce product images:

| Rank | Model | Best For | Status |
|------|-------|----------|--------|
| 🥇 | `nvidia/nemotron-nano-12b-v2-vl:free` | **OCR, product identification** | ✅ Works |
| 🥈 | `openrouter/free` | General analysis (auto-selects) | ✅ Works |
| 🥉 | `google/gemma-3-4b-it:free` | Fast, detailed descriptions | ✅ Works |
| ⚠️ | `mistral` (pixtral-large-latest) | Paid, high quality | ⚠️ Rate limited |

## Available Tools

```bash
# Analyze image with specific model
mcp-cli call vision-mcp analyze_image '{"image_path": "/path/to/image.jpg", "prompt": "Describe", "model": "nvidia/nemotron-nano-12b-v2-vl:free"}'

# Extract text (OCR)
mcp-cli call vision-mcp extract_text '{"image_path": "/path/to/image.jpg"}'

# Extract structured JSON
mcp-cli call vision-mcp extract_structured_from_image '{"image_path": "/path/to.jpg", "format_json": "{\"brand\": \"...\", \"price\": \"...\"}"}'

# List all models
mcp-cli call vision-mcp list_models '{"free_only": true}'

# Check API keys
mcp-cli call vision-mcp check_api_keys '{}'
```

## Usage Examples

### Product Image Analysis (Best)
```bash
mcp-cli call vision-mcp analyze_image '{
  "image_path": "/home/user/Downloads/46526.png",
  "prompt": "This is a product image. Product: Pull Prada €100. Describe brand, color, design, text visible",
  "model": "nvidia/nemotron-nano-12b-v2-vl:free"
}'
```

### OCR / Text Extraction
```bash
mcp-cli call vision-mcp extract_text '{
  "image_path": "/home/user/Downloads/46526.png",
  "model": "nvidia/nemotron-nano-12b-v2-vl:free"
}'
```

### When Rate Limited
If OpenRouter free models are rate-limited, use:
```bash
# Use Mistral instead
mcp-cli call vision-mcp analyze_image '{"image_path": "/path/to.jpg", "prompt": "Describe", "provider": "mistral"}'
```

## Test Results Summary

| Model | Product Detection | OCR | Notes |
|-------|------------------|-----|-------|
| nvidia/nemotron-nano-12b-v2-vl:free | ✅ Excellent | ✅ Best | Best overall |
| openrouter/free | ✅ Good | ✅ Good | Most reliable |
| google/gemma-3-4b-it:free | ✅ Good | ⚠️ Fabric details | Fast |
| mistral (pixtral) | ✅ Excellent | ✅ Excellent | Paid, rate limited |

## API Keys

Config file: `/path/to/Documents/mcps_server/vision_mcp/.env`

- `MISTRAL_API_KEY` - For Mistral provider
- `OPENROUTER_API_KEY` - For OpenRouter provider
- `DEFAULT_PROVIDER` - Set to "openrouter" or "mistral"
