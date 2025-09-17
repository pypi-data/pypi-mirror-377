# CCUX — AI-Powered Website Generator
CCUX uses **Claude AI** to transform a simple product description into production-ready code — no design tools required.

---

## Features

- **One-line generation** — describe your product and get a landing page or full site in minutes  
- **Professional themes** — choose from 13 styles (minimal, corporate, brutalist, animated, etc.)  
- **Precision editing** — regenerate specific sections without rebuilding everything  
- **Interactive workflow** — guided wizard for multi-page sites, live editing, and theme switching  
- **Production-ready output** — responsive HTML with TailwindCSS, SEO, and accessibility  

---

## Installation

```bash
pip install ccux
```

**Prerequisites:**  
- Python 3.9+  
- [Claude CLI](https://claude.ai/code) (used for AI generation)  

---

## Getting Started

### Interactive Mode (Recommended)

```bash
ccux init
```

The interactive terminal app provides:
- Guided website creation wizard  
- Visual project management  
- Live section editing and theme switching  
- Multi-page website generation  
- Form management and customization  
- Press `ESC` anytime to exit  

### Command Line Usage

```bash
# Generate single landing page
ccux gen --desc "AI project management tool" --theme minimal

# Generate complete multi-page website
ccux multipage --desc "SaaS platform for remote teams"

# Regenerate specific sections
ccux regen --section hero,pricing

# Load description from file
ccux gen --desc-file product.pdf --theme brutalist
```

---

## Commands Reference

### `ccux init`
Launch CCUX Interactive Application (Main Entry Point)

The primary interface providing guided project creation, management, and customization through rich terminal menus.

**Features:**
- Single-page project creation wizard with theme and form selection
- Multi-page website generation with intelligent page analysis and parallel processing
- Multi-project management and discovery
- Visual section regeneration with numbered selection
- Interactive theme switching with live preview
- Form management (contact, newsletter, signup forms)
- Built-in help system and workflows
- Content editing with natural language instructions
- **ESC Key Support**: Press ESC anywhere to immediately exit

```bash
ccux init
```

### `ccux gen`
Generate conversion-optimized landing page using AI design methodology

**Options:**
- `--desc, -d TEXT`: Product description
- `--desc-file FILE`: Path to file containing product description (supports .txt and .pdf files)
- `--url, -u URL`: Reference URLs (max 3, can be used multiple times)
- `--theme, -t THEME`: Design theme (default: minimal)
- `--no-design-thinking`: Skip full design process for faster generation
- `--include-forms`: Include contact forms in the landing page
- `--analyze-images/--no-analyze-images`: Enable/disable visual analysis of competitor screenshots (default: enabled, uses more tokens when enabled)
- `--output, -o DIR`: Output directory

**Examples:**
```bash
# Interactive mode (recommended)
ccux gen

# Full design process with theme
ccux gen --desc "AI project management tool" --theme brutalist

# Fast generation mode
ccux gen --desc "SaaS platform" --no-design-thinking

# With competitor analysis (visual analysis enabled by default)
ccux gen --desc "Video platform" --url https://loom.com --url https://vimeo.com

# Load description from PDF file
ccux gen --desc-file product-description.pdf --theme minimal

# Save tokens by disabling image analysis
ccux gen --desc "SaaS platform" --no-analyze-images

# With forms included
ccux gen --desc "Landing page" --include-forms
```

### `ccux multipage`
Generate intelligent multi-page website with parallel processing

**Options:**
- `--desc, -d TEXT`: Product description for multi-page website
- `--desc-file FILE`: Path to file containing product description (supports .txt and .pdf files)
- `--theme, -t THEME`: Design theme (default: minimal)
- `--base-url, -u URL`: Base URL for sitemap generation (default: https://example.com)
- `--output, -o DIR`: Output directory

**Key Features:**
- **Intelligent Analysis**: AI-powered page detection with confidence scoring
- **Interactive Selection**: Rich terminal interface for page selection
- **Parallel Generation**: Generate multiple pages simultaneously
- **Smart Navigation**: Automatic cross-page navigation and linking
- **SEO Optimization**: XML/HTML sitemaps and robots.txt generation
- **Error Handling**: Graceful failure recovery with retry options

**Examples:**
```bash
# Basic multi-page website
ccux multipage --desc "SaaS platform for remote teams"

# With custom theme and base URL
ccux multipage --desc "E-commerce platform" --theme morphism --base-url https://mystore.com

# From PDF description file
ccux multipage --desc-file product-description.pdf --theme brutalist

# Interactive mode (recommended)
ccux init
# Then select "Create Multi-Page Website" from the menu
```

**Three-Phase Process:**
1. **Analysis Phase**: AI analyzes description → Suggests pages → Interactive selection
2. **Generation Phase**: Parallel page generation → Real-time progress → Error handling
3. **Connection Phase**: Build navigation → Generate sitemaps → SEO optimization

### `ccux regen`
Regenerate specific sections of existing landing pages

**Options:**  
- `--section, -s TEXT`: Section(s) to regenerate (comma-separated)
- `--all`: Regenerate all sections
- `--desc, -d TEXT`: Product description (auto-detected if not provided)
- `--file, -f FILE`: Path to landing page file
- `--output, -o DIR`: Output directory

**Key Features:**
- **Precision Targeting**: Only regenerates specified sections
- **Smart Context**: Auto-detects product description from project metadata
- **Theme Preservation**: Maintains existing design consistency
- **Section Detection**: Automatically identifies available sections

**Examples:**
```bash
# Regenerate hero section only
ccux regen --section hero

# Regenerate multiple sections  
ccux regen --section hero,features,pricing

# Regenerate all sections
ccux regen --all

# Target specific file
ccux regen --section pricing --file custom/page.html
```

### `ccux help`
Comprehensive help system with specialized topics

**Usage:** `ccux help [TOPIC]`

**Topics:**
- `quickstart`: Step-by-step setup guide for new users
- `themes`: Complete theme guide with descriptions and use cases
- `examples`: Common usage patterns and practical scenarios  
- `workflows`: Step-by-step workflows for different user types

```bash
# General help
ccux help

# Specific topics
ccux help themes
ccux help quickstart
ccux help examples
ccux help workflows
```

### `ccux version`
Show version information and basic usage guidance

```bash
ccux version
```

---

## What You Get

### Professional Quality Output
- Production-ready HTML with TailwindCSS  
- Mobile-responsive design  
- SEO optimization and accessibility features  
- Clean, semantic code structure  

### AI Design Process
- Automatic competitor analysis and research  
- Structured UX methodology for layouts and flows  
- Conversion-optimized copywriting  
- Consistent visual design across 13 themes  

### 13 Professional Design Themes

**Core Themes:**
- **`minimal`** - Clean, content-focused design inspired by Dieter Rams principles
- **`brutalist`** - Raw, honest design with bold typography and stark contrasts
- **`playful`** - Joyful, approachable design with organic shapes and vibrant colors
- **`corporate`** - Traditional, trustworthy business design for professional services

**Modern Themes:**
- **`morphism`** - Soft, tactile design combining neumorphism and glassmorphism effects
- **`animated`** - Motion-first design where smooth animations drive the user experience
- **`terminal`** - Monospace, CLI-inspired aesthetic perfect for developer tools
- **`aesthetic`** - Retro-futuristic Y2K and vaporwave styling with gradient overlays

**Specialized Themes:**
- **`dark`** - Modern dark theme optimized for reduced eye strain and night viewing
- **`vibrant`** - Colorful, dopamine-rich design that energizes and engages users
- **`sustainable`** - Nature-inspired design with earth tones for eco-conscious brands
- **`data`** - Information-dense design optimized for dashboards and analytics platforms
- **`illustrated`** - Hand-drawn, custom illustration-driven design with artistic flair

Each theme includes carefully crafted color palettes, typography systems, spacing scales, and component styles that work seamlessly across all generated pages.  

---

## Examples

**Single Page:**
```bash
ccux gen --desc "AI-powered project management tool for remote teams"
```

**Multi-Page Website:**
```bash
ccux multipage --desc "SaaS platform with features, pricing, and about pages"
```

**Edit Existing:**
```bash
ccux regen --section hero,pricing
```

---

## View Your Pages

```bash
cd output/
python -m http.server 3000
# Open http://localhost:3000
```

---

## Links

- **PyPI:** [pypi.org/project/ccux](https://pypi.org/project/ccux/)  
- **Claude CLI:** [claude.ai/code](https://claude.ai/code)  
- **Help:** Run `ccux help` for detailed documentation  

---

Created by [Harsh Kumar](https://github.com/thisisharsh7)

