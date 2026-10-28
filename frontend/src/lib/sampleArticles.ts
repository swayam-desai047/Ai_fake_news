export interface ArticleDimensionScores {
    sentiment: number;
    bias: number;
    objectivity: number;
    readability: number;
    propaganda: number;
    headline_accuracy: number;
    source_credibility: number;
    content_quality: number;
    explanations: {
        sentiment: string;
        bias: string;
        objectivity: string;
        readability: string;
        propaganda: string;
        headline_accuracy: string;
        source_credibility: string;
        content_quality: string;
    };
}

export interface NewsArticle {
    id: string;
    title: string;
    source_domain: string;
    source_url: string;
    content_summary: string;
    ai_summary: string;
    category: 'general' | 'politics' | 'business' | 'technology' | 'sports';
    sentiment: 'positive' | 'negative' | 'neutral';
    is_fake: boolean;
    credibility_score: number;
    risk_score: number;
    confidence_level: number;
    credibility_label: 'Low Risk' | 'Moderate Risk' | 'High Risk';
    needs_verification: boolean;
    ai_reasoning: string;
    dimensions: ArticleDimensionScores;
    group_id?: string;
    event_title?: string;
    published_at: string;
    created_at: string;
}

export const SAMPLE_ARTICLES: NewsArticle[] = [
    // -------------------------------------------------------------
    // BUSINESS ARTICLES (Real working links)
    // -------------------------------------------------------------
    {
        id: "biz-001",
        title: "Federal Reserve Holds Benchmark Rates Steady as Global Inflation Cools",
        source_domain: "Bloomberg",
        source_url: "https://www.bloomberg.com/markets",
        content_summary: "The Federal Open Market Committee opted to hold interest rates unchanged at 4.25%-4.50%, highlighting persistent progress in bringing core inflation toward the 2 percent target while maintaining resilient labor market metrics.",
        ai_summary: "The Federal Reserve kept interest rates steady between 4.25% and 4.50% following continued declines in core inflation. Fed officials noted consumer spending and corporate earnings remain in stable equilibrium.",
        category: "business",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.95,
        risk_score: 0.05,
        confidence_level: 0.98,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Strictly factual economic reporting relying on public Federal Reserve transcripts and official macroeconomic indicators.",
        dimensions: {
            sentiment: 72,
            bias: 92,
            objectivity: 96,
            readability: 75,
            propaganda: 98,
            headline_accuracy: 97,
            source_credibility: 96,
            content_quality: 94,
            explanations: {
                sentiment: "Objective tone reflecting monetary stability and balanced economic indicators.",
                bias: "Balanced reporting quoting Federal Reserve officials and Wall Street analysts.",
                objectivity: "Contains explicit basis point ranges, inflation metrics, and historical interest rate indices.",
                readability: "Flesch Reading Ease: 64.2 (Standard economic financial reporting).",
                propaganda: "Zero sensationalism, clickbait phrasing, or speculative bias.",
                headline_accuracy: "Headline accurately summarizes the central committee vote outcome.",
                source_credibility: "Bloomberg is an accredited global financial intelligence service.",
                content_quality: "Robust analytical framing with multi-decade context."
            }
        },
        group_id: "cluster-fed-rates-2026",
        event_title: "Federal Reserve Monetary Policy Review",
        published_at: "2026-10-27T16:00:00Z",
        created_at: "2026-10-27T16:00:00Z"
    },
    {
        id: "biz-002",
        title: "Global Semiconductor Alliance Announces $45B Advanced Packaging Fab in Dresden",
        source_domain: "Reuters",
        source_url: "https://www.reuters.com/business/",
        content_summary: "A joint venture backed by leading European and Asian semiconductor makers will break ground on a $45 billion high-density packaging facility in Dresden. The fab aims to manufacture sub-2nm nodes for automotive and cloud data centers.",
        ai_summary: "A coalition of international chipmakers committed $45B to construct an advanced packaging fabrication plant in Dresden. The facility will strengthen sub-2nm silicon supply chains across Europe.",
        category: "business",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.93,
        risk_score: 0.07,
        confidence_level: 0.95,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Official corporate disclosures cross-referenced with European Union ministerial press briefings.",
        dimensions: {
            sentiment: 80,
            bias: 88,
            objectivity: 94,
            readability: 70,
            propaganda: 94,
            headline_accuracy: 96,
            source_credibility: 95,
            content_quality: 93,
            explanations: {
                sentiment: "Optimistic commercial coverage of large-scale infrastructure investments.",
                bias: "Direct attribution to joint venture partners and national commerce ministries.",
                objectivity: "Verifiable dollar figures, location specifics, and technological node milestones.",
                readability: "Flesch Reading Ease: 61.8 (Formal industrial news standard).",
                propaganda: "Free from commercial hyperbole or unwarranted guarantees.",
                headline_accuracy: "Headline strictly aligns with the announced capital allocation.",
                source_credibility: "Reuters is an established international wire provider.",
                content_quality: "High syntactic coherence and detailed supply chain impact analysis."
            }
        },
        group_id: "cluster-chip-fab-2026",
        event_title: "Dresden $45B Semiconductor Packaging Fab Investment",
        published_at: "2026-10-27T12:15:00Z",
        created_at: "2026-10-27T12:15:00Z"
    },

    // -------------------------------------------------------------
    // POLITICS ARTICLES (Real working links)
    // -------------------------------------------------------------
    {
        id: "pol-001",
        title: "Parliamentary Coalition Reaches Bipartisan Accord on Digital Sovereignty Act",
        source_domain: "BBC News",
        source_url: "https://www.bbc.com/news/politics",
        content_summary: "Lawmakers across party aisles have finalized negotiations on the Digital Sovereignty Act, establishing citizen data ownership protections and stricter oversight protocols for cross-border cloud providers.",
        ai_summary: "A cross-party legislative coalition agreed on the Digital Sovereignty Act, establishing stringent domestic cloud hosting requirements and enforceable user privacy rights.",
        category: "politics",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.92,
        risk_score: 0.08,
        confidence_level: 0.94,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Verified parliamentary hansard records and direct public interviews with committee rapporteurs.",
        dimensions: {
            sentiment: 75,
            bias: 89,
            objectivity: 93,
            readability: 74,
            propaganda: 96,
            headline_accuracy: 94,
            source_credibility: 95,
            content_quality: 92,
            explanations: {
                sentiment: "Constructive tone recording legislative compromise and statutory agreement.",
                bias: "Balanced quotes from both ruling coalition and opposition spokespersons.",
                objectivity: "Direct references to legislative clauses, committee reports, and timetables.",
                readability: "Flesch Reading Ease: 65.4 (Accessible political journalism).",
                propaganda: "No partisan loaded terminology or inflammatory rhetoric.",
                headline_accuracy: "Headline accurately reflects the bipartisan consensus reached in committee.",
                source_credibility: "BBC News retains high editorial credibility.",
                content_quality: "Comprehensive analysis of constitutional and economic implications."
            }
        },
        group_id: "cluster-digital-act-2026",
        event_title: "Digital Sovereignty Act Legislative Accord",
        published_at: "2026-10-27T15:20:00Z",
        created_at: "2026-10-27T15:20:00Z"
    },
    {
        id: "pol-002",
        title: "Bilateral Trade Dialogue Resumes to Address Clean Tech Supply Chain Tariffs",
        source_domain: "Al Jazeera",
        source_url: "https://www.aljazeera.com/economy",
        content_summary: "Trade delegations from five major economies gathered for high-level talks aimed at reducing reciprocal tariff barriers on electric vehicles, battery components, and photovoltaic modules.",
        ai_summary: "Five international trade delegations resumed consultations on easing tariffs for green energy technologies, focusing on EV batteries and solar equipment.",
        category: "politics",
        sentiment: "neutral",
        is_fake: false,
        credibility_score: 0.88,
        risk_score: 0.12,
        confidence_level: 0.90,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Official multilateral joint communiqués and accredited diplomatic press pool verification.",
        dimensions: {
            sentiment: 66,
            bias: 84,
            objectivity: 88,
            readability: 72,
            propaganda: 91,
            headline_accuracy: 92,
            source_credibility: 89,
            content_quality: 89,
            explanations: {
                sentiment: "Pragmatic, neutral framing of delicate diplomatic negotiations.",
                bias: "Presents economic positions of both exporting and importing nations fairly.",
                objectivity: "Empirical focus on harmonized tariff schedules and WTO frameworks.",
                readability: "Flesch Reading Ease: 63.9 (Standard diplomatic news format).",
                propaganda: "Free from nationalist propaganda or partisan spin.",
                headline_accuracy: "Directly mirrors the agenda stated by lead ambassadors.",
                source_credibility: "Al Jazeera English with international editorial review.",
                content_quality: "Detailed trade statistics and historical tariff comparison."
            }
        },
        published_at: "2026-10-27T13:10:00Z",
        created_at: "2026-10-27T13:10:00Z"
    },

    // -------------------------------------------------------------
    // SPORTS ARTICLES (Real working links)
    // -------------------------------------------------------------
    {
        id: "spo-001",
        title: "Record-Breaking Comeback Secures Continental Football Championship in Thrilling Final",
        source_domain: "BBC Sport",
        source_url: "https://www.bbc.com/sport/football",
        content_summary: "In a dramatic 3-2 victory in extra time, the defending champions overcame a two-goal deficit to retain the continental crown before 78,000 spectators at Wembley Stadium.",
        ai_summary: "The defending champions claimed the continental football title after staging a dramatic comeback from 2-0 down to triumph 3-2 in extra time at Wembley.",
        category: "sports",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.96,
        risk_score: 0.04,
        confidence_level: 0.98,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Live stadium match broadcast, official UEFA/FIFA match sheet, and verified post-match press conferences.",
        dimensions: {
            sentiment: 88,
            bias: 91,
            objectivity: 94,
            readability: 82,
            propaganda: 96,
            headline_accuracy: 97,
            source_credibility: 96,
            content_quality: 93,
            explanations: {
                sentiment: "Energetic and celebratory tone capturing championship excitement.",
                bias: "Fair commentary highlighting decisive tactical choices by both head coaches.",
                objectivity: "Accurate minute-by-minute match statistics, fouls, possession rates, and scores.",
                readability: "Flesch Reading Ease: 76.2 (Engaging, readable sports narrative).",
                propaganda: "Standard sports entertainment journalism without misleading assertions.",
                headline_accuracy: "Headline strictly reflects the exact match progression and scoreline.",
                source_credibility: "BBC Sport is a premier sports journalism desk.",
                content_quality: "Vivid match description with comprehensive statistical analysis."
            }
        },
        group_id: "cluster-championship-final-2026",
        event_title: "Continental Championship Final",
        published_at: "2026-10-27T22:30:00Z",
        created_at: "2026-10-27T22:30:00Z"
    },
    {
        id: "spo-002",
        title: "International Olympic Committee Confirms Candidate Cities for 2036 Summer Games",
        source_domain: "Reuters",
        source_url: "https://www.reuters.com/sports/",
        content_summary: "The International Olympic Committee Executive Board released the verified shortlist of four candidate host metropolitan areas for the 2036 Olympic and Paralympic Games following sustainability audits.",
        ai_summary: "The IOC officially announced four shortlisted host cities for the 2036 Olympic Games after completing preliminary carbon-neutral infrastructure reviews.",
        category: "sports",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.94,
        risk_score: 0.06,
        confidence_level: 0.96,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Verified IOC executive board press release and official Lausanne conference presentation.",
        dimensions: {
            sentiment: 76,
            bias: 90,
            objectivity: 95,
            readability: 74,
            propaganda: 95,
            headline_accuracy: 96,
            source_credibility: 95,
            content_quality: 92,
            explanations: {
                sentiment: "Positive and formal coverage of global athletic event selection.",
                bias: "Equitable overview of candidate bids without regional favoritism.",
                objectivity: "Quotes official selection criteria, venue capacity, and transport benchmarks.",
                readability: "Flesch Reading Ease: 67.8 (Clean, institutional sports reporting).",
                propaganda: "No promotional cheerleading; emphasizes strict governance rules.",
                headline_accuracy: "Headline precisely communicates the shortlist announcement.",
                source_credibility: "Reuters Sports desk.",
                content_quality: "Clear structured evaluation of financial and venue readiness."
            }
        },
        published_at: "2026-10-27T10:00:00Z",
        created_at: "2026-10-27T10:00:00Z"
    },

    // -------------------------------------------------------------
    // TECHNOLOGY ARTICLES (Real working links)
    // -------------------------------------------------------------
    {
        id: "tech-001",
        title: "Global Tech Summit Ratifies First Unified AI Safety Governance Accord",
        source_domain: "Reuters",
        source_url: "https://www.reuters.com/technology/artificial-intelligence/",
        content_summary: "Delegates representing 48 nations have formally signed the landmark AI Safety Accord in Geneva. The treaty mandates rigorous third-party red-teaming for frontier foundation models and creates an international incident registry.",
        ai_summary: "48 nations ratified the Geneva AI Safety Accord establishing mandatory third-party red-teaming for frontier AI models. The pact also inaugurates an international incident registry to monitor synthetic media threats.",
        category: "technology",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.94,
        risk_score: 0.06,
        confidence_level: 0.96,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Article adheres to strict neutral attribution standards with multi-institutional citations from verified diplomatic delegations.",
        dimensions: {
            sentiment: 74,
            bias: 88,
            objectivity: 91,
            readability: 72,
            propaganda: 95,
            headline_accuracy: 94,
            source_credibility: 96,
            content_quality: 92,
            explanations: {
                sentiment: "Cautiously optimistic and fact-focused tone describing diplomatic progress.",
                bias: "Balanced reporting referencing perspectives of sovereign signatories and tech bodies.",
                objectivity: "Contains direct quotations, specific treaty names, and empirical timelines.",
                readability: "Flesch Reading Ease: 62.1 (Standard university publication grade level).",
                propaganda: "Zero manipulative language or clickbait phrasing detected.",
                headline_accuracy: "Headline corresponds directly with key terms of the signed treaty.",
                source_credibility: "Reuters is an established Tier-1 international wire service.",
                content_quality: "High syntactic coherence, comprehensive factual context, and proper sourcing."
            }
        },
        group_id: "cluster-ai-treaty-2026",
        event_title: "Geneva 2026 International AI Safety Accord",
        published_at: "2026-10-27T14:30:00Z",
        created_at: "2026-10-27T14:30:00Z"
    },
    {
        id: "tech-002",
        title: "Quantum Computing Milestone: Fault-Tolerant Logical Qubits Demonstrate 99.9% Error Suppression",
        source_domain: "TechCrunch",
        source_url: "https://techcrunch.com/category/artificial-intelligence/",
        content_summary: "Research laboratories have demonstrated physical quantum processors operating with 100 fault-tolerant logical qubits, showing exponential suppression of phase-flip errors in peer-reviewed benchmarks.",
        ai_summary: "Researchers demonstrated 100 error-corrected logical qubits achieving 99.9% gate fidelity, marking a critical transition toward fault-tolerant commercial quantum hardware.",
        category: "technology",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.92,
        risk_score: 0.08,
        confidence_level: 0.94,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Peer-reviewed scientific validation published in Nature Physics with open-access benchmark data.",
        dimensions: {
            sentiment: 79,
            bias: 90,
            objectivity: 96,
            readability: 68,
            propaganda: 97,
            headline_accuracy: 95,
            source_credibility: 91,
            content_quality: 94,
            explanations: {
                sentiment: "Scientific excitement grounded in reproducible experimental metrics.",
                bias: "Fair comparison against competing neutral-atom and superconducting architectures.",
                objectivity: "Exact error threshold percentages, coherence lifetimes, and gate counts.",
                readability: "Flesch Reading Ease: 58.2 (Technical computer science domain level).",
                propaganda: "Strictly avoids quantum hype tropes or magical computation claims.",
                headline_accuracy: "Headline precisely mirrors the paper's quantitative abstract.",
                source_credibility: "TechCrunch Science & DeepTech reporting division.",
                content_quality: "Includes diagrams, error budget tables, and links to source code."
            }
        },
        published_at: "2026-10-27T11:00:00Z",
        created_at: "2026-10-27T11:00:00Z"
    },

    // -------------------------------------------------------------
    // GENERAL ARTICLES (Real working links)
    // -------------------------------------------------------------
    {
        id: "gen-001",
        title: "Clean Energy Output Reaches Historic 40% Milestone on European Power Grid",
        source_domain: "Al Jazeera",
        source_url: "https://www.aljazeera.com/economy",
        content_summary: "Solar, wind, and hydroelectric generation collectively supplied more than 40 percent of total European electricity demand during the third quarter of 2026, according to transmission grid operator ENTSO-E.",
        ai_summary: "Renewable energy sources accounted for over 40% of Europe's power grid output in Q3 2026, driven by record solar capacity additions and offshore wind generation.",
        category: "general",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.89,
        risk_score: 0.11,
        confidence_level: 0.91,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Cites official grid operators with verifiable quarterly energy production metrics.",
        dimensions: {
            sentiment: 78,
            bias: 86,
            objectivity: 92,
            readability: 74,
            propaganda: 90,
            headline_accuracy: 95,
            source_credibility: 88,
            content_quality: 91,
            explanations: {
                sentiment: "Factual reporting on industrial milestone with positive environmental implications.",
                bias: "Relies on non-partisan grid operator telemetry data.",
                objectivity: "Contains quarterly statistics, percentage breakdowns, and seasonal comparisons.",
                readability: "Flesch Reading Ease: 65.2 (Clear, accessible science journalism).",
                propaganda: "Standard economic and infrastructure reporting style.",
                headline_accuracy: "Direct alignment between headline percentage and body statistics.",
                source_credibility: "Al Jazeera English with international editorial review.",
                content_quality: "Thorough investigative structure with corroborating energy charts."
            }
        },
        published_at: "2026-10-27T11:20:00Z",
        created_at: "2026-10-27T11:20:00Z"
    },
    {
        id: "gen-002",
        title: "Historic Artemis IV Crew Lands Safely at Moon's South Pole Basin",
        source_domain: "CNN",
        source_url: "https://www.cnn.com/world",
        content_summary: "NASA's Artemis IV lunar lander touched down at Shackleton Crater at 06:14 UTC. Astronauts reported all systems nominal as they prepared for a 7-day science exploration mission searching for water ice deposits.",
        ai_summary: "The Artemis IV crew achieved a successful lunar touchdown at Shackleton Crater. The team has commenced mission preparation for ice sampling and geological surveying.",
        category: "general",
        sentiment: "positive",
        is_fake: false,
        credibility_score: 0.96,
        risk_score: 0.04,
        confidence_level: 0.97,
        credibility_label: "Low Risk",
        needs_verification: false,
        ai_reasoning: "Live feed official transmission data confirmed by NASA and ESA mission control centers.",
        dimensions: {
            sentiment: 82,
            bias: 90,
            objectivity: 94,
            readability: 75,
            propaganda: 95,
            headline_accuracy: 96,
            source_credibility: 95,
            content_quality: 94,
            explanations: {
                sentiment: "Celebratory tone reflecting scientific achievement.",
                bias: "Direct attribution to NASA flight director and onboard communications.",
                objectivity: "Detailed timestamps, coordinates, and telemetry readings.",
                readability: "Flesch Reading Ease: 67.5 (Standard mainstream journalism).",
                propaganda: "No emotional distortion or manipulative rhetoric.",
                headline_accuracy: "Headline accurately describes location and mission status.",
                source_credibility: "CNN Space Bureau with verified official pool access.",
                content_quality: "Excellent structural progression and verified background details."
            }
        },
        group_id: "cluster-lunar-landing-2026",
        event_title: "Artemis IV Lunar South Pole Landing",
        published_at: "2026-10-27T06:30:00Z",
        created_at: "2026-10-27T06:30:00Z"
    }
];

export function getSampleArticles(query?: string, category?: string): NewsArticle[] {
    let list = [...SAMPLE_ARTICLES];
    const cat = category && category.toLowerCase() !== 'all' ? category.toLowerCase() : '';

    if (cat) {
        list = list.filter(a => a.category.toLowerCase() === cat);
    }

    if (query && query.trim()) {
        const q = query.trim().toLowerCase();
        list = list.filter(a =>
            a.title.toLowerCase().includes(q) ||
            a.content_summary.toLowerCase().includes(q) ||
            a.ai_summary.toLowerCase().includes(q) ||
            a.source_domain.toLowerCase().includes(q)
        );
    }

    return list;
}
