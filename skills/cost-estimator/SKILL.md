---
name: cost-estimator
description: Infrastructure and development cost estimation for technical projects. Use when planning budgets, evaluating build vs buy decisions, or projecting TCO for architecture choices.
---

# Cost Estimator

Provides frameworks for estimating infrastructure costs, development effort, and total cost of ownership (TCO) for technical projects.

## When to Use

- Planning infrastructure budgets
- Evaluating build vs. buy decisions
- Projecting costs at different scale points
- Comparing technology options by cost
- Creating business cases for technical investments

## Cost Categories

### Total Cost of Ownership (TCO)

```
TCO = Infrastructure + Development + Operations + Opportunity Cost

┌─────────────────────────────────────────────────────────────────┐
│                    TOTAL COST OF OWNERSHIP                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Infrastructure    Development    Operations    Opportunity      │
│  ────────────────  ────────────   ──────────    ────────────     │
│  • Compute         • Engineering  • Support     • What else      │
│  • Storage         • QA           • Monitoring  • could team     │
│  • Network         • DevOps       • On-call     • be building?   │
│  • Third-party     • Management   • Training                     │
│    APIs/SaaS       • Contractors  • Incidents                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Infrastructure Cost Reference

### Cloud Compute Pricing (2024-2025)

#### AWS EC2 On-Demand (US regions)

| Instance | vCPU | RAM | Monthly Cost | Best For |
|----------|------|-----|--------------|----------|
| t3.micro | 2 | 1GB | 8 USD | Dev/test |
| t3.medium | 2 | 4GB | 30 USD | Small apps |
| t3.large | 2 | 8GB | 60 USD | Light production |
| m6i.large | 2 | 8GB | 70 USD | General production |
| m6i.xlarge | 4 | 16GB | 140 USD | Medium workloads |
| m6i.2xlarge | 8 | 32GB | 280 USD | Heavy workloads |
| c6i.2xlarge | 8 | 16GB | 250 USD | CPU-intensive |
| r6i.2xlarge | 8 | 64GB | 370 USD | Memory-intensive |

#### GPU Instances

| Instance | GPU | VRAM | Monthly Cost | Best For |
|----------|-----|------|--------------|----------|
| g4dn.xlarge | T4 | 16GB | 380 USD | Inference |
| g5.xlarge | A10G | 24GB | 730 USD | ML training/inference |
| p4d.24xlarge | 8x A100 | 320GB | 23,000 USD | Large model training |

#### Savings Options

| Plan | Savings | Commitment |
|------|---------|------------|
| On-Demand | 0% | None |
| Reserved (1yr) | 30-40% | 1 year |
| Reserved (3yr) | 50-60% | 3 years |
| Spot Instances | 60-90% | Can be interrupted |

### Database Pricing

#### Managed Database (AWS RDS PostgreSQL)

| Instance | vCPU | RAM | Monthly Cost | Connections |
|----------|------|-----|--------------|-------------|
| db.t3.micro | 2 | 1GB | 15 USD | 50 |
| db.t3.medium | 2 | 4GB | 50 USD | 100 |
| db.m6g.large | 2 | 8GB | 120 USD | 200 |
| db.m6g.xlarge | 4 | 16GB | 240 USD | 400 |
| db.r6g.xlarge | 4 | 32GB | 350 USD | 500 |
| db.r6g.2xlarge | 8 | 64GB | 700 USD | 1000 |

**Add for storage**: 0.115 USD/GB/month (gp3)
**Add for IOPS**: 0.02 USD/IOPS/month (over 3000 baseline)

#### Redis/ElastiCache

| Node Type | RAM | Monthly Cost |
|-----------|-----|--------------|
| cache.t3.micro | 0.5GB | 12 USD |
| cache.t3.medium | 3GB | 50 USD |
| cache.m6g.large | 6.4GB | 100 USD |
| cache.r6g.large | 13GB | 175 USD |

### Storage Pricing

| Service | Cost | Use Case |
|---------|------|----------|
| S3 Standard | 0.023 USD/GB | Frequently accessed |
| S3 Infrequent | 0.0125 USD/GB | Backups, archives |
| S3 Glacier | 0.004 USD/GB | Long-term archive |
| EBS gp3 | 0.08 USD/GB | Block storage |
| EBS io2 | 0.125 USD/GB + IOPS | High performance |

### Network Costs (Often Overlooked!)

| Traffic Type | Cost |
|--------------|------|
| Data IN | Free |
| Data OUT (first 10TB) | 0.09 USD/GB |
| Data OUT (next 40TB) | 0.085 USD/GB |
| Inter-AZ transfer | 0.01 USD/GB each way |
| Inter-region transfer | 0.02 USD/GB |
| CloudFront to internet | 0.085 USD/GB |

---

## Development Cost Estimation

### Engineering Cost Framework

```
Development Cost = (Hours × Hourly Rate) × Complexity Factor × Risk Buffer

Hourly Rate (Fully Loaded):
- Junior Engineer: 75-100 USD/hr
- Mid-level Engineer: 100-150 USD/hr
- Senior Engineer: 150-200 USD/hr
- Staff/Principal: 200-300 USD/hr

Complexity Factors:
- Greenfield, known tech: 1.0x
- Existing codebase, known tech: 1.2x
- New technology for team: 1.5x
- Complex integrations: 1.3x
- Regulatory/compliance: 1.4x

Risk Buffer:
- Well-defined requirements: 1.2x
- Ambiguous requirements: 1.5x
- Experimental/R&D: 2.0x
```

### Story Point to Cost Mapping

| Size | Story Points | Hours | Cost (Mid-level) |
|------|-------------|-------|------------------|
| XS | 1 | 2-4 | 200-400 USD |
| S | 2 | 4-8 | 400-800 USD |
| M | 3 | 8-16 | 800-1,600 USD |
| L | 5 | 16-32 | 1,600-3,200 USD |
| XL | 8 | 32-64 | 3,200-6,400 USD |
| XXL | 13+ | 64+ | 6,400+ USD |

### Team Cost Calculator

```markdown
## Monthly Team Cost

Engineering Team:
- 2 Senior Engineers × 15,000 USD = 30,000 USD
- 3 Mid-level Engineers × 10,000 USD = 30,000 USD
- 1 Engineering Manager × 18,000 USD = 18,000 USD

Overhead (benefits, tools, etc.): 30%
Monthly Burn: (78,000 USD) × 1.3 = 101,400 USD

Annual Team Cost: ~1.2M USD
```

---

## Build vs. Buy Analysis

### Decision Framework

```
Build vs Buy Decision Matrix:

                    LOW Differentiation    HIGH Differentiation
                   ┌────────────────────┬────────────────────┐
    HIGH Volume/   │                    │                    │
    Usage          │     Consider       │       BUILD        │
                   │      Build         │    (competitive    │
                   │   (cost savings)   │     advantage)     │
                   ├────────────────────┼────────────────────┤
    LOW Volume/    │                    │                    │
    Usage          │       BUY          │       BUY          │
                   │   (no question)    │  (then consider    │
                   │                    │   build if scales) │
                   └────────────────────┴────────────────────┘
```

### TCO Comparison Template

```markdown
## Option A: Build Custom Solution

### Initial Development
- Engineering time: X months × $Y/month = $Z
- Infrastructure setup: $A

### Ongoing Costs (Annual)
- Infrastructure: $B
- Maintenance (20% of dev time): $C
- On-call/support: $D

### 3-Year TCO
Year 1: $Z + $A + $B + $C + $D
Year 2: $B + $C + $D
Year 3: $B + $C + $D
Total: $XXX

---

## Option B: Buy SaaS Solution

### Initial Costs
- Implementation/integration: $X
- Training: $Y

### Ongoing Costs (Annual)
- License fees: $Z/year
- Per-user costs: $A × users
- API costs: $B

### 3-Year TCO
Year 1: $X + $Y + $Z + $A + $B
Year 2: $Z + $A + $B
Year 3: $Z + $A + $B
Total: $XXX
```

### Common Build vs Buy Scenarios

| Capability | Build When | Buy When |
|------------|------------|----------|
| **Authentication** | Unique security requirements | Standard OAuth/OIDC works |
| **Payments** | Core business differentiator | Standard e-commerce |
| **Search** | Domain-specific relevance | Generic search needs |
| **Analytics** | Proprietary insights needed | Standard dashboards work |
| **Email** | High volume, custom delivery | Standard transactional |
| **ML/AI** | Proprietary models needed | Pre-trained models work |

---

## Cost Projection by Scale

### SaaS Application Cost Model

| Scale | Users | Monthly Infra | Notes |
|-------|-------|---------------|-------|
| **Startup** | 0-1K | 200-500 USD | Single server, managed DB |
| **Growth** | 1K-10K | 500-2,000 USD | Load balancer, caching |
| **Scale** | 10K-100K | 2,000-10,000 USD | Horizontal scaling |
| **Enterprise** | 100K-1M | 10,000-50,000 USD | Multi-region, HA |
| **Large** | 1M+ | 50,000+ USD | Global, custom CDN |

### Cost Per User Benchmarks

| Application Type | Cost/User/Month | Notes |
|------------------|-----------------|-------|
| Simple web app | 0.05-0.20 USD | Static + API |
| Data-intensive | 0.20-0.50 USD | Analytics, storage |
| Real-time | 0.50-2.00 USD | WebSockets, streaming |
| ML-powered | 1.00-5.00 USD | Inference costs |
| Video/media | 2.00-10.00 USD | Transcoding, CDN |

### E-commerce Cost Model

```markdown
## Monthly Infrastructure Cost by GMV

0-100K USD GMV/month:
- Basic infrastructure: 500 USD
- Payment processing (2.9%): ~2,000 USD
- Total: ~2,500 USD

100K-1M USD GMV/month:
- Scaled infrastructure: 2,000 USD
- Payment processing: ~20,000 USD
- Fraud protection: 500 USD
- Total: ~22,500 USD

1M-10M USD GMV/month:
- HA infrastructure: 10,000 USD
- Payment processing: ~200,000 USD
- Fraud/security: 5,000 USD
- CDN/performance: 3,000 USD
- Total: ~218,000 USD
```

---

## Hidden Cost Checklist

### Often Missed in Estimates

**Infrastructure**:
- [ ] Data transfer costs (egress)
- [ ] Backup storage
- [ ] Log storage (CloudWatch: 0.50 USD/GB)
- [ ] SSL certificates
- [ ] DNS queries
- [ ] Load balancer hours

**Development**:
- [ ] Code reviews (add 20-30% to dev time)
- [ ] Documentation
- [ ] Testing infrastructure
- [ ] CI/CD pipeline (GitHub Actions: 0.008 USD/min)
- [ ] Staging environments

**Operations**:
- [ ] Monitoring tools (Datadog: ~15 USD/host/month)
- [ ] Error tracking (Sentry: 26+ USD/month)
- [ ] Log management
- [ ] On-call compensation
- [ ] Incident response time

**Third-Party Services**:
- [ ] Email (SendGrid: 0.00025-0.001 USD/email)
- [ ] SMS (Twilio: 0.0075 USD/message)
- [ ] Video (encoding, streaming)
- [ ] Maps/geocoding (Google: 7 USD/1K requests)

---

## Cost Optimization Strategies

### Quick Wins

| Strategy | Savings | Effort |
|----------|---------|--------|
| Reserved instances | 30-60% | Low |
| Right-sizing instances | 20-40% | Medium |
| Spot instances (non-critical) | 60-90% | Medium |
| Storage tiering | 50-80% | Low |
| CDN caching | 30-50% bandwidth | Low |

### Architecture Optimizations

| Optimization | Impact | Complexity |
|--------------|--------|------------|
| Caching (Redis) | 50-80% DB load reduction | Medium |
| Queue-based processing | Smooth traffic spikes | Medium |
| Auto-scaling | Pay for what you use | Medium |
| Serverless (appropriate use) | Variable → zero when idle | High |
| Multi-region read replicas | Reduce cross-region costs | High |

---

## Cost Estimation Templates

### Project Budget Template

```markdown
# Project: [Name]
# Duration: [X months]

## Development Costs

| Phase | Duration | Team Size | Cost |
|-------|----------|-----------|------|
| Discovery/Design | 2 weeks | 2 | $X |
| MVP Development | 8 weeks | 4 | $X |
| Testing/QA | 2 weeks | 3 | $X |
| Deployment | 1 week | 2 | $X |
| **Total Development** | | | **$X** |

## Infrastructure Costs (First Year)

| Component | Monthly | Annual |
|-----------|---------|--------|
| Compute | $X | $X |
| Database | $X | $X |
| Storage | $X | $X |
| Network | $X | $X |
| Third-party APIs | $X | $X |
| Monitoring/Tools | $X | $X |
| **Total Infrastructure** | **$X** | **$X** |

## Ongoing Costs (Annual)

| Category | Cost |
|----------|------|
| Infrastructure | $X |
| Maintenance (20% of dev) | $X |
| Support/On-call | $X |
| Tool licenses | $X |
| **Total Annual** | **$X** |

## Summary

| Metric | Value |
|--------|-------|
| Total First Year | $X |
| Annual Run Rate | $X |
| 3-Year TCO | $X |
| Cost per User (at scale) | $X |
```

### Quick Estimate Calculator

```markdown
## Quick Infrastructure Estimate

Inputs:
- Expected users: [X]
- Requests per user/day: [Y]
- Data storage per user: [Z GB]
- Growth rate: [W%/month]

Calculations:
- Daily requests: X × Y
- Monthly requests: Daily × 30
- Required compute: (Monthly requests / 100K) × 50 USD
- Storage: X × Z × 0.10 USD
- Database: (X / 10K) × 200 USD
- Estimated monthly: Compute + Storage + Database × 1.3

12-month projection with growth:
Sum of (Monthly × (1 + W%)^month) for months 1-12
```

