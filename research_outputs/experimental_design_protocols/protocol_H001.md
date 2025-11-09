# Experimental Design Protocol: H001
## Integrated Digital Health Ecosystem for Atrial Fibrillation Management

**Protocol ID:** H001-PROTOCOL-2025-01
**Version:** 1.0
**Date:** 2025-11-09
**Principal Investigator:** [To be assigned]
**Study Type:** Pragmatic Cluster Randomized Controlled Trial

### 1. Background and Rationale

Current atrial fibrillation (AF) management faces significant challenges in coordination, monitoring, and timely intervention. While individual components (wearable devices, AI algorithms, decision support) show promise, their integration into a comprehensive ecosystem has not been evaluated. This study tests the hypothesis that an integrated digital health ecosystem will significantly improve clinical outcomes compared to standard care.

### 2. Study Objectives

#### Primary Objective
- To determine if an integrated digital health ecosystem reduces AF-related hospitalizations by 35% compared to standard care over 24 months.

#### Secondary Objectives
- To assess improvement in quality of life (AFEQT score) by 25%
- To evaluate reduction in time to intervention for AF episodes
- To measure improvement in medication adherence
- To assess cost-effectiveness of the intervention
- To evaluate patient satisfaction and engagement

### 3. Study Design

#### Design Overview
- **Type:** Pragmatic, open-label, cluster randomized controlled trial
- **Randomization Unit:** Healthcare system/hospital cluster
- **Stratification Factors:** System size, urban/rural location, baseline digital maturity
- **Clusters:** 20 healthcare systems (10 intervention, 10 control)
- **Study Duration:** 24 months per participant
- **Total Study Duration:** 36 months (including setup and analysis)

#### Cluster Selection Criteria
- Minimum 100 AF patients per system
- Existing electronic health record system
- Willingness to implement digital health integration
- Diverse patient population representation

### 4. Participant Population

#### Inclusion Criteria
- Adults ≥18 years with documented atrial fibrillation
- Able to provide informed consent
- Access to smartphone or tablet
- Fluent in study languages (English/Spanish)

#### Exclusion Criteria
- Cognitive impairment preventing device use
- Life expectancy <1 year
- Participation in another interventional AF study
- Contraindication to wearable devices

### 5. Intervention Components

#### Digital Health Ecosystem Components
1. **Continuous Monitoring Platform**
   - FDA-cleared wearable ECG monitor
   - Mobile app for symptom reporting
   - Automated arrhythmia detection algorithms

2. **AI-Powered Decision Support**
   - Real-time risk assessment
   - Treatment recommendation engine
   - Alert system for clinicians

3. **Care Coordination Platform**
   - Secure messaging between patients and care team
   - Medication tracking and reminders
   - Appointment scheduling integration

4. **Data Integration Hub**
   - EHR integration
   - Wearable data aggregation
   - Clinical decision support integration

#### Implementation Timeline
- **Months 0-3:** Site selection and onboarding
- **Months 4-6:** System installation and training
- **Months 7-30:** Patient enrollment and intervention
- **Months 31-36:** Data analysis and reporting

### 6. Outcomes and Measurements

#### Primary Outcome
- **AF-related Hospitalizations**: Number of hospital admissions primarily due to AF complications
  - **Measurement:** Hospital discharge data adjudicated by blinded committee
  - **Timing:** Continuous monitoring throughout 24-month follow-up

#### Secondary Outcomes
1. **Quality of Life**: AFEQT (Atrial Fibrillation Effect on Quality of Life) score
   - **Measurement:** Validated questionnaire at baseline, 6, 12, 18, 24 months

2. **Time to Intervention**: Duration from AF detection to therapeutic intervention
   - **Measurement:** System timestamps and clinical records

3. **Medication Adherence**: Proportion of days covered (PDC) for anticoagulation and rate control
   - **Measurement**: Pharmacy refill data and patient self-report

4. **Cost-Effectiveness**: Incremental cost per quality-adjusted life year (QALY)
   - **Measurement**: Healthcare utilization costs and utility assessment

5. **Patient Satisfaction**: System usability and satisfaction scores
   - **Measurement:** SUS (System Usability Scale) and custom surveys

### 7. Sample Size Calculation

#### Assumptions
- Baseline hospitalization rate: 15% per year
- Intraclass correlation coefficient (ICC): 0.02
- Average cluster size: 100 patients
- Power: 80%
- Alpha: 0.05
- Expected effect size: 35% relative reduction

#### Required Sample Size
- **Individual participants:** 2,000 total (1,000 per arm)
- **Clusters:** 20 systems (10 per arm)
- **Accounting for 15% attrition:** 2,300 enrolled participants

### 8. Randomization and Blinding

#### Randomization Procedure
- Computer-generated random allocation
- Stratified by system size and location
- Allocation concealment maintained until baseline data collection

#### Blinding
- **Participants:** Open label (impractical to blind)
- **Clinicians:** Open label
- **Outcome Adjudicators:** Blinded to treatment allocation
- **Statistical Analysis:** Blinded until primary analysis complete

### 9. Data Collection and Management

#### Data Sources
1. **Electronic Health Records**: Clinical outcomes, medications, comorbidities
2. **Digital Platform Data**: Device metrics, app usage, alert responses
3. **Patient-Reported Outcomes**: QoL surveys, satisfaction questionnaires
4. **Administrative Data**: Hospitalizations, healthcare utilization

#### Data Quality Assurance
- Automated data validation checks
- Monthly data quality reports
- Source data verification for 10% of records
- Centralized monitoring with trigger algorithms

#### Data Security
- HIPAA-compliant data transmission
- End-to-end encryption for patient data
- De-identified data for analysis
- Regular security audits

### 10. Statistical Analysis Plan

#### Primary Analysis
- **Population:** Intention-to-treat (all enrolled participants)
- **Method:** Mixed-effects Poisson regression
- **Model:** Hospitalization count ~ treatment + time + covariates + (1|cluster)
- **Adjustment for:** Baseline hospitalization rate, age, sex, comorbidities

#### Secondary Analyses
- **Quality of Life:** Mixed-effects linear repeated measures
- **Time to Event:** Cox proportional hazards with shared frailty
- **Cost-Effectiveness:** Incremental cost-effectiveness ratio with bootstrapped confidence intervals

#### Subgroup Analyses
- Age groups (<65, 65-80, >80)
- AF type (paroxysmal, persistent, permanent)
- Digital literacy level
- Socioeconomic status

#### Missing Data
- Primary outcome: No missing data (hospitalization capture complete)
- Secondary outcomes: Multiple imputation with chained equations
- Sensitivity analysis: Complete case and worst-case scenarios

### 11. Safety Monitoring

#### Adverse Event Monitoring
- **Serious Adverse Events:** Immediate reporting within 24 hours
- **Device-Related Events:** Weekly safety reviews
- **Data Security Breaches:** Immediate notification and mitigation

#### Data Safety Monitoring Board
- Independent committee with cardiology, statistics, and ethics expertise
- Quarterly safety reviews
- Stopping rules for efficacy or safety concerns

### 12. Ethical Considerations

#### Informed Consent
- Comprehensive consent process with digital literacy assessment
- Option for limited data sharing preferences
- Clear explanation of data security measures

#### Privacy Protection
- Minimum necessary data collection
- Transparent data use policies
- Right to withdraw without penalty

#### Equity Considerations
- Provision of devices for participants unable to afford
- Technical support for digital literacy challenges
- Multi-language support and cultural adaptation

### 13. Timeline and Milestones

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| Start-up | Months 0-6 | Site selection, system implementation, staff training |
| Enrollment | Months 7-30 | Participant recruitment, baseline assessments |
| Intervention | Months 7-54 | 24-month participant follow-up |
| Analysis | Months 55-60 | Data cleaning, analysis, manuscript preparation |
| Dissemination | Months 61-66 | Publication, guideline updates, implementation guidance |

### 14. Budget Considerations

#### Major Cost Categories
- **Technology Development:** $1.2M (platform integration, customization)
- **Equipment:** $800K (wearable devices, tablets for participants)
- **Personnel:** $1.5M (coordinators, data managers, analysts)
- **Site Support:** $600K (training, technical support, incentives)
- **Data Management:** $400K (secure servers, software licenses)
- **Overhead:** $500K (institutional costs, regulatory compliance)

#### Total Estimated Budget: $5.0 million

### 15. Dissemination Plan

#### Scientific Dissemination
- Publication in high-impact cardiology and digital health journals
- Presentation at major cardiology conferences
- Data sharing through appropriate repositories

#### Clinical Implementation
- Development of implementation toolkit for healthcare systems
- Collaboration with professional societies for guideline integration
- Real-world evidence generation through registry extension

#### Patient and Public Engagement
- Plain language summaries for participants
- Community presentations and webinars
- Patient advocacy group partnerships

### 16. Potential Limitations and Mitigation Strategies

#### Limitations
1. **Contamination:** Control sites may adopt similar technologies
   - *Mitigation:* Delayed feedback to control sites, technology transfer after study

2. **Digital Divide:** Variable participant digital literacy
   - *Mitigation:* Comprehensive training, technical support, device provision

3. **Technology Evolution:** Rapid changes in digital health landscape
   - *Mitigation:* Platform flexibility, regular technology updates

4. **Generalizability:** Study sites may not represent all settings
   - *Mitigation:* Diverse site selection, pragmatic design elements

### 17. Success Criteria

#### Primary Success
- Statistically significant 35% reduction in AF-related hospitalizations
- Successful implementation across 80% of intervention clusters
- Cost-effectiveness ratio <$50,000 per QALY

#### Secondary Success
- 25% improvement in quality of life scores
- High patient satisfaction (>80% satisfied)
- Scalable model for other healthcare systems

---

**Protocol Approval Status:** Draft
**IRB Submission:** Planned within 3 months
**First Patient Enrollment:** Estimated 6 months after funding