# Experimental Design Protocol: H003 - AI-Guided Genetic Testing Strategy

**Protocol ID:** H003-GEN-AI-2025
**Version:** 1.0
**Date:** 2025-11-09

## Study Overview

**Title:** Machine Learning-Guided Genetic Testing Strategy to Improve Diagnostic Yield and Reduce Costs in Pediatric Cardiomyopathy

**Study Type:** Pragmatic, multi-center, randomized controlled trial

**Primary Hypothesis:** Machine learning algorithms incorporating ECG and clinical features will prioritize genetic testing in pediatric cardiomyopathy patients, increasing diagnostic yield by 35% while reducing testing costs by 25%.

## Study Objectives

### Primary Objective
- To determine if an AI-guided genetic testing approach improves diagnostic yield compared to standard genetic testing strategies

### Secondary Objectives
- To evaluate cost-effectiveness of AI-guided testing
- To assess time to diagnosis
- To measure impact on clinical decision-making
- To evaluate physician acceptance and satisfaction

## Study Design

### Design Summary
- **Design:** Pragmatic, open-label, randomized controlled trial
- **Arms:** (1) AI-guided genetic testing strategy vs (2) Standard of care genetic testing
- **Randomization:** 1:1 allocation, stratified by center and cardiomyopathy type
- **Sample Size:** 400 pediatric patients (200 per arm)
- **Duration:** 24 months enrollment, 6 months follow-up

### Study Sites
- **Lead Site:** Boston Children's Hospital
- **Participating Sites:** 4 additional major pediatric cardiology centers
- **Target Population:** Children with cardiomyopathy requiring genetic evaluation

### Population
- **Inclusion Criteria:**
  - Age 0-18 years
  - Clinical diagnosis of cardiomyopathy (any type)
  - No prior genetic testing for cardiomyopathy
  - Referral for genetic evaluation by treating cardiologist
- **Exclusion Criteria:**
  - Known genetic syndrome
  - Previous comprehensive genetic testing
  - Inability to provide informed consent
  - Non-residents (follow-up challenges)

## Intervention

### AI-Guided Testing Arm
- **Algorithm Development:** Retrospective training on 1,000+ cases
- **Input Features:** ECG characteristics, family history, clinical symptoms, echocardiogram findings
- **Output:** Tiered testing recommendation (comprehensive WES, targeted panel, or single gene testing)
- **Real-time Integration:** Decision support integrated into EMR workflow
- **Genetic Counselor Review:** All AI recommendations reviewed by certified genetic counselor

### Standard Care Arm
- **Current Standard Practice:** Comprehensive WES for all patients (per current guidelines)
- **Usual Clinical Workflow:** No AI decision support
- **Genetic Counselor Review:** Standard pre- and post-test counseling

## Data Collection

### Baseline Data
- **Demographics:** Age, sex, ethnicity, insurance status
- **Clinical Presentation:** Symptoms, functional class, NYHA/WHO classification
- **Family History:** Detailed pedigree analysis (3 generations)
- **ECG Data:** Standard 12-lead ECG with automated feature extraction
- **Echocardiogram Data:** Standard measurements, functional assessment
- **Medications:** Current cardiac medications and dosages

### Genetic Testing Data
- **Testing Strategy:** Type of test ordered (WES, panel, single gene)
- **Turnaround Time:** Days from sample collection to result
- **Cost:** Actual cost of genetic testing (reimbursement rates)
- **Results:** Pathogenic/likely pathogenic variants, VUS, negative results
- **Clinical Impact:** Changes in management based on results

### Outcome Measures
- **Primary Endpoint:** Diagnostic yield (pathogenic/likely pathogenic variants)
- **Secondary Endpoints:** Cost per diagnosis, time to diagnosis, clinical utility
- **Process Measures:** Physician adherence to recommendations, patient satisfaction

## Sample Size Calculation

### Assumptions
- **Standard Care Diagnostic Yield:** 33% (based on literature)
- **AI-Guided Yield Improvement:** 35% relative increase (from 33% to 45%)
- **Power:** 80% power, alpha = 0.05, two-sided test
- **Attrition:** 10% loss to follow-up

### Required Sample Size
- **Per Group:** 180 patients
- **Total:** 360 patients (inflated to 400 for attrition)
- **Justification:** Adequate power to detect clinically meaningful difference

## Statistical Analysis Plan

### Primary Analysis
- **Primary Endpoint:** Comparison of diagnostic yield between arms
- **Method:** Chi-square test or Fisher's exact test (as appropriate)
- **Effect Measure:** Risk difference with 95% confidence interval

### Secondary Analyses
- **Cost Analysis:** Cost per diagnosis using bootstrap methods
- **Time-to-Event:** Kaplan-Meier curves for time to diagnosis
- **Subgroup Analyses:** By cardiomyopathy type, age group, center
- **Per-Protocol Analysis:** Patients adhering to assigned strategy

### Interim Analyses
- **Safety Analysis:** After 100 patients enrolled
- **Futility Analysis:** After 200 patients enrolled
- **Stopping Rules:** O'Brien-Fleming boundaries for efficacy

## AI Model Development

### Training Dataset
- **Source:** Retrospective cases from participating centers (2015-2023)
- **Sample Size:** Minimum 1,000 patients with known outcomes
- **Features:** 50+ ECG, clinical, and family history variables
- **Target:** Genetic testing result (positive/negative) and optimal testing strategy

### Model Architecture
- **Algorithm:** Gradient boosting with SHAP interpretability
- **Cross-validation:** 10-fold cross-validation
- **Feature Selection:** Recursive feature elimination with cross-validation
- **Calibration:** Platt scaling for probability outputs

### Validation Strategy
- **Internal Validation:** Hold-out test set (20% of training data)
- **Temporal Validation:** Most recent year of data
- **External Validation:** Independent dataset from non-participating center

## Ethical Considerations

### IRB Review
- Central IRB with reliance agreements
- Focus on pragmatic trial ethics
- Minimal risk to participants

### Informed Consent
- **Process:** Two-stage consent (study consent + genetic testing consent)
- **Materials:** Age-appropriate assent forms (>7 years)
- **Genetic Counseling:** Available for all participants

### Data Privacy
- **De-identified Data:** All study data de-identified
- **Secure Storage:** HIPAA-compliant servers
- **Access Controls:** Role-based access to genetic data

### Return of Results
- **Clinically Actionable Results:** Returned through standard clinical channels
- **VUS Management:** Follow current ACMG guidelines
- **Incidental Findings:** Policy aligned with current recommendations

## Quality Assurance

### Data Quality
- **Monitoring:** Regular data quality checks
- **Training:** Site initiation and ongoing training
- **Standardization:** Common data elements and definitions

### Model Performance
- **Monitoring:** Real-time performance tracking
- **Updates:** Model retraining quarterly with new data
- **Safety:** Monitoring for bias and fairness

### Clinical Quality
- **Standardization:** Genetic testing protocols across sites
- **Adherence:** Monitoring of protocol compliance
- **Safety:** DSMB oversight

## Budget and Resources

### Personnel
- **Principal Investigator:** 10% effort
- **Co-Investigators:** 5% effort each (5 sites)
- **Study Coordinator:** 1 FTE lead + 0.5 FTE per site
- **Data Scientist:** 75% effort
- **Genetic Counselor:** 1 FTE
- **Biostatistician:** 20% effort
- **Economic Analyst:** 25% effort

### Direct Costs
- **Personnel:** $850K over 3 years
- **Genetic Testing:** $1,000/patient × 400 = $400K
- **Data Management:** $250K
- **Site Support:** $200K ($40K per site)
- **Travel and Meetings:** $150K
- **Indirect Costs:** 35% of direct costs

**Total Estimated Budget:** $2.2M over 3 years

## Timeline

### Phase 1: Preparation (Months 1-6)
- **Months 1-3:** Finalize protocol, IRB approvals, site contracts
- **Months 4-6:** AI model development, data infrastructure setup, staff training

### Phase 2: Enrollment (Months 7-30)
- **Months 7-12:** Site initiation, enrollment begins
- **Months 13-24:** Full enrollment period
- **Months 25-30:** Complete enrollment, continue follow-up

### Phase 3: Analysis and Dissemination (Months 31-36)
- **Months 31-33:** Data cleaning and final analysis
- **Months 34-36:** Manuscript preparation, conference presentations

## Expected Outcomes

### Primary Expected Result
- **Diagnostic Yield:** 45% in AI-guided arm vs 33% in standard care (35% relative improvement)

### Secondary Expected Results
- **Cost Reduction:** 25% reduction in average testing cost per patient
- **Time Savings:** 50% reduction in time to diagnosis
- **Clinical Impact:** 20% increase in management changes based on genetic results

### Implementation Impact
- **Scalable Framework:** Model applicable to other genetic conditions
- **Healthcare Value:** Improved value-based care in pediatric genetics
- **Patient Experience:** Faster, more efficient diagnostic journey

## Dissemination Plan

### Scientific Dissemination
- **Primary Manuscript:** High-impact genetics or medical journal
- **Methods Paper:** AI/ML journal with detailed methodology
- **Economic Analysis:** Health economics journal

### Clinical Dissemination
- **Conference Presentations:** AAP, AHA, ASHG conferences
- **Guideline Impact:** Potential influence on future clinical guidelines
- **Implementation Toolkit:** Resources for clinical adoption

### Patient Dissemination
- **Patient Summaries:** Lay summaries of findings
- **Advocacy Groups:** Presentations to patient advocacy organizations
- **Media Outreach:** Science communication for broader impact

## Risk Mitigation

### Clinical Risks
- **Standard of Care:** All patients receive appropriate clinical care
- **Safety Monitoring:** DSMB oversight for patient safety
- **Backup Plans:** Standard testing available if AI fails

### Technical Risks
- **Model Performance:** Continuous monitoring and updates
- **System Failures:** Backup manual processes
- **Data Quality:** Rigorous data validation procedures

### Implementation Risks
- **Physician Adoption:** Training and support systems
- **System Integration:** Phased rollout with feedback
- **Patient Acceptance:** Education and counseling support

---

**Principal Investigator:** [Name, MD, PhD]
**Contact:** [email], [phone]
**ClinicalTrials.gov Identifier:** [To be assigned]

*This protocol represents a pragmatic approach to evaluating AI-guided genetic testing in real-world clinical practice.*