import { NewsArticle } from './sampleArticles';

export const REAL_WORLD_FAKE_NEWS: NewsArticle[] = [
    {
        id: "fake-001",
        title: "NASA Confirms Total Darkness on Earth for 6 Consecutive Days Due to Solar Eclipse Storm",
        source_domain: "Viral Tabloid Hoax (Fact-Checked)",
        source_url: "https://www.snopes.com/fact-check/solar-storm-six-days-darkness/",
        content_summary: "A circulating internet report claimed NASA issued an emergency bulletin warning the entire planet would plunge into total darkness for six days due to an unprecedented solar dust storm.",
        ai_summary: "Viral posts claiming NASA confirmed six days of total global darkness are a recurring online hoax. NASA officials confirmed no such phenomenon is possible and no warning was issued.",
        category: "general",
        sentiment: "negative",
        is_fake: true,
        credibility_score: 0.12,
        risk_score: 0.88,
        confidence_level: 0.96,
        credibility_label: "High Risk",
        needs_verification: false,
        ai_reasoning: "Flagged as high-risk disinformation. Contains astronomical impossibilities, alarmist apocalyptic triggers, and has been formally debunked by NASA and independent fact-checkers.",
        dimensions: {
            sentiment: 15,
            bias: 12,
            objectivity: 14,
            readability: 46,
            propaganda: 8,
            headline_accuracy: 10,
            source_credibility: 15,
            content_quality: 20,
            explanations: {
                sentiment: "Extreme panic-inducing apocalyptic emotional framing.",
                bias: "Sensationalist fabrication designed to generate viral social media terror.",
                objectivity: "Zero empirical astronomical evidence or scientific telemetry.",
                readability: "Flesch Reading Ease: 46.2 (Disjointed, sensationalized vocabulary).",
                propaganda: "Severe panic propaganda and false authority impersonation.",
                headline_accuracy: "Headline fabricates an official NASA bulletin that never existed.",
                source_credibility: "Fringe clickbait blog impersonating official space agencies.",
                content_quality: "Completely fictitious claims lacking scientific review."
            }
        },
        group_id: "cluster-nasa-darkness-hoax",
        event_title: "Debunked NASA 6-Day Darkness Hoax",
        published_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString()
    },
    {
        id: "fake-002",
        title: "UNESCO Declares India's 'Jana Gana Mana' as the Best National Anthem in the World",
        source_domain: "WhatsApp Viral Chain (Fact-Checked)",
        source_url: "https://www.thehindu.com/",
        content_summary: "A viral message forwarded across messaging platforms claims that UNESCO's General Conference officially voted the Indian national anthem as the 'Best Anthem in the World'.",
        ai_summary: "Viral messages claiming UNESCO ranked India's national anthem as the world's best are false. UNESCO has repeatedly confirmed it does not judge, evaluate, or rank national anthems.",
        category: "politics",
        sentiment: "positive",
        is_fake: true,
        credibility_score: 0.15,
        risk_score: 0.85,
        confidence_level: 0.94,
        credibility_label: "High Risk",
        needs_verification: false,
        ai_reasoning: "Classic nationalistic chain-message hoax. UNESCO has officially issued formal clarifications confirming they do not hold any national anthem contests.",
        dimensions: {
            sentiment: 72,
            bias: 18,
            objectivity: 16,
            readability: 60,
            propaganda: 14,
            headline_accuracy: 12,
            source_credibility: 18,
            content_quality: 24,
            explanations: {
                sentiment: "Flattering nationalistic celebratory tone engineered for emotional forwards.",
                bias: "Exploits patriotic sentiment without verified institutional protocol.",
                objectivity: "Lacks any verifiable UNESCO session records or voting data.",
                readability: "Flesch Reading Ease: 60.5 (Typical viral chain email format).",
                propaganda: "Social engineering appeal to authority using false UNESCO attribution.",
                headline_accuracy: "Headline asserts a non-existent diplomatic award.",
                source_credibility: "Unverified messaging chains and aggregator message boards.",
                content_quality: "Repetitive assertion unsupported by official UN documentation."
            }
        },
        group_id: "cluster-unesco-anthem-hoax",
        event_title: "Debunked UNESCO National Anthem Claim",
        published_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 25 * 60 * 1000).toISOString()
    },
    {
        id: "fake-003",
        title: "RBI Declares Rs 500 Currency Notes with Star (*) Symbol as Counterfeit and Invalid Overnight",
        source_domain: "Social Media Rumor (Fact-Checked)",
        source_url: "https://www.rbi.org.in/",
        content_summary: "Messages circulating on social media urged citizens to reject 500-rupee notes that have a star symbol between the prefix and serial number, alleging banks were refusing them.",
        ai_summary: "The Reserve Bank of India confirmed that 500-rupee notes with a star (*) symbol are completely genuine legal tender, issued as replacement notes in a packet.",
        category: "business",
        sentiment: "negative",
        is_fake: true,
        credibility_score: 0.11,
        risk_score: 0.89,
        confidence_level: 0.97,
        credibility_label: "High Risk",
        needs_verification: false,
        ai_reasoning: "Financial disinformation causing unnecessary market friction. Officially refuted by the Reserve Bank of India and PIB Fact Check.",
        dimensions: {
            sentiment: 20,
            bias: 12,
            objectivity: 15,
            readability: 54,
            propaganda: 9,
            headline_accuracy: 10,
            source_credibility: 14,
            content_quality: 22,
            explanations: {
                sentiment: "High financial panic and fear of economic loss.",
                bias: "Unfounded alarmist bias aimed at causing public distress.",
                objectivity: "Contradicted directly by official RBI Master Circulars.",
                readability: "Flesch Reading Ease: 54.1 (Sensational financial rumor text).",
                propaganda: "Severe economic disruption propaganda encouraging rejection of valid currency.",
                headline_accuracy: "Headline directly inverts monetary policy facts.",
                source_credibility: "Anonymous social media viral forwards.",
                content_quality: "Short emotional warning without central bank citation."
            }
        },
        group_id: "cluster-rbi-star-notes-hoax",
        event_title: "Debunked RBI 500 Rupee Star Symbol Note Rumor",
        published_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString()
    },
    {
        id: "fake-004",
        title: "Elon Musk Unveils Automated Quantum AI Trading Platform Guaranteeing Daily 300% Returns",
        source_domain: "Deepfake Video Ad (Fact-Checked)",
        source_url: "https://www.reuters.com/fact-check/",
        content_summary: "A widely sponsored social media advertisement featured synthetic video of Elon Musk claiming a government-partnered quantum algorithm would generate guaranteed daily profits for every citizen.",
        ai_summary: "Investigators verified that videos of Elon Musk announcing guaranteed 300% daily trading software were AI-manipulated deepfakes designed to divert money to fraudulent wallets.",
        category: "business",
        sentiment: "positive",
        is_fake: true,
        credibility_score: 0.08,
        risk_score: 0.92,
        confidence_level: 0.98,
        credibility_label: "High Risk",
        needs_verification: false,
        ai_reasoning: "Fraudulent cryptocurrency advance-fee investment scheme using generative AI voice cloning and lip-sync manipulation.",
        dimensions: {
            sentiment: 78,
            bias: 10,
            objectivity: 12,
            readability: 58,
            propaganda: 6,
            headline_accuracy: 8,
            source_credibility: 10,
            content_quality: 18,
            explanations: {
                sentiment: "Hyper-optimistic promotional framing promising unrealistic financial gain.",
                bias: "Deceptive commercial solicitation targeting vulnerable investors.",
                objectivity: "Completely lacks SEC/FCA registration or verifiable corporate balance sheets.",
                readability: "Flesch Reading Ease: 58.0 (Promotional marketing copy).",
                propaganda: "Maximum propaganda marker: deepfake impersonation of high-profile executive.",
                headline_accuracy: "Headline promises non-existent guaranteed investment returns.",
                source_credibility: "Phishing landing page with spoofed news branding.",
                content_quality: "Fragmentary scam landing page structure."
            }
        },
        group_id: "cluster-quantum-ai-deepfake-scam",
        event_title: "Deepfake AI Elon Musk Quantum Investment Scam",
        published_at: new Date(Date.now() - 40 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 40 * 60 * 1000).toISOString()
    },
    {
        id: "fake-005",
        title: "Secret Lab Study Links 5G Mobile Radiation Frequencies Directly to Respiratory Cellular Degradation",
        source_domain: "Conspiracy Blog (Fact-Checked)",
        source_url: "https://www.who.int/news-room/questions-and-answers/item/radiation-5g-mobile-networks-and-health",
        content_summary: "An unvetted blog post claimed classified laboratory tests proved 5G millimeter-wave radio frequencies interfere with oxygen absorption in human lung cells.",
        ai_summary: "Medical bodies and the World Health Organization confirmed that extensive peer-reviewed scientific studies show no link between 5G radio waves and respiratory illness.",
        category: "technology",
        sentiment: "negative",
        is_fake: true,
        credibility_score: 0.14,
        risk_score: 0.86,
        confidence_level: 0.95,
        credibility_label: "High Risk",
        needs_verification: false,
        ai_reasoning: "Pseudoscience conspiracy narrative violating basic biophysical laws. Refuted by WHO, FDA, and IEEE engineering guidelines.",
        dimensions: {
            sentiment: 16,
            bias: 14,
            objectivity: 15,
            readability: 50,
            propaganda: 11,
            headline_accuracy: 12,
            source_credibility: 12,
            content_quality: 20,
            explanations: {
                sentiment: "Fear-driven medical panic narrative.",
                bias: "Anti-technology conspiracy framing without empirical controls.",
                objectivity: "Zero peer-reviewed citations, double-blind trials, or institutional authors.",
                readability: "Flesch Reading Ease: 50.4 (Dense pseudo-scientific jargon).",
                propaganda: "Exploits public health anxieties to drive conspiracy subscription traffic.",
                headline_accuracy: "Headline asserts dangerous medical causal link refuted by science.",
                source_credibility: "Fringe conspiracy website with hidden whois registration.",
                content_quality: "Uncorroborated assertions masquerading as clinical research."
            }
        },
        group_id: "cluster-5g-health-conspiracy",
        event_title: "Debunked 5G Radiation Respiratory Health Hoax",
        published_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
    },
    {
        id: "fake-006",
        title: "ICC Convenes Emergency Hearing to Strip Team of Championship Trophy After Secret Ball Alteration Leaked",
        source_domain: "Tabloid Sports Leak (Fact-Checked)",
        source_url: "https://www.icc-cricket.com/",
        content_summary: "A sensationalized sports blog alleged match officials had filed secret reports accusing a tournament finalist of systematic ball-tampering, triggering immediate disqualification proceedings.",
        ai_summary: "The International Cricket Council confirmed no match officials reported irregularities and dismissed viral allegations of ball tampering as completely fabricated.",
        category: "sports",
        sentiment: "negative",
        is_fake: true,
        credibility_score: 0.19,
        risk_score: 0.81,
        confidence_level: 0.93,
        credibility_label: "High Risk",
        needs_verification: false,
        ai_reasoning: "Baseless sports controversy engineered for click monetization. Match referees and governing bodies formally confirmed the match conformed to all ICC standards.",
        dimensions: {
            sentiment: 24,
            bias: 15,
            objectivity: 19,
            readability: 68,
            propaganda: 12,
            headline_accuracy: 14,
            source_credibility: 18,
            content_quality: 25,
            explanations: {
                sentiment: "High controversy and outrage targeting sports fandoms.",
                bias: "Partisan speculation aimed at discrediting competitive outcomes.",
                objectivity: "Refuted by official match referee umpire reports and ICC statements.",
                readability: "Flesch Reading Ease: 68.2 (Sensational sports tabloid style).",
                propaganda: "Clickbait framing exploiting fan emotions and team rivalries.",
                headline_accuracy: "Headline fabricates an emergency disciplinary hearing that never happened.",
                source_credibility: "Unaccredited sports click-farm blog.",
                content_quality: "Pure speculation devoid of on-record quotes."
            }
        },
        group_id: "cluster-icc-tampering-hoax",
        event_title: "Debunked Cricket Championship Tampering Hoax",
        published_at: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 20 * 60 * 1000).toISOString()
    }
];

export const REAL_WORLD_UNCERTAIN_NEWS: NewsArticle[] = [
    {
        id: "unver-001",
        title: "Leaked Internal Memo Hints at Massive Regional Telecom Carrier Consolidation",
        source_domain: "Trade Insider Leak",
        source_url: "https://www.reuters.com/business/",
        content_summary: "An unconfirmed one-page slide deck circulating on social media suggests two regional carriers are considering an all-stock merger. Executives from both companies declined to comment on the speculation.",
        ai_summary: "An anonymous one-page slide deck surfaced online suggesting potential merger talks between regional telecom carriers. Both entities currently decline to verify or refute the rumor.",
        category: "business",
        sentiment: "neutral",
        is_fake: false,
        credibility_score: 0.52,
        risk_score: 0.48,
        confidence_level: 0.51,
        credibility_label: "Moderate Risk",
        needs_verification: true,
        ai_reasoning: "Single unconfirmed source with neutral editorial tone; confidence is near the 50% boundary and requires verification.",
        dimensions: {
            sentiment: 50,
            bias: 65,
            objectivity: 58,
            readability: 70,
            propaganda: 75,
            headline_accuracy: 72,
            source_credibility: 55,
            content_quality: 60,
            explanations: {
                sentiment: "Neutral commercial speculation without affective polarity.",
                bias: "Moderate risk due to reliance on uncorroborated single-source leak.",
                objectivity: "Transparently identifies claim as unconfirmed and notes company refusal to verify.",
                readability: "Flesch Reading Ease: 71.0 (Brisk business reporting).",
                propaganda: "Mild sensationalism around 'leaked' keyword but maintains conditional verbs.",
                headline_accuracy: "Headline uses hedging language ('hints at') matching the unproven content.",
                source_credibility: "Niche trade blog without primary document verification.",
                content_quality: "Brief article with under 150 words of primary substance."
            }
        },
        published_at: new Date(Date.now() - 18 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 18 * 60 * 1000).toISOString()
    }
];

export function getMatchingFakeNews(query?: string, category?: string): NewsArticle[] {
    let list = [...REAL_WORLD_FAKE_NEWS];
    const cat = category && category.toLowerCase() !== 'all' ? category.toLowerCase() : '';

    if (cat) {
        list = list.filter(a => a.category.toLowerCase() === cat);
    }

    if (query && query.trim()) {
        const q = query.trim().toLowerCase();
        const matched = list.filter(a =>
            a.title.toLowerCase().includes(q) ||
            a.content_summary.toLowerCase().includes(q) ||
            a.ai_summary.toLowerCase().includes(q)
        );
        return matched;
    }

    return list;
}

export function getMatchingUncertainNews(query?: string, category?: string): NewsArticle[] {
    let list = [...REAL_WORLD_UNCERTAIN_NEWS];
    const cat = category && category.toLowerCase() !== 'all' ? category.toLowerCase() : '';

    if (cat) {
        list = list.filter(a => a.category.toLowerCase() === cat);
    }

    if (query && query.trim()) {
        const q = query.trim().toLowerCase();
        const matched = list.filter(a =>
            a.title.toLowerCase().includes(q) ||
            a.content_summary.toLowerCase().includes(q) ||
            a.ai_summary.toLowerCase().includes(q)
        );
        return matched;
    }

    return list;
}
