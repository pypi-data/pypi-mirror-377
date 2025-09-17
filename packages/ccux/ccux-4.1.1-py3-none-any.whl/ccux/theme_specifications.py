"""
Enhanced Theme System with Modern Design Theory
Comprehensive theme specifications for CCUI
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ThemeSpec:
    """Theme specification with design theory backing"""
    name: str
    description: str
    use_cases: List[str]
    target_audience: str
    design_philosophy: str
    visual_characteristics: Dict[str, Any]
    accessibility_priority: str
    implementation_notes: str

# Enhanced Theme System based on Modern Design Theory
THEME_SPECIFICATIONS = {
    "minimal": ThemeSpec(
        name="Minimal",
        description="Clean, content-focused design rooted in Dieter Rams' principles of clarity and function.",
        use_cases=[
            "B2B SaaS platforms",
            "Professional services",
            "Documentation sites",
            "Portfolio websites"
        ],
        target_audience="Efficiency-driven professionals who value clarity over decoration",
        design_philosophy="Less but better – eliminate non-essential elements, elevate hierarchy",
        visual_characteristics={
            "color_palette": "Neutral monochrome with restrained single accent",
            "typography": "System and modern sans-serif (Inter, SF Pro) for legibility",
            "spacing": "Generous whitespace, strict 8pt grid rhythm",
            "components": "Flat surfaces, hairline borders, subtle elevation (no skeuomorphism)",
            "interactions": "Micro-hover cues, restrained transitions (opacity/fade only)",
            "layout": "Grid-first, wide margins, plenty of negative space"
        },
        accessibility_priority="AAA target – strict readability and contrast across breakpoints",
        implementation_notes="Use fluid type scales, responsive whitespace, avoid decorative overload"
    ),

    "brutalist": ThemeSpec(
        name="Brutalist",
        description="Raw, bold design inspired by Brutalist architecture – uncompromising and experimental.",
        use_cases=[
            "Creative agencies",
            "Art portfolios",
            "Experimental products",
            "Bold brand statements"
        ],
        target_audience="Design-forward users seeking unconventional, striking aesthetics",
        design_philosophy="Raw materials, geometric intensity, deliberate visual discomfort",
        visual_characteristics={
            "color_palette": "High-contrast black/white with primary or neon accent",
            "typography": "Heavy sans-serif (Helvetica Bold, Arial Black)",
            "spacing": "Dense, overlapping, deliberate grid breaks",
            "components": "Hard edges, thick borders, no rounded corners",
            "interactions": "Abrupt state changes, instant feedback (no easing)",
            "layout": "Asymmetrical, overlapping blocks, raw visual stacking"
        },
        accessibility_priority="AA target – maintain legibility despite high-contrast extremes",
        implementation_notes="Use system fonts at heavy weights, avoid gradients, embrace harsh edges"
    ),

    "playful": ThemeSpec(
        name="Playful",
        description="Joyful, approachable design with vibrant colors and organic forms.",
        use_cases=[
            "Consumer apps",
            "Children's products",
            "Entertainment platforms",
            "Creative tools"
        ],
        target_audience="Consumers seeking delight, warmth, and engaging experiences",
        design_philosophy="Design should spark joy and emotional connection through whimsy",
        visual_characteristics={
            "color_palette": "Bright, saturated primaries with multi-color gradients",
            "typography": "Rounded sans (Circular, Nunito) with playful weight variations",
            "spacing": "Organic spacing, non-uniform padding",
            "components": "Rounded corners, gradient fills, soft shadows",
            "interactions": "Bouncy micro-animations, spring physics",
            "layout": "Fluid, circular and curved motifs"
        },
        accessibility_priority="AA target – careful management of bright color contrast",
        implementation_notes="Use CSS custom properties for color variations, implement spring-based motion"
    ),

    "corporate": ThemeSpec(
        name="Corporate",
        description="Trust-focused design using established business conventions and conservative styling.",
        use_cases=[
            "Financial services",
            "Healthcare",
            "Government",
            "Enterprise software"
        ],
        target_audience="Business professionals who require signals of reliability and authority",
        design_philosophy="Familiar patterns that convey competence, hierarchy, and trust",
        visual_characteristics={
            "color_palette": "Blue-dominant, conservative secondary palette",
            "typography": "Serif + sans pairings (Georgia, Arial)",
            "spacing": "Consistent grid, proportional margins",
            "components": "Conventional buttons, structured form layouts",
            "interactions": "Predictable, subtle transitions",
            "layout": "Formal hierarchy, left-to-right reading emphasis"
        },
        accessibility_priority="AA compliance minimum across corporate branding colors",
        implementation_notes="Follow established UI patterns, prioritize clarity over novelty"
    ),

    "morphism": ThemeSpec(
        name="Morphism",
        description="Soft, tactile UI blending neumorphism and glassmorphism principles.",
        use_cases=[
            "Mobile apps",
            "Design portfolios",
            "Premium products",
            "UI/UX showcases"
        ],
        target_audience="Design enthusiasts and premium product users",
        design_philosophy="Digital tactility – UI elements that appear touchable and layered",
        visual_characteristics={
            "color_palette": "Muted pastels with depth gradients",
            "typography": "Rounded sans (SF Pro, Poppins)",
            "spacing": "Generous padding for tactile touch targets",
            "components": "Inset/outset shadows, frosted glass backgrounds",
            "interactions": "Depth-shift on press, soft scaling",
            "layout": "Layered elements floating in depth"
        },
        accessibility_priority="AA target – ensure glass overlays maintain readable contrast",
        implementation_notes="Use multi-layer box-shadows, CSS backdrop-filter, avoid overuse of blur"
    ),

    "animated": ThemeSpec(
        name="Animated",
        description="Motion-first design where animation drives narrative and engagement.",
        use_cases=[
            "Interactive storytelling",
            "Product launches",
            "Creative portfolios",
            "Brand experiences"
        ],
        target_audience="Users seeking immersive, dynamic digital experiences",
        design_philosophy="Motion as primary design material – guiding attention and storytelling",
        visual_characteristics={
            "color_palette": "Dynamic, adaptive colors shifting with user input",
            "typography": "Variable and web fonts optimized for motion",
            "spacing": "Fluid spacing responsive to animations",
            "components": "Transformable, stateful UI blocks",
            "interactions": "Scroll-triggered scenes, choreographed transitions",
            "layout": "Scene-based transformations instead of static layouts"
        },
        accessibility_priority="AA target – respect prefers-reduced-motion for accessibility",
        implementation_notes="Use CSS/JS motion frameworks, optimize for GPU performance, support motion toggles"
    ),

    "terminal": ThemeSpec(
        name="Terminal",
        description="CLI-inspired design with monospace typography and retro computing aesthetics.",
        use_cases=[
            "Developer tools",
            "Technical documentation",
            "API platforms",
            "Hacker/security tools"
        ],
        target_audience="Developers, sysadmins, and tech-savvy audiences",
        design_philosophy="Lean into the nostalgia and efficiency of terminal interfaces",
        visual_characteristics={
            "color_palette": "Dark background with neon green/amber text",
            "typography": "Strict monospace (Fira Code, JetBrains Mono)",
            "spacing": "Character-grid spacing (ch units)",
            "components": "ASCII-art, code block metaphors",
            "interactions": "Typewriter effects, blinking cursors",
            "layout": "Terminal-window inspired fixed-width layouts"
        },
        accessibility_priority="High-contrast defaults, screen reader-friendly semantics",
        implementation_notes="Use CSS ch units for grid, typewriter animations, support ASCII visuals"
    ),

    "aesthetic": ThemeSpec(
        name="Aesthetic",
        description="Retro-futuristic design blending Y2K, vaporwave, and cyber nostalgia with modern UX.",
        use_cases=[
            "Creative platforms",
            "Music & entertainment",
            "Fashion brands",
            "Art communities"
        ],
        target_audience="Gen Z and millennials drawn to digital nostalgia and cyberculture",
        design_philosophy="Reinterpret nostalgic aesthetics with usability-focused design",
        visual_characteristics={
            "color_palette": "Dark navy/black with neon accents (cyan, magenta, electric blue)",
            "typography": "Retro-inspired but legible fonts (bold sans with neon glow)",
            "spacing": "Structured grid softened with retro visuals",
            "components": "Outlined neon UI, glowing buttons",
            "interactions": "Subtle neon glows, hover pulses",
            "layout": "Dark theme with vibrant accent-driven hierarchy"
        },
        accessibility_priority="AA target – maintain 4.5:1 contrast despite neon styling",
        implementation_notes="Always test neon contrasts on dark, ensure glow effects never replace contrast"
    ),

    "dark": ThemeSpec(
        name="Dark",
        description="Modern dark theme optimized for reduced eye strain and immersive focus.",
        use_cases=[
            "Developer tools",
            "Creative portfolios",
            "Entertainment platforms",
            "Productivity apps"
        ],
        target_audience="Night users, developers, gamers, and professionals",
        design_philosophy="Focus attention on content by minimizing luminance and maximizing contrast",
        visual_characteristics={
            "color_palette": "Deep grays/blacks with sharp accent colors (teal, purple, green)",
            "typography": "Readable sans (Inter, Roboto)",
            "spacing": "Balanced negative space for readability on dark",
            "components": "High-contrast CTAs, glowing outlines, subtle shadows",
            "interactions": "Smooth fades, glow hover states",
            "layout": "Content-forward with accent highlights"
        },
        accessibility_priority="AA target – maintain 4.5:1 contrast minimum",
        implementation_notes="Avoid mid-gray on dark, validate all text/background ratios"
    ),

    "vibrant": ThemeSpec(
        name="Vibrant",
        description="High-energy theme using bold colors and gradients to energize interactions.",
        use_cases=[
            "Marketing websites",
            "Consumer products",
            "Music apps",
            "Startups"
        ],
        target_audience="Younger, casual users who seek stimulation and excitement",
        design_philosophy="Color as emotion – bold hues designed to energize and engage",
        visual_characteristics={
            "color_palette": "Dopamine-rich gradients (purple-pink, orange-teal)",
            "typography": "Expressive, bold sans (Montserrat, Gilroy)",
            "spacing": "Dynamic asymmetry with active negative space",
            "components": "Gradient-filled CTAs, shadow pops",
            "interactions": "Gradient shifts, hover glows, micro-transitions",
            "layout": "Hero-first design with strong CTA emphasis"
        },
        accessibility_priority="AA target – ensure text legibility over bright backgrounds",
        implementation_notes="Validate gradient legibility, avoid oversaturation, layer dark overlays when needed"
    ),

    "sustainable": ThemeSpec(
        name="Sustainable",
        description="Nature-inspired design using earth tones and calm layouts for eco-conscious branding.",
        use_cases=[
            "Environmental organizations",
            "Eco-products",
            "Sustainable brands",
            "Wellness platforms"
        ],
        target_audience="Eco-conscious consumers and brands prioritizing sustainability",
        design_philosophy="Calm, grounded design that reflects environmental values",
        visual_characteristics={
            "color_palette": "Greens, browns, and muted naturals",
            "typography": "Organic, humanist fonts (Lora, Poppins)",
            "spacing": "Generous whitespace for light, airy feel",
            "components": "Soft corners, textures, nature-inspired motifs",
            "interactions": "Smooth fades, natural flow animations",
            "layout": "Grounded grid with breathing room"
        },
        accessibility_priority="AA target – ensure muted colors still pass contrast",
        implementation_notes="Avoid neon greens, prioritize muted natural palettes, always test color contrast"
    ),

    "data": ThemeSpec(
        name="Data",
        description="Dense, information-rich theme designed for analytics and dashboards.",
        use_cases=[
            "Analytics dashboards",
            "Finance apps",
            "Enterprise SaaS",
            "Developer tools"
        ],
        target_audience="Analysts, engineers, and decision-makers who need clarity at scale",
        design_philosophy="Clarity and efficiency in communicating large datasets",
        visual_characteristics={
            "color_palette": "Neutral grays with strong accent colors for charts",
            "typography": "Readable sans (Roboto, IBM Plex Sans)",
            "spacing": "Tight, grid-aligned spacing for density",
            "components": "Tables, charts, modular cards",
            "interactions": "Hover tooltips, interactive filters, smooth sorting",
            "layout": "Modular grid optimized for scanning data"
        },
        accessibility_priority="AAA target – clarity and colorblind-safe palette",
        implementation_notes="Validate chart colorblind safety, provide text equivalents for visualizations"
    ),

    "illustrated": ThemeSpec(
        name="Illustrated",
        description="Hand-drawn, character-driven design that emphasizes warmth and personality.",
        use_cases=[
            "Creative startups",
            "Onboarding flows",
            "Educational platforms",
            "Community websites"
        ],
        target_audience="Students, casual users, and creative professionals",
        design_philosophy="Humanize digital experiences with illustration as storytelling",
        visual_characteristics={
            "color_palette": "Soft pastels with vibrant accent pops",
            "typography": "Rounded, friendly fonts (Nunito, Quicksand)",
            "spacing": "Organic spacing around illustrations",
            "components": "Illustration-driven CTAs, custom iconography",
            "interactions": "Playful onboarding animations, micro-delight",
            "layout": "Centered, narrative-driven structures"
        },
        accessibility_priority="AA target – do not rely solely on illustration for meaning",
        implementation_notes="Use lightweight SVGs, consider Lottie for animated illustrations"
    ),

    # Additional DaisyUI-inspired themes

    "light": ThemeSpec(
        name="Light",
        description="Clean, neutral theme with bright background — classic baseline for content-first UI.",
        use_cases=["General websites", "Blogs & documentation", "Dashboards with light backgrounds", "Corporate landing pages"],
        target_audience="Users who prefer bright, minimal interfaces and high readability",
        design_philosophy="Clarity, simplicity, high contrast on light backgrounds",
        visual_characteristics={
            "color_palette": "Whites, light grays, neutral tones, subdued accent",
            "typography": "Dark text on light background, clean sans fonts",
            "spacing": "Moderate padding/margins for clarity",
            "components": "Light-borders, minimal shadows, flat feel",
            "interactions": "Subtle hover/focus effects",
            "layout": "Open spaces, strong clarity of content"
        },
        accessibility_priority="High contrast for text, good visibility on bright background",
        implementation_notes="Often used as default; ensure accent colors readable over base-100"
    ),

    "cupcake": ThemeSpec(
        name="Cupcake",
        description="Soft, pastel-forward theme with a warm, friendly tone and gentle contrasts.",
        use_cases=["Personal blogs", "Casual e-commerce", "Children or hobby sites", "Friendly brand pages"],
        target_audience="Audiences seeking approachable, soft visuals",
        design_philosophy="Use pastels and gentle shapes to create approachability and calm",
        visual_characteristics={
            "color_palette": "Light cream bases with pastel pinks, blues, and mint accents",
            "typography": "Rounded and legible sans; moderate weights",
            "spacing": "Comfortable whitespace with soft padding",
            "components": "Rounded corners, subtle shadows, soft borders",
            "interactions": "Gentle hover states, fade transitions",
            "layout": "Airy, non-dense layout to emphasize friendliness"
        },
        accessibility_priority="AA target — ensure pastels are legible for text and UI elements",
        implementation_notes="Use darker text anchors to preserve legibility over pastel backgrounds"
    ),

    "bumblebee": ThemeSpec(
        name="Bumblebee",
        description="Warm, energetic palette inspired by honey and sunshine — bold and optimistic.",
        use_cases=["Event pages", "Food & beverage", "Youth brands", "Seasonal promos"],
        target_audience="Brands seeking high-energy, cheerful visuals",
        design_philosophy="Convey warmth and optimism via saturated yellow/orange accents with stabilizing neutrals",
        visual_characteristics={
            "color_palette": "Warm yellows, soft creams, muted browns and dark accent colors",
            "typography": "Readable sans with friendly tones",
            "spacing": "Balanced spacing to avoid overwhelming brightness",
            "components": "Bright CTAs, warm panels, subtle rounded shapes",
            "interactions": "Hover brighten, gentle elevation",
            "layout": "Inviting layout with focal CTAs"
        },
        accessibility_priority="AA target — be cautious with yellow on white backgrounds",
        implementation_notes="Pair bright yellows with darker text anchors and outlines for clarity"
    ),

    "emerald": ThemeSpec(
        name="Emerald",
        description="Fresh green-forward theme evoking growth, health, and sustainability.",
        use_cases=["Wellness brands", "Sustainable products", "Health apps", "Eco-focused websites"],
        target_audience="Audiences that value natural, calming aesthetics",
        design_philosophy="Use green accents to communicate health, calm, and forward motion",
        visual_characteristics={
            "color_palette": "Emerald greens, muted neutrals, possible earth tone complements",
            "typography": "Neutral sans for clarity",
            "spacing": "Generous margins to let green accents breathe",
            "components": "Green primary buttons, subtle rounded cards, light shadows",
            "interactions": "Soft color shifts on hover emphasizing green tones",
            "layout": "Balanced layouts with imagery to support the green motif"
        },
        accessibility_priority="AA target — ensure green contrasts on both light and dark bases",
        implementation_notes="Reserve high-saturation greens for accents not body text"
    ),

    "synthwave": ThemeSpec(
        name="Synthwave",
        description="Neon-glow retro-futuristic palette inspired by 80s synth aesthetics — bold and dramatic.",
        use_cases=["Music/media sites", "Gaming landing pages", "Retro branding", "Promotional microsites"],
        target_audience="Users seeking stylized, nostalgic, high-energy visuals",
        design_philosophy="Combine deep dark bases with vivid neon accents for dramatic contrast",
        visual_characteristics={
            "color_palette": "Deep purples and indigos with neon pinks, cyans and electric blues",
            "typography": "Display or geometric fonts for headings; clear sans for body",
            "spacing": "Moderate spacing allowing glow effects to show",
            "components": "Glowing borders, neon outlines, backlit CTAs",
            "interactions": "Glow/pulse hover states, color shifts",
            "layout": "Dark-first layout with neon highlights and visual drama"
        },
        accessibility_priority="AA target — ensure text over neon glows remains readable",
        implementation_notes="Use CSS variables for glow color and limit blur radii for legibility"
    ),

    "retro": ThemeSpec(
        name="Retro",
        description="Muted, nostalgic palettes with vintage vibes — softened tones and analogue warmth.",
        use_cases=["Vintage brands", "Music/art sites", "Lifestyle blogs", "Nostalgic campaigns"],
        target_audience="Audiences that appreciate throwback aesthetics and softer palettes",
        design_philosophy="Embrace slightly desaturated colors and retro typography cues for nostalgia",
        visual_characteristics={
            "color_palette": "Washed pastels, warm browns, muted greens and oranges",
            "typography": "Serif or slab accents mixed with clean body text",
            "spacing": "Generous spacing and intentional texture",
            "components": "Soft borders, small textures, aged-style overlays optional",
            "interactions": "Gentle fades, soft movement mimicking analogue media",
            "layout": "Centered content and visual storytelling elements"
        },
        accessibility_priority="AA target — ensure desaturated text remains legible",
        implementation_notes="Add optional subtle textures via SVG or background images for authenticity"
    ),

    "cyberpunk": ThemeSpec(
        name="Cyberpunk",
        description="High-contrast, neon-laden futuristic palette — edgy and energetic.",
        use_cases=["Tech startups", "Gaming UI", "Sci-fi experiences", "Event pages"],
        target_audience="Users drawn to dramatic, futuristic, and gritty visuals",
        design_philosophy="Mix dark city-night bases with bright neon accents for a tech-noir feel",
        visual_characteristics={
            "color_palette": "Near-black bases with cyan, magenta, neon purple accents",
            "typography": "Bold sans for headlines, monospaced for tech flavor optionally",
            "spacing": "Compact to moderate; leave room for glowing accents",
            "components": "Outlined neon buttons, high-contrast cards, glassy panels",
            "interactions": "Flicker, neon outlines on hover, vivid color pops",
            "layout": "Layered, depth with glow effects and strong visual hierarchy"
        },
        accessibility_priority="AA target — test neon on dark for readability; provide alternatives",
        implementation_notes="Avoid excessive blur; keep text outside heavy glow masks"
    ),

    "valentine": ThemeSpec(
        name="Valentine",
        description="Romantic pink/red palette that feels warm, intimate and emotive.",
        use_cases=["Seasonal/holiday pages", "Wedding sites", "Greeting cards", "Romantic product pages"],
        target_audience="Users and brands seeking romantic and personal tones",
        design_philosophy="Emphasize warmth, softness and approachable charm via pink/red hues",
        visual_characteristics={
            "color_palette": "Pinks, soft reds, cream neutrals",
            "typography": "Friendly serif or rounded display for headings, clear body text",
            "spacing": "Comfortable white space and centered compositions",
            "components": "Rounded buttons, soft gradients, heart or floral motifs optional",
            "interactions": "Subtle scale/fade micro-interactions, gentle glows",
            "layout": "Centered, emotive compositions with imagery"
        },
        accessibility_priority="AA target — ensure red/pink contrasts with text and background",
        implementation_notes="Avoid overly saturated pink for body text; reserve for accents"
    ),

    "halloween": ThemeSpec(
        name="Halloween",
        description="Seasonal spooky palette with dark purples, oranges and moody accents.",
        use_cases=["Holiday microsites", "Event pages", "Entertainment promotions", "Seasonal shops"],
        target_audience="Brands seeking playful spooky visuals for seasonal marketing",
        design_philosophy="Use thematic color cues and motifs to create a festive mood",
        visual_characteristics={
            "color_palette": "Dark purples/indigos, orange, black and muted browns",
            "typography": "Playful or display headings with clear body text",
            "spacing": "Moderate; allow motif placement and imagery",
            "components": "Themed icons, accent borders, decorative patterns optional",
            "interactions": "Hover glows, subtle flicker or pulse effects",
            "layout": "Dramatic, imagery-forward with thematic accents"
        },
        accessibility_priority="AA target — ensure contrast against dark backgrounds",
        implementation_notes="Use seasonal imagery and ensure accessibility for assistive tech"
    ),

    "garden": ThemeSpec(
        name="Garden",
        description="Lush botanical palette focused on greens and floral accents for a natural feeling.",
        use_cases=["Gardening businesses", "Eco-lifestyle brands", "Wellness sites", "Landscape portfolios"],
        target_audience="Nature-focused audiences and brands",
        design_philosophy="Bring serenity and freshness through foliage-inspired color choices",
        visual_characteristics={
            "color_palette": "Leaf greens, soft florals, warm neutrals",
            "typography": "Clean sans with friendly accents",
            "spacing": "Generous spacing for imagery and breathing room",
            "components": "Soft-edged cards, botanical iconography, image-focused panels",
            "interactions": "Subtle color changes and gentle reveals",
            "layout": "Image-led layouts with plentiful whitespace"
        },
        accessibility_priority="AA target — verify green contrast and readability",
        implementation_notes="Pair greens with neutral text and consider textured backgrounds"
    ),

    "forest": ThemeSpec(
        name="Forest",
        description="Deep, grounded greens and earthy tones for a moody, organic aesthetic.",
        use_cases=["Outdoor brands", "Craft/handmade stores", "Eco tours", "Premium natural products"],
        target_audience="Users who prefer rich, natural visual language",
        design_philosophy="Use depth and earthy accents to create a sense of rootedness",
        visual_characteristics={
            "color_palette": "Deep forest greens, rich browns, dark neutrals",
            "typography": "Readable sans with slightly warm tones",
            "spacing": "Balanced spacing with tighter content clusters for mood",
            "components": "Dark panels, natural textures, grounded imagery",
            "interactions": "Soft lightening on hover, gentle reveals",
            "layout": "Immersive, photography-forward where appropriate"
        },
        accessibility_priority="AA target — ensure text contrast on dark green backgrounds",
        implementation_notes="Use lighter text anchors and avoid mid-tone greens for copy"
    ),

    "aqua": ThemeSpec(
        name="Aqua",
        description="Cool cyan and teal palette evoking water, clarity and freshness.",
        use_cases=["Spa & wellness", "Marine brands", "Travel sites", "Health products"],
        target_audience="Audiences seeking calm, clean, refreshing visual language",
        design_philosophy="Use cool hues to communicate cleanliness, clarity and relaxation",
        visual_characteristics={
            "color_palette": "Cyan, teal, light blues, crisp neutrals",
            "typography": "Neutral sans, crisp headings",
            "spacing": "Airy spacing and clean panels",
            "components": "Light panels with aqua accents, clean buttons",
            "interactions": "Smooth transitions, slight lift on hover",
            "layout": "Open, calm layout with focus on imagery or whitespace"
        },
        accessibility_priority="AA target — ensure cyan contrasts on chosen bases",
        implementation_notes="Use darker text anchors on light aqua backgrounds for readability"
    ),

    "lofi": ThemeSpec(
        name="Lofi",
        description="Muted, relaxed palette with low saturation for calm, contemplative interfaces.",
        use_cases=["Personal journals", "Music blogs", "Relaxed brand sites", "Memoir or writing platforms"],
        target_audience="Users who prefer understated visuals and low stimulation",
        design_philosophy="Desaturate and soften elements to focus on content and calm",
        visual_characteristics={
            "color_palette": "Muted neutrals, soft pastels, low saturation tones",
            "typography": "Comfortable readable fonts with warm weights",
            "spacing": "Generous whitespace to reduce visual density",
            "components": "Flat cards, subtle borders, minimal decoration",
            "interactions": "Slow, gentle transitions or no animation",
            "layout": "Simple, centered layouts that promote reading"
        },
        accessibility_priority="AA target — ensure text contrast despite muted tones",
        implementation_notes="Provide alternate higher-contrast variants if necessary"
    ),

    "pastel": ThemeSpec(
        name="Pastel",
        description="Very soft, delicate color palette using pastel hues for gentle, airy UIs.",
        use_cases=["Children's products", "Design showcases", "Lifestyle blogs", "Wedding sites"],
        target_audience="Audiences who appreciate softness and a light mood",
        design_philosophy="Employ pastel hues with restrained contrast to create a serene tone",
        visual_characteristics={
            "color_palette": "Mint greens, baby blues, soft pinks and creams",
            "typography": "Light and airy sans; readable weights for body text",
            "spacing": "Airy spacing and rounded elements",
            "components": "Rounded cards, subtle gradients, soft shadows",
            "interactions": "Gentle fades and micro-interactions",
            "layout": "Open layout with plentiful whitespace for breathing room"
        },
        accessibility_priority="AA target — pay attention to pastel contrast for text",
        implementation_notes="Consider darker copy colors and overlays on top of pastels"
    ),

    "fantasy": ThemeSpec(
        name="Fantasy",
        description="Playful, magical palette mixing rich jewel tones with whimsical accents.",
        use_cases=["Gaming sites", "Children's entertainment", "Creative storytelling", "Imaginative brands"],
        target_audience="Fans of whimsical, ornate and narrative-driven visuals",
        design_philosophy="Blend rich color with decorative touches to evoke wonder",
        visual_characteristics={
            "color_palette": "Jewel tones: deep purples, teals, gold accents",
            "typography": "Decorative display fonts for headings, legible body fonts",
            "spacing": "Flexible spacing to accommodate illustrative elements",
            "components": "Ornamental borders, illustrative CTAs, themed icons",
            "interactions": "Color-shifts, reveal animations, parallax hints",
            "layout": "Narrative-driven layouts with illustration focus"
        },
        accessibility_priority="AA target — ensure ornamentation doesn't obscure content",
        implementation_notes="Use illustrations as progressive enhancement; always include text alternatives"
    ),

    "wireframe": ThemeSpec(
        name="Wireframe",
        description="Blueprint-like, skeletal styles suited for low-fidelity prototyping and structure-first layouts.",
        use_cases=["Prototyping", "Design reviews", "Education", "Early-stage product demos"],
        target_audience="Designers and developers needing quick structural mockups",
        design_philosophy="Strip styling to emphasize layout and hierarchy over finish",
        visual_characteristics={
            "color_palette": "Neutral outlines, light grays, minimal fills",
            "typography": "System fonts or neutral sans for clarity",
            "spacing": "Clear spacing that highlights structure",
            "components": "Outlined cards, placeholder shapes, minimalistic controls",
            "interactions": "Very subtle, mostly static to show structure",
            "layout": "Grid and flow-focused layouts to communicate hierarchy"
        },
        accessibility_priority="AA target — keep controls clear and keyboard navigable",
        implementation_notes="Great for sharing structure with non-technical stakeholders"
    ),

    "black": ThemeSpec(
        name="Black",
        description="True-black first theme for maximum contrast and dramatic visuals.",
        use_cases=["Luxury brands", "Media portals", "Dark-first portfolios", "Consoles and kiosks"],
        target_audience="Users wanting strong drama, contrast and spotlighted content",
        design_philosophy="Leverage pure black to make color accents and imagery pop",
        visual_characteristics={
            "color_palette": "#000 or near-black bases with vivid accent colors",
            "typography": "Bright, readable sans or serif choices for headings/body",
            "spacing": "Spacious layouts to counteract intensity of black",
            "components": "Minimal shadows, stark outlines, high-contrast CTAs",
            "interactions": "Bold hover states, illuminated accents",
            "layout": "Immersive content-first layouts with spotlighting"
        },
        accessibility_priority="High — ensure all text is highly legible against true black",
        implementation_notes="Consider OLED implications and ensure blacks are handled consistently"
    ),

    "luxury": ThemeSpec(
        name="Luxury",
        description="Upscale palette with rich dark bases and metallic/gold accents for premium feel.",
        use_cases=["High-end retail", "Jewelry", "Luxury hospitality", "Premium service landing pages"],
        target_audience="Brands that want to project sophistication and exclusivity",
        design_philosophy="Subtle ornament, restrained palette, and high-quality imagery to convey luxury",
        visual_characteristics={
            "color_palette": "Deep charcoals or blacks with gold, cream or deep burgundy accents",
            "typography": "Elegant serif or display fonts for headings; refined body text",
            "spacing": "Generous negative space and carefully considered proportions",
            "components": "Fine borders, understated textures, tasteful gloss/shadow",
            "interactions": "Subtle sheen/hover transitions and gentle reveals",
            "layout": "Centered, curated layouts with premium imagery"
        },
        accessibility_priority="AA target — ensure metallic accents don't hinder legibility",
        implementation_notes="Use metallic effects sparingly and test on varied screens"
    ),

    "dracula": ThemeSpec(
        name="Dracula",
        description="Dark theme with purples and pink accents; moody yet developer-friendly aesthetics.",
        use_cases=["Code editors", "Developer tools", "Dark mode apps", "Themed dashboards"],
        target_audience="Developers and users who like dramatic dark palettes with colorful accents",
        design_philosophy="Balance dark neutrals with bright, saturated accent colors for clarity",
        visual_characteristics={
            "color_palette": "Deep purples, pinks, cyan accents with light text",
            "typography": "Monospace for code snippets; clean sans for UI",
            "spacing": "Functional spacing tuned for reading and code density",
            "components": "High-contrast panels, colored badges, accent outlines",
            "interactions": "Accent reveals on hover, subtle glows",
            "layout": "Content-first, optimized for focus and developer workflows"
        },
        accessibility_priority="AA target — ensure neon-like accents don't reduce readability",
        implementation_notes="Good fit for code-centric UIs; avoid excessive glow blur"
    ),

    "cmyk": ThemeSpec(
        name="CMYK",
        description="Bold print-inspired palette using primary print colors for a graphic, loud feel.",
        use_cases=["Creative agencies", "Print/design portfolios", "Poster-style landing pages"],
        target_audience="Design-forward users who favor strong graphic statements",
        design_philosophy="Use high-saturation primaries with bold layout decisions for impact",
        visual_characteristics={
            "color_palette": "Cyan, Magenta, Yellow (and Black) with supporting neutrals",
            "typography": "Bold display headings and readable body fonts",
            "spacing": "Tight and punchy to emphasize blocks of color",
            "components": "Blocky panels, sharp edges, bold CTA treatments",
            "interactions": "Color shifts and stark hover contrasts",
            "layout": "Poster-like sections and strong hero statements"
        },
        accessibility_priority="AA target — watch text contrast on vivid backgrounds",
        implementation_notes="Use neutral buffers around strong color blocks to avoid visual fatigue"
    ),

    "autumn": ThemeSpec(
        name="Autumn",
        description="Warm, rustic palette capturing the colours and coziness of fall.",
        use_cases=["Seasonal campaigns", "Food & craft brands", "Lifestyle blogs", "Rustic product pages"],
        target_audience="Users seeking warmth, nostalgia and seasonal charm",
        design_philosophy="Celebrate warm earthy tones and tactile visual elements",
        visual_characteristics={
            "color_palette": "Burnt oranges, deep reds, mustard yellows, warm browns",
            "typography": "Warm, readable serif or sans pairings",
            "spacing": "Comfortable padding and cozy layout proportions",
            "components": "Textured backgrounds optional, warm CTAs, rounded cards",
            "interactions": "Soft fades, warm hover color changes",
            "layout": "Inviting, narrative-driven layout with imagery"
        },
        accessibility_priority="AA target — ensure darker tones contrast sufficiently",
        implementation_notes="Use imagery and texture to emphasise seasonal storytelling"
    ),

    "business": ThemeSpec(
        name="Business",
        description="Neutral, polished palette built for professional, conservative uses.",
        use_cases=["Consulting firms", "Corporate portfolios", "B2B SaaS", "Professional services"],
        target_audience="Professionals and enterprises looking for restrained styling",
        design_philosophy="Prioritize clarity, predictable interactions, and conservative visual language",
        visual_characteristics={
            "color_palette": "Greys, steel blues, muted accents",
            "typography": "Neutral sans for body, optional serif in headings",
            "spacing": "Tight to moderate, consistent rhythm",
            "components": "Structured forms, clean tables, subdued CTAs",
            "interactions": "Predictable micro-interactions, minimal animation",
            "layout": "Grid-first, content-focused layouts"
        },
        accessibility_priority="AA target — consistent contrast and focus management",
        implementation_notes="Keep decorative touches minimal and maintain brand consistency"
    ),

    "acid": ThemeSpec(
        name="Acid",
        description="High-energy, almost fluorescent palette with electric contrast for standout visuals.",
        use_cases=["Edgy fashion", "Experimental art sites", "Music visuals", "Bold brand statements"],
        target_audience="Audiences who want shock, vibrancy, and maximal expression",
        design_philosophy="Push saturation and contrast for visual impact; use sparingly for emphasis",
        visual_characteristics={
            "color_palette": "Fluorescent greens, hot pinks, stark blacks and whites",
            "typography": "Bold, condensed display fonts for headings",
            "spacing": "Tight, punchy spacing to match loud visuals",
            "components": "High-contrast CTAs, stark outline buttons, bold cards",
            "interactions": "Sharp transitions, immediate color flips on hover",
            "layout": "Attention-first layouts with strong focal points"
        },
        accessibility_priority="AA target — ensure legibility; provide toned-down alternatives",
        implementation_notes="Avoid using across entire UI — reserve for accents and campaign content"
    ),

    "lemonade": ThemeSpec(
        name="Lemonade",
        description="Bright, citrusy palette with playful summer vibes and friendly contrast.",
        use_cases=["Food & drink", "Seasonal promos", "Kid-friendly brands", "Fresh startups"],
        target_audience="Brands wanting a cheerful and approachable tone",
        design_philosophy="Use vibrant yellows and light neutrals to convey freshness and approachability",
        visual_characteristics={
            "color_palette": "Sunny yellows, soft whites, coral or peach accents",
            "typography": "Light and friendly sans fonts",
            "spacing": "Airy spacing to prevent visual fatigue",
            "components": "Bright CTA buttons, light cards, minimal shadows",
            "interactions": "Hover brighten, subtle pop scales",
            "layout": "Playful but functional layouts with strong CTAs"
        },
        accessibility_priority="AA target — be careful with yellow contrast on white",
        implementation_notes="Use dark anchors for text and outlines for readability"
    ),

    "night": ThemeSpec(
        name="Night",
        description="Soft dark theme leaning toward deep blues and comfortable reading at night.",
        use_cases=["Reading apps", "Night mode UIs", "Blogs and portfolios used in low light"],
        target_audience="Users who prefer gentle dark themes rather than pure black",
        design_philosophy="Reduce glare while maintaining warmth and readability",
        visual_characteristics={
            "color_palette": "Deep navy/indigo, soft warm accents, gentle neutrals",
            "typography": "Readable sans with relaxed letterforms",
            "spacing": "Balanced spacing for comfortable reading",
            "components": "Soft panels, muted shadows, subtle highlights",
            "interactions": "Smooth fades and low-intensity glows",
            "layout": "Comfort-first layout for long-form reading"
        },
        accessibility_priority="AA target — ensure text contrast while keeping soft tones",
        implementation_notes="Use warm highlights sparingly and prefer higher contrast for body text"
    ),

    "coffee": ThemeSpec(
        name="Coffee",
        description="Warm, earthy tones inspired by coffeehouse culture and coziness.",
        use_cases=[
            "Cafés and restaurants",
            "Lifestyle brands",
            "Content blogs",
            "Wellness platforms"
        ],
        target_audience="Users seeking comfort and organic aesthetics",
        design_philosophy="Natural warmth through earthy palettes and textures",
        visual_characteristics={
            "color_palette": "Browns, creams, muted oranges",
            "typography": "Serif or humanist sans",
            "spacing": "Medium spacing with grounded rhythm",
            "components": "Rounded with soft textures",
            "interactions": "Gentle fades, smooth hover states",
            "layout": "Content-centric with cozy atmosphere"
        },
        accessibility_priority="AA target – confirm contrast across earthy tones",
        implementation_notes="Pair dark coffee browns with light cream backgrounds"
    ),

    "winter": ThemeSpec(
        name="Winter",
        description="Crisp, cool design evoking snowy landscapes and clean minimalism.",
        use_cases=[
            "Seasonal campaigns",
            "Travel websites",
            "Retail promotions",
            "Portfolio sites"
        ],
        target_audience="Users drawn to clean, refreshing digital aesthetics",
        design_philosophy="Use icy palettes to convey clarity and calm",
        visual_characteristics={
            "color_palette": "Whites, pale blues, silver grays",
            "typography": "Thin sans-serif, modern feel",
            "spacing": "Wide whitespace, airy spacing",
            "components": "Frosted backgrounds, subtle shadows",
            "interactions": "Gentle fades, smooth reveals",
            "layout": "Minimal grid with cold tone hierarchy"
        },
        accessibility_priority="AA target – ensure pale blues maintain sufficient contrast",
        implementation_notes="Avoid overly low-contrast whites on light blues"
    ),

    "dim": ThemeSpec(
        name="Dim",
        description="Low-contrast, muted dark theme for soft night-time readability.",
        use_cases=[
            "Reader apps",
            "Low-light productivity",
            "News sites",
            "Documentation"
        ],
        target_audience="Users who prefer muted visuals to reduce eye fatigue",
        design_philosophy="Soften the dark theme experience with dimmed contrasts",
        visual_characteristics={
            "color_palette": "Dark grays with muted accent tones",
            "typography": "Readable sans, moderate contrast",
            "spacing": "Comfortable line spacing for reading",
            "components": "Minimal shadows, subdued CTAs",
            "interactions": "Gentle hover highlights, opacity shifts",
            "layout": "Text-centric, distraction-free"
        },
        accessibility_priority="AA target – confirm muted accents remain legible",
        implementation_notes="Always verify readability with dim backgrounds"
    ),

    "nord": ThemeSpec(
        name="Nord",
        description="Nordic-inspired cool theme with calm, desaturated palettes.",
        use_cases=[
            "Developer tools",
            "Productivity apps",
            "Documentation",
            "Design systems"
        ],
        target_audience="Professionals who prefer calm, functional interfaces",
        design_philosophy="Reduce visual noise with balanced cool tones",
        visual_characteristics={
            "color_palette": "Cool blues, slate grays, ice tones",
            "typography": "Geometric sans (Inter, IBM Plex Sans)",
            "spacing": "Consistent modular spacing",
            "components": "Flat buttons, minimal borders",
            "interactions": "Fade and opacity transitions",
            "layout": "Grid-aligned, strict hierarchy"
        },
        accessibility_priority="AAA target – clarity across muted blues and grays",
        implementation_notes="Test all cool grays for readability against backgrounds"
    ),

    "sunset": ThemeSpec(
        name="Sunset",
        description="Vibrant gradient-driven theme inspired by warm sunsets.",
        use_cases=[
            "Marketing campaigns",
            "Landing pages",
            "Creative portfolios",
            "Lifestyle brands"
        ],
        target_audience="Younger, casual users drawn to vibrant visuals",
        design_philosophy="Infuse warmth and emotion through gradient storytelling",
        visual_characteristics={
            "color_palette": "Oranges, pinks, purples in gradient transitions",
            "typography": "Expressive sans, bold weights",
            "spacing": "Dynamic spacing for hero-first design",
            "components": "Gradient CTAs, strong imagery",
            "interactions": "Gradient shifts, smooth fades",
            "layout": "Hero-focused, narrative-driven"
        },
        accessibility_priority="AA target – ensure gradient backgrounds preserve text contrast",
        implementation_notes="Overlay dark gradients behind text when needed"
    ),

    "caramellatte": ThemeSpec(
        name="Caramellatte",
        description="Warm, latte-inspired tones blending caramel hues with cozy design.",
        use_cases=[
            "Coffee brands",
            "Lifestyle ecommerce",
            "Food products",
            "Wellness apps"
        ],
        target_audience="Users who enjoy warm, cozy aesthetics",
        design_philosophy="Blend caramel warmth with modern minimalism",
        visual_characteristics={
            "color_palette": "Caramel browns, latte creams, soft whites",
            "typography": "Rounded sans, smooth edges",
            "spacing": "Medium spacing with generous margins",
            "components": "Rounded buttons, cream surfaces",
            "interactions": "Soft fades, hover warm glows",
            "layout": "Centered, warm brand emphasis"
        },
        accessibility_priority="AA target – validate brown contrasts with text",
        implementation_notes="Balance darker caramel tones with light cream surfaces"
    ),

    "abyss": ThemeSpec(
        name="Abyss",
        description="Dark, mysterious theme inspired by deep-sea and sci-fi aesthetics.",
        use_cases=[
            "Gaming sites",
            "Sci-fi brands",
            "Developer platforms",
            "Immersive apps"
        ],
        target_audience="Gamers and users attracted to deep, immersive visuals",
        design_philosophy="Create mystery through layered dark palettes and glows",
        visual_characteristics={
            "color_palette": "Black, deep blues, neon accents",
            "typography": "Monospace or geometric sans",
            "spacing": "Tight, immersive spacing",
            "components": "Glowing CTAs, layered depth",
            "interactions": "Glows, fades, immersive hover states",
            "layout": "Scene-like, layered structures"
        },
        accessibility_priority="AA target – ensure readability in deep-dark contrasts",
        implementation_notes="Use neon accents sparingly for focus points"
    ),

    "silk": ThemeSpec(
        name="Silk",
        description="Soft, elegant theme with luxurious minimalism and smooth surfaces.",
        use_cases=[
            "Luxury brands",
            "Fashion ecommerce",
            "Portfolios",
            "Premium apps"
        ],
        target_audience="Premium, design-conscious users",
        design_philosophy="Use softness and refinement to convey luxury",
        visual_characteristics={
            "color_palette": "Ivory, beige, muted gold accents",
            "typography": "Elegant serif + sans pairing",
            "spacing": "Generous, flowing whitespace",
            "components": "Subtle shadows, refined borders",
            "interactions": "Smooth, slow transitions",
            "layout": "Minimal grid with refined spacing"
        },
        accessibility_priority="AA target – confirm beige/ivory contrast remains strong",
        implementation_notes="Pair muted gold only with high-contrast surfaces"
    )
}

def get_theme_design_system_rules(theme_name: str) -> str:
    """Generate theme-specific design system rules for prompts"""
    if theme_name not in THEME_SPECIFICATIONS:
        return ""
    
    theme = THEME_SPECIFICATIONS[theme_name]
    
    return f"""
THEME-SPECIFIC DESIGN SYSTEM RULES FOR {theme.name.upper()}:

Philosophy: {theme.design_philosophy}
Target Use: {', '.join(theme.use_cases[:2])}

Visual Requirements:
- Colors: {theme.visual_characteristics['color_palette']}
- Typography: {theme.visual_characteristics['typography']}
- Spacing: {theme.visual_characteristics['spacing']}
- Components: {theme.visual_characteristics['components']}
- Interactions: {theme.visual_characteristics['interactions']}
- Layout: {theme.visual_characteristics['layout']}

Accessibility: {theme.accessibility_priority}
Implementation Notes: {theme.implementation_notes}

CRITICAL: All design tokens must align with these {theme.name} theme characteristics.
"""

def get_theme_choices() -> List[str]:
    """Get all available theme names"""
    return list(THEME_SPECIFICATIONS.keys())

def get_theme_description(theme_name: str) -> str:
    """Get theme description for CLI help"""
    if theme_name not in THEME_SPECIFICATIONS:
        return "Unknown theme"
    
    theme = THEME_SPECIFICATIONS[theme_name]
    return f"{theme.description}"

def detect_theme_from_content(content: str) -> str:
    """Enhanced theme detection from HTML/CSS content with priority-based scoring"""
    content_lower = content.lower()

    # Initialize scoring for all themes
    scores = {}

    # High-priority theme detection patterns

    # Brutalist (check before dark theme since both use bg-black)
    brutalist_score = 0
    if 'brutalist-border' in content_lower: brutalist_score += 10
    if 'brutalist-shadow' in content_lower: brutalist_score += 10
    if 'font-black' in content_lower: brutalist_score += 5
    if 'font-bold uppercase' in content_lower: brutalist_score += 3
    if 'bg-red-600' in content_lower and 'bg-yellow-400' in content_lower: brutalist_score += 5
    if 'jetbrains mono' in content_lower: brutalist_score += 3
    scores['brutalist'] = brutalist_score

    # Morphism
    morphism_score = 0
    if 'backdrop-filter' in content_lower: morphism_score += 10
    if 'glassmorphism' in content_lower: morphism_score += 10
    if 'neumorphism' in content_lower: morphism_score += 10
    if 'bg-white/20' in content_lower or 'bg-opacity-' in content_lower: morphism_score += 5
    scores['morphism'] = morphism_score

    # Terminal
    terminal_score = 0
    if 'font-mono' in content_lower: terminal_score += 5
    if 'text-green-400' in content_lower or 'text-green-500' in content_lower: terminal_score += 5
    if 'border-green-500' in content_lower: terminal_score += 5
    if 'animate-pulse' in content_lower and 'green' in content_lower: terminal_score += 3
    if 'terminal' in content_lower: terminal_score += 3
    scores['terminal'] = terminal_score

    # Synthwave
    synthwave_score = 0
    if 'synthwave' in content_lower: synthwave_score += 10
    if 'neon' in content_lower and ('pink' in content_lower or 'cyan' in content_lower): synthwave_score += 8
    if 'glow' in content_lower and ('purple' in content_lower or 'magenta' in content_lower): synthwave_score += 6
    if '80s' in content_lower or 'retro-futur' in content_lower: synthwave_score += 5
    scores['synthwave'] = synthwave_score

    # Cyberpunk
    cyberpunk_score = 0
    if 'cyberpunk' in content_lower: cyberpunk_score += 10
    if 'neon' in content_lower and 'black' in content_lower: cyberpunk_score += 8
    if 'cyber' in content_lower or 'tech-noir' in content_lower: cyberpunk_score += 6
    if 'flicker' in content_lower or 'glitch' in content_lower: cyberpunk_score += 5
    scores['cyberpunk'] = cyberpunk_score

    # Dracula
    dracula_score = 0
    if 'dracula' in content_lower: dracula_score += 10
    if 'bg-purple-' in content_lower and 'bg-pink-' in content_lower: dracula_score += 8
    if 'developer' in content_lower and 'dark' in content_lower: dracula_score += 6
    if 'code' in content_lower and ('purple' in content_lower or 'pink' in content_lower): dracula_score += 5
    scores['dracula'] = dracula_score

    # Nord
    nord_score = 0
    if 'nord' in content_lower: nord_score += 10
    if 'nordic' in content_lower: nord_score += 8
    if 'bg-slate-' in content_lower or 'bg-blue-gray-' in content_lower: nord_score += 6
    if 'cool' in content_lower and ('blue' in content_lower or 'gray' in content_lower): nord_score += 4
    scores['nord'] = nord_score

    # Night
    night_score = 0
    if 'night' in content_lower and 'theme' in content_lower: night_score += 10
    if 'bg-indigo-' in content_lower or 'bg-navy' in content_lower: night_score += 6
    if 'reading' in content_lower and 'dark' in content_lower: night_score += 5
    scores['night'] = night_score

    # Light
    light_score = 0
    if 'light' in content_lower and 'theme' in content_lower: light_score += 10
    if 'bg-white' in content_lower and 'text-gray-900' in content_lower: light_score += 8
    if 'bright' in content_lower and 'minimal' in content_lower: light_score += 5
    scores['light'] = light_score

    # Luxury
    luxury_score = 0
    if 'luxury' in content_lower: luxury_score += 10
    if 'gold' in content_lower and 'black' in content_lower: luxury_score += 8
    if 'premium' in content_lower or 'elegant' in content_lower: luxury_score += 6
    if 'serif' in content_lower and 'refined' in content_lower: luxury_score += 4
    scores['luxury'] = luxury_score

    # Playful
    playful_score = 0
    if 'playful' in content_lower: playful_score += 10
    if 'rounded-xl' in content_lower or 'rounded-2xl' in content_lower: playful_score += 5
    if 'bg-pink-' in content_lower or 'bg-purple-' in content_lower: playful_score += 5
    if 'hover:scale-' in content_lower: playful_score += 3
    if 'gradient' in content_lower and ('pink' in content_lower or 'purple' in content_lower): playful_score += 5
    scores['playful'] = playful_score

    # Corporate
    corporate_score = 0
    if 'corporate' in content_lower: corporate_score += 10
    if 'bg-blue-900' in content_lower or 'bg-blue-800' in content_lower: corporate_score += 5
    if 'shadow-lg' in content_lower or 'shadow-xl' in content_lower: corporate_score += 3
    if 'professional' in content_lower: corporate_score += 5
    scores['corporate'] = corporate_score

    # Dark theme (check after other dark themes to avoid conflicts)
    dark_score = 0
    if 'dark' in content_lower and 'theme' in content_lower and 'night' not in content_lower: dark_score += 10
    if 'bg-gray-900' in content_lower: dark_score += 5
    if 'text-gray-100' in content_lower or 'text-white' in content_lower: dark_score += 3
    if 'border-gray-700' in content_lower: dark_score += 3
    scores['dark'] = dark_score

    # Medium-priority themes

    # Emerald
    if 'emerald' in content_lower or ('green' in content_lower and 'health' in content_lower):
        scores['emerald'] = 8
    elif 'bg-emerald-' in content_lower or 'text-emerald-' in content_lower:
        scores['emerald'] = 6
    else:
        scores['emerald'] = 0

    # Sunset
    if 'sunset' in content_lower or ('gradient' in content_lower and 'orange' in content_lower and 'pink' in content_lower):
        scores['sunset'] = 8
    elif 'bg-gradient-to-' in content_lower and ('orange' in content_lower or 'pink' in content_lower):
        scores['sunset'] = 6
    else:
        scores['sunset'] = 0

    # Coffee
    if 'coffee' in content_lower or ('brown' in content_lower and 'cream' in content_lower):
        scores['coffee'] = 8
    elif 'bg-amber-' in content_lower or 'bg-stone-' in content_lower:
        scores['coffee'] = 5
    else:
        scores['coffee'] = 0

    # Get theme with highest score (minimum threshold of 5)
    max_theme = max(scores, key=scores.get) if scores else 'minimal'
    if scores.get(max_theme, 0) >= 5:
        return max_theme

    # Enhanced fallback patterns for remaining themes
    if 'aesthetic' in content_lower or 'y2k' in content_lower or 'vaporwave' in content_lower:
        return 'aesthetic'
    elif 'retro' in content_lower and ('vintage' in content_lower or 'nostalgic' in content_lower):
        return 'retro'
    elif 'vibrant' in content_lower or 'dopamine' in content_lower:
        return 'vibrant'
    elif 'sustainable' in content_lower or 'eco' in content_lower or 'nature' in content_lower:
        return 'sustainable'
    elif 'data' in content_lower or 'dashboard' in content_lower or 'analytics' in content_lower:
        return 'data'
    elif 'illustrated' in content_lower or 'illustration' in content_lower:
        return 'illustrated'
    elif 'animation' in content_lower and ('transform' in content_lower or 'keyframes' in content_lower):
        return 'animated'
    elif 'pastel' in content_lower or ('soft' in content_lower and 'pink' in content_lower):
        return 'pastel'
    elif 'cupcake' in content_lower or ('sweet' in content_lower and 'friendly' in content_lower):
        return 'cupcake'
    elif 'bumblebee' in content_lower or ('yellow' in content_lower and 'warm' in content_lower):
        return 'bumblebee'
    elif 'lemonade' in content_lower or ('citrus' in content_lower and 'yellow' in content_lower):
        return 'lemonade'
    elif 'garden' in content_lower or ('botanical' in content_lower and 'green' in content_lower):
        return 'garden'
    elif 'forest' in content_lower or ('deep' in content_lower and 'green' in content_lower):
        return 'forest'
    elif 'aqua' in content_lower or ('cyan' in content_lower and 'teal' in content_lower):
        return 'aqua'
    elif 'winter' in content_lower or ('crisp' in content_lower and 'blue' in content_lower):
        return 'winter'
    elif 'autumn' in content_lower or ('warm' in content_lower and 'orange' in content_lower):
        return 'autumn'
    elif 'valentine' in content_lower or ('romantic' in content_lower and 'pink' in content_lower):
        return 'valentine'
    elif 'halloween' in content_lower or ('spooky' in content_lower and 'purple' in content_lower):
        return 'halloween'
    elif 'fantasy' in content_lower or ('magical' in content_lower and 'jewel' in content_lower):
        return 'fantasy'
    elif 'cmyk' in content_lower or ('print' in content_lower and 'bold' in content_lower):
        return 'cmyk'
    elif 'acid' in content_lower or ('fluorescent' in content_lower and 'bright' in content_lower):
        return 'acid'
    elif 'business' in content_lower and 'neutral' in content_lower:
        return 'business'
    elif 'black' in content_lower and 'pure' in content_lower:
        return 'black'
    elif 'wireframe' in content_lower or ('prototype' in content_lower and 'outline' in content_lower):
        return 'wireframe'
    elif 'lofi' in content_lower or ('muted' in content_lower and 'calm' in content_lower):
        return 'lofi'
    elif 'dim' in content_lower or ('low-contrast' in content_lower and 'dark' in content_lower):
        return 'dim'
    elif 'caramellatte' in content_lower or ('caramel' in content_lower and 'latte' in content_lower):
        return 'caramellatte'
    elif 'abyss' in content_lower or ('deep-sea' in content_lower and 'mysterious' in content_lower):
        return 'abyss'
    elif 'silk' in content_lower or ('elegant' in content_lower and 'soft' in content_lower):
        return 'silk'
    else:
        return 'minimal'