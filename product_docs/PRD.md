# NexusReach — Product Requirements Document

**Version:** 1.1
**Author:** SingularRarity Labs
**Status:** Approved for Development
**Last Updated:** March 2026

---

## 1. Executive Summary

The influencer marketing industry in India is growing rapidly, yet the tooling available to brands and creators remains fragmented, opaque, and expensive. NexusReach is an AI-powered influencer-brand intelligence platform that closes this gap — enabling data-driven discovery, verified credibility, and transparent campaign execution across major cities in India.

Unlike incumbent platforms (Winkl, Plixxo) that rely on self-reported metrics and opaque matching algorithms, NexusReach delivers verified social analytics, geo-intelligent discovery, and LLM-powered brand-influencer pairing — all within a single, audit-friendly workflow.

---

## 2. Problem Statement

Brands operating across major cities in India have no efficient, trustworthy way to discover, vet, and activate micro-influencers at scale. Simultaneously, micro-influencers lack the structured tooling to present verified metrics, manage incoming proposals, or track earnings transparently.

**Core pain points:**

| Stakeholder | Pain Point |
|---|---|
| Brand Manager | Manual influencer discovery is slow; engagement metrics are unverified; ROI attribution is near-impossible |
| Micro-Influencer | No single verified profile; deal proposals arrive through informal channels; no pipeline visibility |
| Agency / Media Buyer | Managing multiple brand campaigns across influencers requires disparate spreadsheets and fragile processes |

Existing platforms compound these problems with high subscription fees, black-box matching logic, and no geographic intelligence layer.

---

## 3. Target Users

| Persona | Description | Primary Job-to-be-Done |
|---|---|---|
| Brand Manager | Marketing lead at a D2C, FMCG, or lifestyle brand | Find the right influencers for a campaign brief, fast |
| Micro-Influencer | Creator with 5K–200K followers on Instagram, YouTube, or Moj | Build a verified profile and receive qualified deal proposals |
| Agency / Media Buyer | Manages 5–20 brand accounts simultaneously | Run multiple influencer campaigns from a single dashboard |

---

## 4. Core Features — MVP Scope

| Feature | Description | Priority |
|---|---|---|
| Influencer Profile | Verified social metrics (pulled via OAuth), niche taxonomy tags, geo-location (city-level) | P0 |
| Brand Discovery Feed | Browse and filter influencers by reach, city, content category, engagement rate | P0 |
| AI Match Engine | Score-based brand ↔ influencer pairing using LLM embeddings and cosine similarity | P0 |
| Campaign Manager | Create campaign briefs, assign shortlisted influencers, track proposal → active → completed lifecycle | P1 |
| Analytics Dashboard | Impressions, cost-per-engagement (CPE), ROI estimator, campaign-level performance rollup | P1 |
| Geo Heatmap | Influencer density visualization across major cities in India — Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Pune, Kolkata | P1 |
| Real-time Notifications | Deal alerts and campaign status updates delivered via WebSocket | P2 |
| Export Reports | PDF and CSV campaign reports formatted for brand stakeholder reviews | P2 |

---

## 5. Out of Scope — v1

- Payment processing or escrow functionality
- Native mobile application (iOS / Android)
- Influencer content scheduling or direct publishing
- Multi-country expansion (India-only for v1; international expansion is v2 roadmap)
- Influencer content performance tracking beyond campaign window

---

## 6. User Stories

### Influencer

- As an influencer, I can create a verified profile with my niche, city, and social handles so that qualified brands can discover me.
- As an influencer, I can view incoming deal proposals with campaign brief details and accept or decline them from a single inbox.
- As an influencer, I can review my full campaign history, current active engagements, and estimated earnings at a glance.

### Brand

- As a brand manager, I can write a campaign brief in plain language and receive AI-matched influencer recommendations ranked by fit score.
- As a brand, I can filter the influencer pool by city (across major metros), content category, follower band, and minimum engagement rate.
- As a brand, I can track the real-time status of every influencer in an active campaign — from proposal sent through to completion.
- As a brand, I can export a formatted PDF analytics report to share campaign ROI with internal stakeholders.

### Admin

- As an admin, I can review pending influencer profile submissions, verify social metric accuracy, and approve or reject profiles.
- As an admin, I can monitor platform-wide health metrics — active campaigns, match engine latency, error rates — via an internal operations dashboard.

---

## 7. Success Metrics

| Metric | Target (60 Days Post-Launch) |
|---|---|
| Verified influencer profiles onboarded | 200+ |
| Brand accounts with at least one active campaign | 50+ |
| AI match score accuracy (user-rated as relevant) | > 75% |
| Average campaign creation time (brief to first match) | < 5 minutes |
| WebSocket notification delivery latency | < 500ms p95 |
| Platform uptime | ≥ 99.5% |

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | All read API endpoints must respond in < 200ms at p95 under normal load |
| **Scalability** | Stateless backend horizontally scalable behind a load balancer; no session state in application tier |
| **Security** | All PII encrypted at rest; OAuth2-only authentication; zero password storage; JWT refresh rotation via Redis blacklist |
| **Availability** | 99.5% monthly uptime SLA on Railway managed infrastructure |
| **Observability** | Structured JSON logging via `structlog`; distributed tracing via OpenTelemetry; error tracking via Sentry with full request context |
| **Compliance** | DPDP Act (India) compliant data handling; opt-in consent flows for social data ingestion |

---

## 9. Geographic Scope

**v1 Target Cities (India):**

| Tier | Cities |
|---|---|
| Tier 1 | Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Pune, Kolkata |
| Tier 2 (onboarding) | Ahmedabad, Jaipur, Surat, Lucknow, Chandigarh |

The geo heatmap visualization will render influencer density across all supported cities, with city-level drill-down for brand discovery filtering. Geographic expansion beyond India is scoped to v2.

---

## 10. Milestones

| Phase | Deliverable | Duration |
|---|---|---|
| 1 | Foundation — Docker environment, PostgreSQL + pgvector, authentication | Week 1 |
| 2 | Core data models, CRUD APIs, cursor-based pagination | Week 2 |
| 3 | AI Match Engine — LangChain embeddings, pgvector cosine similarity | Week 3 |
| 4 | Analytics CQRS layer + Celery aggregation workers | Week 4 |
| 5 | Frontend UI — Discovery feed, Campaign Manager, Geo Heatmap | Week 5 |
| 6 | WebSocket real-time notifications + PDF/CSV export | Week 6 |
| 7 | End-to-end testing, CI/CD pipeline, production deployment | Week 7 |

---

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Social platform API rate limits throttle metric verification | Medium | High | Cache verified metrics with 24h TTL; implement exponential backoff on API calls |
| AI match quality perceived as low by early users | Medium | High | Collect user feedback signals (thumbs up/down) from Day 1; retrain embeddings post-MVP |
| Influencer cold-start problem (sparse profiles at launch) | High | Medium | Seed platform with manually curated profiles during Week 1 onboarding sprint |
| DPDP Act compliance scope unclear at launch | Low | High | Engage legal counsel pre-launch; implement consent flows for all social data ingestion |

---

*NexusReach — where data-driven creator economy meets geo-intelligent brand activation.*
