## Overview
Deploy the MRC Runs Django application to Oracle Cloud Infrastructure (OCI) Always Free tier with a production-ready setup including PostgreSQL database, automated GitHub Actions CI/CD pipeline, and proper security configurations.

## Description
Currently, the application runs only in local development. This issue covers complete production deployment to OCI's Always Free tier, which provides permanent free compute and storage resources perfect for small-to-medium Django applications.

OCI's Always Free tier offers generous resources that will never expire, making it ideal for hosting this application at zero ongoing cost.

## Business Value
- **Zero Cost Hosting**: Permanent free tier (not time-limited trial)
- **Production Ready**: Real cloud infrastructure, not toy hosting
- **Scalable**: Can upgrade to paid tier later if needed
- **Automated Deployments**: GitHub Actions CI/CD pipeline
- **Professional Setup**: Industry-standard deployment architecture
- **Learning Value**: Experience with enterprise cloud platform
- **Reliability**: Oracle's enterprise-grade infrastructure

## OCI Always Free Tier Resources (2024-2025)

### Compute Instances
- **ARM Ampere A1**: 4 OCPUs + 24 GB RAM (can split into multiple VMs)
  - Flexible allocation (e.g., 1 VM with 4 cores/24GB, or 2 VMs with 2 cores/12GB each)
  - Up to 3,000 OCPU hours/month
- **AMD E2.1.Micro**: 2 VMs with 1/8 OCPU + 1 GB RAM each

### Storage
- **Block Volume**: 200 GB total
- **Boot Volume**: 47 GB minimum per VM
- **Object Storage**: 10 GB

### Database Options
- **Autonomous Database**: 2 Oracle databases (20 GB storage each) - **Oracle DB, not PostgreSQL**
- **PostgreSQL**: Must self-host on compute instance (no managed PostgreSQL in free tier)

### Networking
- **Bandwidth**: 10 TB outbound/month
- **Public IPs**: 2 reserved public IPv4 addresses
- **Load Balancer**: 1 load balancer (10 Mbps)

**Reference**: [OCI Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)

## Proposed Architecture

See full architecture diagram and detailed implementation in the complete issue description.

## Full Documentation

Due to the comprehensive nature of this deployment guide (15,000+ words), the complete issue with all acceptance criteria, step-by-step instructions, code examples, and troubleshooting guides has been prepared.

The deployment covers:
1. OCI Account & Infrastructure Setup
2. Compute Instance Configuration
3. PostgreSQL Installation
4. Django Application Deployment
5. Nginx & Gunicorn Setup
6. SSL/TLS with Let's Encrypt
7. OCI CLI Installation & Configuration
8. GitHub Actions CI/CD Pipeline
9. Monitoring, Backups & Security
10. Performance Optimization

## Key Highlights

### What You Get
- ARM-based server (2 cores, 12GB RAM)
- Self-hosted PostgreSQL database
- Automated deployments via GitHub Actions
- Free SSL certificates
- Production-ready architecture
- **Total cost: $0/month** (excluding optional domain ~$15/year)

### Technologies Used
- OCI Compute (ARM Ampere A1)
- PostgreSQL 15
- Gunicorn WSGI server
- Nginx reverse proxy
- Supervisor process manager
- Let's Encrypt SSL
- GitHub Actions CI/CD

### Estimated Time
15-20 hours total (can spread over 1-2 weeks)

## Priority
**Tier 1: Critical** - Production deployment required for real-world usage
