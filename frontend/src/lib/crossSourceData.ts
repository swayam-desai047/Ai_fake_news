export interface ClusteredArticle {
    id: string;
    publisher: string;
    publisherDomain: string;
    title: string;
    url: string;
    publishedAt: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    credibilityScore: number;
    riskTier: 'Low Risk' | 'Moderate Risk' | 'High Risk';
    headlineDivergence: string; // How this headline frames the story
    narrativeFocus: string; // What specific angle this publisher highlights
    contentSnippet: string;
    dimensions: {
        sentiment: number;
        bias: number;
        objectivity: number;
        readability: number;
        propaganda: number;
        headline_accuracy: number;
        source_credibility: number;
        content_quality: number;
    };
}

export interface StoryCluster {
    id: string;
    eventTitle: string;
    category: 'technology' | 'business' | 'politics' | 'sports' | 'general';
    consensusRate: number; // e.g. 94 for 94%
    summary: string;
    agreedFacts: string[];
    divergences: string[];
    articles: ClusteredArticle[];
}

export const CURATED_STORY_CLUSTERS: StoryCluster[] = [
    {
        id: "cluster-ai-treaty-2026",
        eventTitle: "Geneva 2026 International AI Safety Accord & Frontier Compute Audits",
        category: "technology",
        consensusRate: 94,
        summary: "Over 40 nations and top frontier research laboratories signed a multilateral governance accord in Geneva mandating independent algorithmic audits and compute registries for frontier models exceeding 10^26 FLOPs.",
        agreedFacts: [
            "Signed in Geneva with 42 national delegations and major frontier AI laboratories.",
            "Establishes a multilateral registry for computing clusters operating above 10^26 FLOPs.",
            "Requires third-party red-teaming and safety audits before deployment of autonomous agents.",
            "Takes effect formally in Q3 2027 with initial reporting guidelines starting next month."
        ],
        divergences: [
            "Reuters focuses heavily on international diplomatic compliance and treaty enforcement mechanisms.",
            "TechCrunch highlights startup exemptions, compute tier thresholds, and open-source licensing impact.",
            "BBC News emphasizes civil liberties safeguards, algorithmic discrimination, and EU regulatory alignment.",
            "The Verge investigates whether hardware compute tracking can be enforced without border inspections."
        ],
        articles: [
            {
                id: "art-ai-reuters",
                publisher: "Reuters",
                publisherDomain: "reuters.com",
                title: "Global Envoys Conclude Landmark AI Safety Treaty with Mandatory Frontier Audits",
                url: "https://www.reuters.com/technology/",
                publishedAt: "2026-10-27T14:30:00Z",
                sentiment: "positive",
                credibilityScore: 0.95,
                riskTier: "Low Risk",
                headlineDivergence: "Diplomatic & Procedural Consensus",
                narrativeFocus: "Focuses on multilateral state negotiations, treaty legalities, and enforcement mandates across Geneva delegations.",
                contentSnippet: "Diplomats from 42 nations reached consensus on the Geneva Frontier AI Governance Accord, establishing international baseline verification protocols for compute clusters exceeding 10^26 FLOPs.",
                dimensions: {
                    sentiment: 72,
                    bias: 92,
                    objectivity: 96,
                    readability: 74,
                    propaganda: 98,
                    headline_accuracy: 97,
                    source_credibility: 96,
                    content_quality: 95
                }
            },
            {
                id: "art-ai-techcrunch",
                publisher: "TechCrunch",
                publisherDomain: "techcrunch.com",
                title: "What the Geneva AI Treaty Means for Startup Compute Allotments and Open Source",
                url: "https://techcrunch.com/category/artificial-intelligence/",
                publishedAt: "2026-10-27T15:10:00Z",
                sentiment: "neutral",
                credibilityScore: 0.91,
                riskTier: "Low Risk",
                headlineDivergence: "Commercial & Startup Ecosystem Angle",
                narrativeFocus: "Examines compliance burden on venture-backed AI startups and safeguards for open-weights below regulatory thresholds.",
                contentSnippet: "While large labs face rigorous quarterly audits under the new Geneva accord, early-stage startups and research teams utilizing sub-threshold compute pools will operate under streamlined reporting tiers.",
                dimensions: {
                    sentiment: 68,
                    bias: 87,
                    objectivity: 91,
                    readability: 80,
                    propaganda: 92,
                    headline_accuracy: 93,
                    source_credibility: 90,
                    content_quality: 91
                }
            },
            {
                id: "art-ai-bbc",
                publisher: "BBC News",
                publisherDomain: "bbc.com",
                title: "Nations Sign Geneva AI Safety Accord Amid Push for Independent Algorithmic Audits",
                url: "https://www.bbc.com/news/technology",
                publishedAt: "2026-10-27T16:00:00Z",
                sentiment: "neutral",
                credibilityScore: 0.94,
                riskTier: "Low Risk",
                headlineDivergence: "Civil Liberties & Public Accountability",
                narrativeFocus: "Highlights civil society oversight, whistleblower protections, and independent verification of algorithmic bias.",
                contentSnippet: "The Geneva accord incorporates landmark requirements for third-party bias auditing and whistleblower protections, aiming to establish transparent public accountability across generative intelligence systems.",
                dimensions: {
                    sentiment: 70,
                    bias: 91,
                    objectivity: 94,
                    readability: 78,
                    propaganda: 96,
                    headline_accuracy: 95,
                    source_credibility: 95,
                    content_quality: 93
                }
            },
            {
                id: "art-ai-verge",
                publisher: "The Verge",
                publisherDomain: "theverge.com",
                title: "The Global AI Treaty Promises Audits, but Exempts Open Weights Under 10^24 FLOPs",
                url: "https://www.theverge.com/tech",
                publishedAt: "2026-10-27T16:45:00Z",
                sentiment: "neutral",
                credibilityScore: 0.89,
                riskTier: "Low Risk",
                headlineDivergence: "Technical Scrutiny & Hardware Realism",
                narrativeFocus: "Deep-dives into hardware tracking mechanics and whether export-restricted clusters can evade treaty telemetry checks.",
                contentSnippet: "Silicon tracking telemetry remains the treaty's most contentious provision, leaving experts debating whether distributed training runs across unsanctioned data centers can effectively be detected.",
                dimensions: {
                    sentiment: 64,
                    bias: 84,
                    objectivity: 89,
                    readability: 82,
                    propaganda: 90,
                    headline_accuracy: 92,
                    source_credibility: 89,
                    content_quality: 89
                }
            }
        ]
    },
    {
        id: "cluster-rbi-repo-2026",
        eventTitle: "RBI Monetary Policy: Repo Rate Kept Steady at 6.50% with Balanced Growth Outlook",
        category: "business",
        consensusRate: 96,
        summary: "The Reserve Bank of India's Monetary Policy Committee unanimously voted to maintain the policy repo rate unchanged at 6.50%, highlighting resilient GDP expansion alongside controlled core CPI inflation within the 4% target band.",
        agreedFacts: [
            "Policy repo rate held constant at 6.50% by the Monetary Policy Committee (MPC).",
            "Real GDP growth for fiscal 2026-27 projected at 7.0% supported by rural consumption and capital expenditure.",
            "Retail CPI inflation projected at 4.5% with food inflation cooling across core staples.",
            "Stance remains focused on 'withdrawal of accommodation' to align inflation durably with targets."
        ],
        divergences: [
            "Business Standard emphasizes bond market yields, government borrowing stability, and debt liquidity.",
            "Livemint highlights retail borrower impacts, home loan EMI trajectory, and bank fixed deposit interest rates.",
            "The Hindu focuses on rural demand indicators, agricultural harvest outcomes, and monsoon distribution.",
            "Reuters India assesses foreign institutional investor inflows, rupee currency resilience, and global crude oil factors."
        ],
        articles: [
            {
                id: "art-rbi-bs",
                publisher: "Business Standard",
                publisherDomain: "business-standard.com",
                title: "RBI MPC Holds Repo Rate at 6.50% as Yield Curves Stabilize Across Sovereign Bonds",
                url: "https://www.business-standard.com/economy/news",
                publishedAt: "2026-10-27T10:30:00Z",
                sentiment: "positive",
                credibilityScore: 0.94,
                riskTier: "Low Risk",
                headlineDivergence: "Bond Yield & Fixed Income Orientation",
                narrativeFocus: "Examines banking liquidity deficits, sovereign bond yields, and RBI's secondary market bond operations.",
                contentSnippet: "Yields on benchmark 10-year government securities softened by 4 basis points after RBI Governor announced status quo on the repo rate, citing strong macro fundamentals and orderly liquidity management.",
                dimensions: {
                    sentiment: 74,
                    bias: 94,
                    objectivity: 96,
                    readability: 71,
                    propaganda: 97,
                    headline_accuracy: 96,
                    source_credibility: 94,
                    content_quality: 94
                }
            },
            {
                id: "art-rbi-mint",
                publisher: "Livemint",
                publisherDomain: "livemint.com",
                title: "Reserve Bank Pauses Repo Rate at 6.50%: What It Means for Home Loans and Fixed Deposits",
                url: "https://www.livemint.com/economy",
                publishedAt: "2026-10-27T11:00:00Z",
                sentiment: "neutral",
                credibilityScore: 0.92,
                riskTier: "Low Risk",
                headlineDivergence: "Consumer Finance & EMI Impact",
                narrativeFocus: "Breaks down monthly home loan installments, auto loan interest, and senior citizen fixed deposit yields.",
                contentSnippet: "Borrowers with floating-rate home loans will continue with existing EMI structures as the central bank decided against rate cuts, prioritizing inflation control over early monetary easing.",
                dimensions: {
                    sentiment: 69,
                    bias: 90,
                    objectivity: 93,
                    readability: 84,
                    propaganda: 94,
                    headline_accuracy: 94,
                    source_credibility: 92,
                    content_quality: 91
                }
            },
            {
                id: "art-rbi-reuters",
                publisher: "Reuters",
                publisherDomain: "reuters.com",
                title: "India Central Bank Retains Key Policy Rate at 6.50% on Resilient Growth Forecast",
                url: "https://www.reuters.com/world/india/",
                publishedAt: "2026-10-27T11:30:00Z",
                sentiment: "positive",
                credibilityScore: 0.95,
                riskTier: "Low Risk",
                headlineDivergence: "Macroeconomic Growth & Global Currency Stance",
                narrativeFocus: "Focuses on foreign exchange reserves, rupee defense against strong US Dollar index, and trade balances.",
                contentSnippet: "The Reserve Bank of India held its benchmark interest rate steady for the eleventh consecutive meeting, maintaining an upbeat 7% economic growth outlook while monitoring global commodity price volatility.",
                dimensions: {
                    sentiment: 76,
                    bias: 93,
                    objectivity: 97,
                    readability: 76,
                    propaganda: 98,
                    headline_accuracy: 97,
                    source_credibility: 96,
                    content_quality: 95
                }
            }
        ]
    },
    {
        id: "cluster-india-pak-2026",
        eventTitle: "India-Pakistan Bilateral Contacts: Consular Protocols & Humanitarian Repatriation",
        category: "politics",
        consensusRate: 91,
        summary: "Diplomatic representatives of India and Pakistan concluded scheduled bilateral consular talks addressing the repatriation of detained civilian prisoners, border fishermen accords, and maintenance of the 2021 Line of Control ceasefire.",
        agreedFacts: [
            "Scheduled high-level diplomatic and consular meetings held under standard diplomatic protocols.",
            "Mutual lists of civilian prisoners and fishermen verified and exchanged between foreign ministries.",
            "Reaffirmation of adherence to the bilateral Line of Control (LoC) ceasefire agreement.",
            "Agreement to expedite medical clearances for detained individuals qualifying for repatriation."
        ],
        divergences: [
            "The Hindu highlights institutional diplomacy, legal status under the Vienna Convention, and consular access.",
            "Indian Express investigates state-level border security apparatus, coast guard patrol logs, and maritime boundaries.",
            "NDTV focuses on humanitarian human-interest narratives of separated fishing families awaiting border return.",
            "Reuters contextualizes the dialogue within broader South Asian regional stability and multilateral summit sidelines."
        ],
        articles: [
            {
                id: "art-inp-hindu",
                publisher: "The Hindu",
                publisherDomain: "thehindu.com",
                title: "India, Pakistan Envoys Review Consular Access and Repatriation of Detained Fishermen",
                url: "https://www.thehindu.com/news/national/",
                publishedAt: "2026-10-27T09:00:00Z",
                sentiment: "neutral",
                credibilityScore: 0.94,
                riskTier: "Low Risk",
                headlineDivergence: "Institutional & Legal Diplomacy",
                narrativeFocus: "Detailed breakdown of Vienna Convention compliance, verified prisoner rosters, and bilateral judicial committees.",
                contentSnippet: "Senior diplomatic officials from India and Pakistan reviewed pending consular access cases in New Delhi, agreeing to accelerate judicial and medical verification procedures for detained fishermen.",
                dimensions: {
                    sentiment: 66,
                    bias: 95,
                    objectivity: 97,
                    readability: 70,
                    propaganda: 98,
                    headline_accuracy: 96,
                    source_credibility: 95,
                    content_quality: 96
                }
            },
            {
                id: "art-inp-ie",
                publisher: "The Indian Express",
                publisherDomain: "indianexpress.com",
                title: "LoC Ceasefire Holds as Border Officials Exchange Humanitarian Rosters in Scheduled Meet",
                url: "https://indianexpress.com/section/india/",
                publishedAt: "2026-10-27T09:45:00Z",
                sentiment: "neutral",
                credibilityScore: 0.92,
                riskTier: "Low Risk",
                headlineDivergence: "Border Security & Ceasefire Integrity",
                narrativeFocus: "Focuses on military commander hotline communication, zero civilian casualties along LoC, and maritime patrol lines.",
                contentSnippet: "Border management officials noted that the 2021 ceasefire understanding remains fully respected along the Line of Control, enabling constructive progress on bilateral humanitarian rosters.",
                dimensions: {
                    sentiment: 68,
                    bias: 91,
                    objectivity: 94,
                    readability: 75,
                    propaganda: 95,
                    headline_accuracy: 94,
                    source_credibility: 93,
                    content_quality: 92
                }
            },
            {
                id: "art-inp-reuters",
                publisher: "Reuters",
                publisherDomain: "reuters.com",
                title: "South Asian Neighbours Conclude Bilateral Humanitarian Protocol Review",
                url: "https://www.reuters.com/world/asia-pacific/",
                publishedAt: "2026-10-27T10:15:00Z",
                sentiment: "neutral",
                credibilityScore: 0.95,
                riskTier: "Low Risk",
                headlineDivergence: "Regional Stability & Geopolitical Summary",
                narrativeFocus: "Places the consular talks in the context of broader regional economic corridor discussions and international mediation.",
                contentSnippet: "India and Pakistan completed a routine exchange of civilian prisoner manifests under existing bilateral accords, affirming their commitment to maintain peace protocols along disputed frontier regions.",
                dimensions: {
                    sentiment: 70,
                    bias: 93,
                    objectivity: 96,
                    readability: 77,
                    propaganda: 97,
                    headline_accuracy: 96,
                    source_credibility: 96,
                    content_quality: 94
                }
            }
        ]
    },
    {
        id: "cluster-icc-trophy-2026",
        eventTitle: "ICC Champions Trophy 2026: Hybrid Multi-City Schedule Approved",
        category: "sports",
        consensusRate: 95,
        summary: "The International Cricket Council officially approved the hybrid staging model for the 2026 Champions Trophy, confirming match itineraries across designated neutral hubs with full security guarantees.",
        agreedFacts: [
            "ICC Executive Board unanimously ratified the hybrid hosting framework.",
            "All India matches and knockout games involving the Indian team will take place in neutral venues.",
            "Group stage matches for non-travelling pools will proceed across primary host stadiums.",
            "Broadcast revenue sharing and logistical insurance arrangements finalized between all member boards."
        ],
        divergences: [
            "ESPN Cricinfo provides ball-by-ball tournament fixture breakdown, pitch conditions, and squad travel itineraries.",
            "NDTV Sports highlights government clearance protocols, security delegation audits, and player logistics.",
            "The Indian Express investigates the financial negotiations between BCCI, PCB, and broadcast sponsors."
        ],
        articles: [
            {
                id: "art-icc-cricinfo",
                publisher: "ESPN Cricinfo",
                publisherDomain: "espncricinfo.com",
                title: "ICC Approves Champions Trophy Hybrid Schedule with Designated Neutral Match Hubs",
                url: "https://www.espncricinfo.com/",
                publishedAt: "2026-10-27T12:00:00Z",
                sentiment: "positive",
                credibilityScore: 0.94,
                riskTier: "Low Risk",
                headlineDivergence: "Fixture Operations & Tournament Format",
                narrativeFocus: "Focuses on match schedule dates, venue pitch preparation, and player recovery turnaround intervals.",
                contentSnippet: "The International Cricket Council announced the finalized schedule for the 2026 Champions Trophy, confirming a hybrid operational blueprint ensuring all qualified national teams participate without travel restrictions.",
                dimensions: {
                    sentiment: 78,
                    bias: 92,
                    objectivity: 96,
                    readability: 82,
                    propaganda: 96,
                    headline_accuracy: 97,
                    source_credibility: 94,
                    content_quality: 94
                }
            },
            {
                id: "art-icc-ndtv",
                publisher: "NDTV Sports",
                publisherDomain: "sports.ndtv.com",
                title: "Champions Trophy Schedule Confirmed: Hybrid Model Cleared Following BCCI Consultations",
                url: "https://sports.ndtv.com/cricket",
                publishedAt: "2026-10-27T12:40:00Z",
                sentiment: "positive",
                credibilityScore: 0.91,
                riskTier: "Low Risk",
                headlineDivergence: "Administrative & Government Clearance Angle",
                narrativeFocus: "Examines security advisory clearances issued by sporting ministries and diplomatic travel guidelines.",
                contentSnippet: "After weeks of high-level board discussions, cricket's governing body confirmed that India's games will take place at neutral venues, maintaining sporting parity while adhering to national security travel directives.",
                dimensions: {
                    sentiment: 75,
                    bias: 89,
                    objectivity: 92,
                    readability: 80,
                    propaganda: 94,
                    headline_accuracy: 93,
                    source_credibility: 91,
                    content_quality: 91
                }
            },
            {
                id: "art-icc-ie",
                publisher: "The Indian Express",
                publisherDomain: "indianexpress.com",
                title: "Behind the ICC Hybrid Model: How Board Negotiations Reached Revenue and Fixture Accord",
                url: "https://indianexpress.com/section/sports/cricket/",
                publishedAt: "2026-10-27T13:15:00Z",
                sentiment: "neutral",
                credibilityScore: 0.93,
                riskTier: "Low Risk",
                headlineDivergence: "Financial Governance & Revenue Mechanics",
                narrativeFocus: "Dissects sponsorship valuations, gate receipt compensations, and broadcast prime-time scheduling agreements.",
                contentSnippet: "The compromise agreement safeguards multi-million dollar broadcasting contracts while distributing supplementary venue compensation funds to primary host stadiums.",
                dimensions: {
                    sentiment: 70,
                    bias: 92,
                    objectivity: 94,
                    readability: 77,
                    propaganda: 95,
                    headline_accuracy: 95,
                    source_credibility: 93,
                    content_quality: 93
                }
            }
        ]
    },
    {
        id: "cluster-lunar-landing-2026",
        eventTitle: "Artemis Lunar South Pole Mission: Core Volatile Ice Extraction Confirmed",
        category: "general",
        consensusRate: 98,
        summary: "International space agencies confirmed that surface rover spectrometers in permanently shadowed lunar craters detected subsurface water-ice deposits with 99.4% spectral purity, marking a critical leap for in-situ lunar habitation.",
        agreedFacts: [
            "Subsurface water-ice volatiles identified within Shackleton crater rim permanently shadowed regions.",
            "Spectral purity confirmed via mass spectrometers operating aboard automated lunar rovers.",
            "Joint mission verified by NASA, ESA, ISRO, and JAXA ground telemetry stations.",
            "Extraction data lays baseline for oxygen and rocket fuel synthesis protocols."
        ],
        divergences: [
            "Nature Physics details Raman spectroscopy readings, isotopic ratios, and cryosphere physics.",
            "BBC Science focuses on the global human impact, in-situ water extraction, and future astronaut drinking supplies.",
            "Reuters examines space commercialization contracts, private launch partnerships, and patent filings."
        ],
        articles: [
            {
                id: "art-lunar-nature",
                publisher: "Nature",
                publisherDomain: "nature.com",
                title: "Spectroscopic Detection of Subsurface Water Ice Volatiles in Lunar Polar Regolith",
                url: "https://www.nature.com/nature/articles",
                publishedAt: "2026-10-27T08:00:00Z",
                sentiment: "positive",
                credibilityScore: 0.98,
                riskTier: "Low Risk",
                headlineDivergence: "Rigorous Peer-Reviewed Scientific Findings",
                narrativeFocus: "Presents mass spectroscopy isotope data, regolith mineral composition, and cryo-thermal stability models.",
                contentSnippet: "Direct measurements from deep-shadow drill penetrometers reveal high concentrations of preserved cryogenic water-ice volatiles at depths of 1.2 meters, corroborating orbital radar estimates.",
                dimensions: {
                    sentiment: 82,
                    bias: 97,
                    objectivity: 99,
                    readability: 60,
                    propaganda: 99,
                    headline_accuracy: 98,
                    source_credibility: 98,
                    content_quality: 98
                }
            },
            {
                id: "art-lunar-bbc",
                publisher: "BBC Science",
                publisherDomain: "bbc.com",
                title: "Lunar South Pole Rovers Confirm Abundant Water Ice in Permanently Shadowed Craters",
                url: "https://www.bbc.com/news/science_and_environment",
                publishedAt: "2026-10-27T08:45:00Z",
                sentiment: "positive",
                credibilityScore: 0.95,
                riskTier: "Low Risk",
                headlineDivergence: "Human Exploration & Future Habitation",
                narrativeFocus: "Highlights astronaut life support viability, sustainable lunar bases, and the global international space coalition.",
                contentSnippet: "Scientists celebrated a historic milestone as robotic drill probes confirmed deep reserves of pure water ice, paving the way for permanent human research stations on the Moon by the decade's end.",
                dimensions: {
                    sentiment: 84,
                    bias: 94,
                    objectivity: 96,
                    readability: 79,
                    propaganda: 97,
                    headline_accuracy: 96,
                    source_credibility: 96,
                    content_quality: 95
                }
            },
            {
                id: "art-lunar-reuters",
                publisher: "Reuters",
                publisherDomain: "reuters.com",
                title: "International Space Agencies Validate Lunar Ice Data for Long-Duration Moon Missions",
                url: "https://www.reuters.com/technology/space/",
                publishedAt: "2026-10-27T09:30:00Z",
                sentiment: "positive",
                credibilityScore: 0.96,
                riskTier: "Low Risk",
                headlineDivergence: "Commercial Supply Chain & Program Milestones",
                narrativeFocus: "Focuses on commercial payload launch timelines, aerospace supply contracts, and agency budgetary authorizations.",
                contentSnippet: "Space agency administrators confirmed that confirmed lunar ice extraction significantly reduces mission launch payload weights, cutting anticipated logistics costs for orbital resupply by an estimated 40 percent.",
                dimensions: {
                    sentiment: 78,
                    bias: 95,
                    objectivity: 97,
                    readability: 73,
                    propaganda: 98,
                    headline_accuracy: 97,
                    source_credibility: 96,
                    content_quality: 95
                }
            }
        ]
    }
];

/**
 * Retrieves matching story clusters filtered by query or category.
 */
export function getStoryClusters(query?: string, category?: string): StoryCluster[] {
    const q = (query || '').toLowerCase().trim();
    const cat = (category || '').toLowerCase().trim();

    return CURATED_STORY_CLUSTERS.filter(cluster => {
        // Category filter
        if (cat && cat !== 'all' && cluster.category !== cat) {
            return false;
        }

        // Search query filter
        if (q) {
            const matchesTitle = cluster.eventTitle.toLowerCase().includes(q);
            const matchesSummary = cluster.summary.toLowerCase().includes(q);
            const matchesArticles = cluster.articles.some(a =>
                a.title.toLowerCase().includes(q) ||
                a.publisher.toLowerCase().includes(q) ||
                a.narrativeFocus.toLowerCase().includes(q)
            );
            return matchesTitle || matchesSummary || matchesArticles;
        }

        return true;
    });
}
