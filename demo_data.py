"""Pre-baked demo result. Returned instantly with NO API call so a live demo
never fails on flaky wifi or API issues. Triggered by the 'Demo mode' toggle in
the UI, or by setting DEMO_MODE=1 in the environment.
"""

DEMO_GOALS = (
    "Founder raising a pre-seed round; looking for early-stage AI investors and "
    "design-partner customers."
)

DEMO_PEOPLE = [
    {
        "name": "Maya Chen",
        "brief": "Partner at Foundry Labs, an early-stage fund focused on AI "
        "infrastructure and developer tools. Recently led a seed round in a vector "
        "database startup and writes about the infra-vs-app investment debate.",
        "topics": ["AI infra", "dev tools", "seed investing"],
        "sources": [
            "https://foundrylabs.example.com/team/maya-chen",
            "https://twitter.com/mayachen",
        ],
        "score": 95,
        "reason": "Active pre-seed AI investor whose thesis directly matches your raise.",
        "starters": [
            "I saw Foundry just led a vector-DB seed — are you more bullish on the infra layer than the app layer right now?",
            "Your piece on 'picks and shovels' AI investing really resonated — how are you thinking about agent infra?",
            "I'm building in the AI tooling space and raising pre-seed — would love your read on the current market.",
        ],
    },
    {
        "name": "Devesh Rao",
        "brief": "Head of Platform Engineering at Northwind, a 400-person fintech. "
        "Leads a team evaluating AI agents for internal automation and has spoken "
        "about buying vs building AI tooling.",
        "topics": ["platform eng", "AI adoption", "fintech"],
        "sources": ["https://northwind.example.com/blog/ai-tooling"],
        "score": 82,
        "reason": "Strong design-partner candidate actively evaluating AI tools to buy.",
        "starters": [
            "You talked about buy-vs-build for AI tooling at Northwind — where did you land for agent workflows?",
            "I'm looking for design partners for an AI tool aimed at platform teams — open to comparing notes?",
            "How is your team measuring ROI on the AI pilots you've run so far?",
        ],
    },
    {
        "name": "Sofia Alvarez",
        "brief": "Founder of Lumen, a Series A analytics startup. Two-time founder "
        "with a prior exit; mentors at several accelerators and is well connected "
        "among early-stage operators.",
        "topics": ["founder", "analytics", "go-to-market"],
        "sources": ["https://lumen.example.com/about"],
        "score": 71,
        "reason": "Not an investor, but a connected operator who can intro you to funds.",
        "starters": [
            "You've raised a Series A recently — what surprised you most about the early-stage market this cycle?",
            "I'm raising pre-seed and admire how Lumen found its GTM wedge — how did you crack early distribution?",
            "Any investors you'd say really 'get' AI infra that I should be talking to?",
        ],
    },
    {
        "name": "Tom Becker",
        "brief": "Senior Product Designer at a consumer social app. Focused on mobile "
        "UX and design systems; no public investing or enterprise-buying activity.",
        "topics": ["product design", "mobile UX"],
        "sources": [],
        "score": 28,
        "reason": "Talented but weak fit for a pre-seed raise or B2B design partnership.",
        "starters": [
            "Love the craft in consumer design lately — what's a product you think nails onboarding?",
            "How do you balance design-system consistency with shipping fast?",
            "What's caught your eye in AI-assisted design tools recently?",
        ],
    },
]


def demo_result() -> dict:
    return {
        "people": DEMO_PEOPLE,
        "note": "Demo mode — sample data, no API call. Toggle off to run live.",
    }
