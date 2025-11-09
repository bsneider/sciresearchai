# Experimental Design Protocol: H002
## Genomic-Guided Anticoagulation Therapy Selection

**Protocol ID:** H002-PROTOCOL-2025-01
**Version:** 1.0
**Date:** 2025-11-09
**Principal Investigator:** [To be assigned]
**Study Type:** Multicenter Randomized Controlled Trial

### 1. Background and Rationale

Anticoagulation therapy for atrial fibrillation requires balancing stroke prevention against bleeding risk. Current selection relies on clinical scoring systems (CHA2DS2-VASc, HAS-BLED) with limited precision. Pharmacogenomic variations in CYP2C9 and VKORC1 significantly affect warfarin metabolism, while emerging evidence suggests genetic factors may also influence DOAC metabolism and efficacy. This study tests whether genotype-guided anticoagulation selection improves outcomes compared to standard clinical decision-making.

### 2. Study Objectives

#### Primary Objective
- To determine if genotype-guided anticoagulation therapy reduces major bleeding events by 45% compared to standard clinical selection over 36 months.

#### Secondary Objectives
- To assess improvement in stroke prevention efficacy by 20%
- To evaluate medication adherence and persistence
- To measure time to therapeutic anticoagulation
- To assess patient-reported outcomes and satisfaction
- To evaluate cost-effectiveness of genotype-guided therapy

### 3. Study Design

#### Design Overview
- **Type:** Multicenter, open-label, randomized controlled trial
- **Randomization Ratio:** 1:1
- **Randomization Unit:** Individual patient
- **Stratification Factors:** Center, age group (<75, ≥75), baseline anticoagulation status
- **Centers:** 15 sites across diverse healthcare settings
- **Study Duration:** 36 months per participant
- **Total Study Duration:** 48 months

#### Study Arms
1. **Intervention Arm:** Genotype-guided anticoagulation selection
2. **Control Arm:** Standard anticoagulation selection based on clinical factors

### 4. Participant Population

#### Inclusion Criteria
- Adults ≥18 years with atrial fibrillation requiring anticoagulation
- CHA2DS2-VASc score ≥2 (male) or ≥3 (female)
- Ability to provide informed consent
- Willingness to undergo genetic testing

#### Exclusion Criteria
- Current therapeutic anticoagulation >3 months
- Contraindication to all anticoagulant classes
- Life expectancy <1 year
- Severe renal impairment (eGFR <15 mL/min)
- Active bleeding or high bleeding risk precluding anticoagulation
- Pregnancy or breastfeeding

### 5. Intervention Details

#### Genotype-Guided Selection Algorithm
1. **Rapid Genotyping Panel:**
   - CYP2C9 (*2, *3 alleles)
   - VKORC1 (-1639 G>A)
   - CYP4F2 (V433M)
   - ABCB1 (rs1045642)
   - CES1 (rs2244613)

2. **Decision Support Protocol:**
   - **Warfarin-Preferring Genotypes:** Normal CYP2C9 activity, low bleeding risk
   - **DOAC-Preferring Genotypes:** Reduced CYP2C9 activity, high bleeding risk
   - **Apixaban Preference:** ABCB1 variants affecting drug transport
   - **Dabigatran Preference:** CES1 variants affecting drug activation

3. **Dosing Guidance:**
   - Warfarin: Pharmacogenomic dosing algorithm
   - DOACs: Standard dosing with genetic considerations for drug selection

#### Testing Protocol
- **Sample Collection:** Buccal swab or peripheral blood
- **Turnaround Time:** <72 hours from sample collection
- **Testing Platform:** FDA-approved pharmacogenomic testing
- **Reporting:** Integrated into EHR with clinical decision support

### 6. Outcomes and Measurements

#### Primary Outcome
- **Major Bleeding Events:** ISTH definition (fatal bleeding, symptomatic bleeding in critical organ, bleeding causing ≥2g/dL hemoglobin drop or requiring ≥2 units transfusion)
  - **Measurement:** Clinical event adjudication by blinded committee
  - **Timing:** Continuous monitoring throughout 36-month follow-up

#### Secondary Outcomes
1. **Stroke and Systemic Embolism**: Ischemic stroke, TIA, systemic embolism
   - **Measurement:** Neurological imaging and clinical assessment
   - **Adjudication:** Blinded stroke neurologist committee

2. **Therapeutic Anticoagulation Achievement**: Time to first therapeutic INR for warfarin
   - **Measurement:** INR values and pharmacy records
   - **Definition:** INR 2.0-3.0 for two consecutive measurements

3. **Medication Adherence**: Proportion of days covered (PDC)
   - **Measurement**: Pharmacy refill data and pill counts
   - **Threshold**: PDC ≥80% considered adherent

4. **Quality of Life**: SF-36 and disease-specific satisfaction scales
   - **Measurement:** Baseline, 6, 12, 24, 36 months

5. **Cost-Effectiveness**: Incremental cost per QALY gained
   - **Measurement**: Healthcare utilization, medication costs, testing costs

### 7. Sample Size Calculation

#### Assumptions
- Annual major bleeding rate in standard care: 4.5%
- Expected relative risk reduction: 45%
- Power: 80%
- Alpha: 0.05
- Attrition rate: 15% over 3 years

#### Required Sample Size
- **Calculated N:** 2,280 participants (1,140 per arm)
- **Adjusted for attrition:** 2,680 total enrollment
- **Per site average:** ~180 participants

### 8. Randomization and Blinding

#### Randomization Procedure
- Web-based randomization system
- Variable block sizes (2, 4, 6)
- Stratified by center and age group
- Allocation concealed until baseline assessment

#### Blinding
- **Participants:** Open label (necessary for treatment assignment)
- **Clinicians:** Open label (treatment assignment required)
- **Outcome Adjudicators:** Blinded to treatment allocation
- **Statistical Analysis:** Blinded until primary database lock

### 9. Statistical Analysis Plan

#### Primary Analysis
- **Population:** Intention-to-treat (all randomized participants)
- **Method:** Cox proportional hazards regression
- **Model:** Time to major bleeding ~ treatment + stratification factors
- **Adjustment for:** Baseline bleeding risk, age, renal function

#### Secondary Analyses
- **Stroke Prevention:** Competing risks analysis (Fine-Gray model)
- **Time to Therapeutic INR:** Accelerated failure time model
- **Adherence:** Mixed-effects logistic regression
- **Quality of Life:** Repeated measures mixed model

#### Subgroup Analyses
- Age groups (<65, 65-80, >80)
- Renal function categories
- Baseline bleeding risk levels
- Specific genotype combinations

#### Per-Protocol Analysis
- Participants receiving genotype-concordant therapy
- Sensitivity analysis for adherence impact

### 10. Data Collection and Management

#### Data Elements
- **Baseline:** Demographics, medical history, genetics, medications
- **Follow-up:** Clinical events, medication changes, lab values, outcomes
- **Safety:** Adverse events, serious adverse events, protocol violations

#### Data Quality
- Electronic data capture with range and logic checks
- Source data verification for 5% of records
- Monitoring queries resolved within 7 days
- Quarterly data quality reports

#### Genetic Data Security
- Separate storage for genetic data
- De-identified genotype data for analysis
- Access limited to authorized personnel
- Compliance with GINA (Genetic Information Nondiscrimination Act)

### 11. Safety Monitoring

#### Adverse Event Reporting
- **Serious Adverse Events:** Within 24 hours
- **Bleeding Events:** Immediate reporting
- **Genetic Test Findings:** Incidental findings protocol

#### Data Safety Monitoring Board
- Independent cardiologists, hematologists, statisticians
- Quarterly safety reviews
- Annual efficacy reviews
- Stopping rules for safety or overwhelming efficacy

### 12. Ethical Considerations

#### Genetic Testing Ethics
- **Informed Consent:** Comprehensive genetic counseling
- **Incidental Findings:** Protocol for reporting actionable findings
- **Data Privacy:** Secure storage, limited access
- **Discrimination Protection:** Compliance with GINA

#### Clinical Ethics
- **Standard Care Assurance:** Control arm receives evidence-based care
- **Withdrawal Rights:** Participants may withdraw without penalty
- **Access to Results:** Participants receive genetic results and counseling

### 13. Timeline

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| Start-up | Months 0-6 | Site initiation, staff training, system setup |
| Enrollment | Months 7-30 | Participant recruitment, baseline assessments |
| Follow-up | Months 7-42 | 36-month participant follow-up |
| Analysis | Months 43-45 | Data cleaning, analysis, DSMB review |
| Reporting | Months 46-48 | Manuscript preparation, dissemination |

### 14. Budget Considerations

#### Major Cost Categories
- **Genetic Testing:** $600K (3000 participants × $200 per test)
- **Personnel:** $1.2M (PI, coordinators, genetic counselors, data management)
- **Site Support:** $750K (site payments, monitoring, training)
- **Central Testing:** $300K (central laboratory, shipping, quality control)
- **Data Management:** $350K (EDC system, statistics, DSMB)
- **Overhead:** $500K (institutional costs, regulatory compliance)

#### Total Estimated Budget: $3.7 million

### 15. Dissemination Plan

#### Scientific Dissemination
- Publication in major cardiology and pharmacogenomics journals
- Presentation at American Heart Association, HRS, ACC meetings
- Data sharing through dbGaP for genetic data

#### Clinical Integration
- Development of clinical decision support tools
- Guideline recommendations for pharmacogenomic testing
- Educational programs for clinicians

#### Patient Education
- Educational materials about genetic testing in AF
- Results counseling protocols
- Patient advocacy group engagement

### 16. Potential Challenges and Mitigation

#### Technical Challenges
- **Rapid Turnaround:** Ensure testing completes within 72 hours
  - *Mitigation:* Local testing sites, backup laboratories, express shipping

- **Test Quality:** Ensure accuracy across multiple sites
  - *Mitigation:* Centralized quality control, proficiency testing

#### Clinical Challenges
- **Clinician Adoption:** Resistance to genetic guidance
  - *Mitigation:* Education, decision support, evidence generation

- **Treatment Changes:** Evolution of standard therapy during study
  - *Mitigation:* Protocol amendments, adaptive design elements

### 17. Success Criteria

#### Primary Success
- 45% reduction in major bleeding events (statistically significant)
- Implementation success across all sites
- Cost-effectiveness <$100,000 per QALY

#### Secondary Success
- Improved stroke prevention outcomes
- High clinician satisfaction with genotype guidance
- Successful integration into clinical workflow

---

**Protocol Approval Status:** Draft
**IRB Submission:** Planned within 3 months
**First Patient Enrollment:** Estimated 6 months after funding
**Genetic Counseling Certification:** Required for all site personnel