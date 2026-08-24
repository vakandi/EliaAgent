---
name: vision-mcp
description: Multi-provider image analysis MCP (Mistral + OpenRouter :free models). Multi-image support (Qwen VL, Gemma 3, Mistral, Llama vision). Best models tested for product images.
---

# Vision-MCP Skill

Multi-provider image analysis using Mistral and OpenRouter free models.

## ⚠️ CRITICAL: Best Models for Product Images

Based on testing with e-commerce product images:

| Rank | Model | Multi-Image | Best For | Status |
|------|-------|-------------|----------|--------|
| 🥇 | `nvidia/nemotron-nano-12b-v2-vl:free` | ❌ | **OCR, product identification** | ✅ Works |
| 🥈 | `openrouter/free` | ❌ | General analysis (auto-selects) | ✅ Works |
| 🥉 | `google/gemma-3-4b-it:free` | ✅ (8) | Fast, detailed descriptions | ✅ Works |
| 🥉 | `google/gemma-3-27b-it:free` | ✅ (8) | Larger model, better detail | ✅ Works |
| ⚠️ | `mistral` (pixtral-large-latest) | ✅ (8) | Paid, high quality | ⚠️ Rate limited |
| 🆕 | `qwen/qwen2.5-vl-72b-instruct:free` | ✅ (8) | **Best overall** - OCR/struct/extraction | ✅ Works |
| 🆕 | `qwen/qwen2.5-vl-32b-instruct:free` | ✅ (8) | Good balance speed/accuracy | ✅ Works |
| 🆕 | `meta-llama/llama-3.2-11b-vision-instruct:free` | ✅ (8) | Contextual understanding | ✅ Works |

## 🖼️ Multi-Image Support

Models with `multi_image: True` accept up to **8 images** in a single API call — all images are sent in one content array for combined analysis.

Models without multi-image support use **only the first image** (with a warning in the response).

```bash
# Multi-image comparison (Qwen VL, Gemma 3, Mistral, Llama vision)
mcp-cli call vision-mcp analyze_image '{"image_paths": ["shot1.jpg","shot2.jpg","shot3.jpg"], "prompt": "Compare these product angles, list differences"}'
```

## Available Tools

```bash
# Analyze image(s) with specific model
mcp-cli call vision-mcp analyze_image '{"image_paths": ["/path/to/image.jpg"], "prompt": "Describe", "model": "nvidia/nemotron-nano-12b-v2-vl:free"}'

# Extract text (OCR) — multi-image supported
mcp-cli call vision-mcp extract_text '{"image_paths": ["/path/to/image.jpg"]}'

# Extract structured JSON — multi-image supported
mcp-cli call vision-mcp extract_structured_from_image '{"image_paths": ["/path/to.jpg"], "format_json": "{\"brand\": \"...\", \"price\": \"...\"}"}'

# List all models (filter by multi-image capability)
mcp-cli call vision-mcp list_models '{"free_only": true}'
mcp-cli call vision-mcp list_models '{"multi_image_only": true}'

# Get model info
mcp-cli call vision-mcp vision_model_info '{}'

# Check API keys
mcp-cli call vision-mcp check_api_keys '{}'
```

## Usage Examples

### Product Image Analysis (Best)
```bash
mcp-cli call vision-mcp analyze_image '{
  "image_paths": ["~/Downloads/46526.png"],
  "prompt": "This is a product image. Product: Pull Prada €100. Describe brand, color, design, text visible",
  "model": "nvidia/nemotron-nano-12b-v2-vl:free"
}'
```

### Multi-Image Product Comparison
```bash
mcp-cli call vision-mcp analyze_image '{
  "image_paths": ["~/Downloads/product1.png","~/Downloads/product2.png"],
  "prompt": "Compare these two products: brand differences, price tags, condition",
  "model": "qwen/qwen2.5-vl-72b-instruct:free"
}'
```

### OCR / Text Extraction
```bash
mcp-cli call vision-mcp extract_text '{
  "image_paths": ["~/Downloads/46526.png"],
  "model": "nvidia/nemotron-nano-12b-v2-vl:free"
}'
```

### When Rate Limited
If OpenRouter free models are rate-limited, use:
```bash
# Use Mistral instead
mcp-cli call vision-mcp analyze_image '{"image_paths": ["/path/to.jpg"], "prompt": "Describe", "provider": "mistral"}'
```

## Test Results Summary

| Model | Multi-Image | Product Detection | OCR | Notes |
|-------|-------------|------------------|-----|-------|
| nvidia/nemotron-nano-12b-v2-vl:free | ❌ | ✅ Excellent | ✅ Best | Best single-image OCR |
| openrouter/free | ❌ | ✅ Good | ✅ Good | Safest fallback |
| google/gemma-3-4b-it:free | ✅ | ✅ Good | ⚠️ Fabric details | Fast + multi-image |
| google/gemma-3-27b-it:free | ✅ | ✅ Good | ✅ Good | Better than 4b |
| qwen/qwen2.5-vl-72b-instruct:free | ✅ | ✅ Excellent | ✅ Excellent | **Best overall** |
| mistral (pixtral) | ✅ | ✅ Excellent | ✅ Excellent | Paid, rate limited |

## API Keys

Config file: `~/mcps_server/vision_mcp/.env`

- `MISTRAL_API_KEY` - For Mistral provider
- `OPENROUTER_API_KEY` - For OpenRouter provider
- `DEFAULT_PROVIDER` - Set to "openrouter" or "mistral"
