# Experimental Design Protocol: H001 - Multi-modal Neonatal Cardiac Risk Prediction

**Protocol ID:** H001-NEO-RISK-2025
**Version:** 1.0
**Date:** 2025-11-09

## Study Overview

**Title:** Multi-modal Integration of ECG, Echocardiogram, and Genetic Data for 6-Month Mortality Prediction in Neonates with Congenital Heart Disease

**Study Type:** Prospective, multicenter, observational cohort study with embedded model development and validation

**Primary Hypothesis:** Integration of ECG, echocardiogram, and genetic data in neonates with congenital heart disease will improve 6-month mortality prediction by 40% compared to single-modality ECG analysis alone.

## Study Objectives

### Primary Objective
- To develop and validate a multi-modal AI model that predicts 6-month all-cause mortality in neonates (≤28 days) with congenital heart disease

### Secondary Objectives
- To predict ICU length of stay and surgical complication rates
- To identify high-risk neonates 48 hours earlier than standard clinical assessment
- To create interpretable risk stratification for clinical decision-making

## Study Design

### Design Summary
- **Phase 1:** Retrospective model development (12 months)
- **Phase 2:** Prospective validation (24 months)
- **Phase 3:** Clinical implementation pilot (12 months)

### Study Sites
- **Lead Site:** Boston Children's Hospital
- **Participating Sites:** Children's Hospital of Philadelphia, Texas Children's Hospital, Cincinnati Children's Hospital
- **Target Enrollment:** 2,000 neonates across all sites

### Population
- **Inclusion Criteria:**
  - Neonates ≤28 days old at enrollment
  - Diagnosed congenital heart disease (any lesion)
  - Available ECG within 24 hours of echocardiogram
  - Parental consent for genetic testing
- **Exclusion Criteria:**
  - Prematurity <34 weeks gestation
  - Known chromosomal abnormalities
  - Non-cardiac life-limiting conditions
  - Incomplete data sets

## Data Collection

### ECG Data
- Standard 12-lead ECG (or neonatal adapted leads)
- Digital acquisition at 500Hz sampling rate
- Raw waveform data stored for AI processing
- Timing: Within 24 hours of echocardiogram

### Echocardiogram Data
- Standardized transthoracic echocardiogram
- 2D, Doppler, and color flow imaging
- Quantitative measurements (ventricular dimensions, valve function)
- Image storage in DICOM format

### Genetic Data
- Rapid whole exome sequencing (WES)
- Targeted congenital heart disease gene panel (as backup)
- Turnaround time: 7-10 days
- Variant interpretation according to ACMG guidelines

### Clinical Data
- Demographics (birth weight, gestational age, sex)
- Prenatal diagnosis information
- Initial presentation and clinical status
- Surgical/procedural interventions
- Outcomes (mortality, complications, length of stay)

## AI Model Development

### Model Architecture
- **Multi-modal neural network** with separate branches for each data type
- **ECG branch:** 1D CNN with attention mechanism
- **Echo branch:** CNN for image features + MLP for measurements
- **Genetic branch:** Embedding layer for variant data
- **Fusion layer:** Combines features from all modalities

### Training Strategy
- **Internal validation:** 70/15/15 split (train/validation/test)
- **External validation:** Hold-out dataset from participating centers
- **Cross-validation:** 5-fold cross-validation for robustness
- **Hyperparameter optimization:** Bayesian optimization

### Performance Metrics
- **Primary:** AUROC, AUPRC for 6-month mortality prediction
- **Secondary:** Sensitivity, specificity, calibration curves
- **Clinical utility:** Net reclassification improvement (NRI), decision curve analysis

## Statistical Analysis

### Sample Size Calculation
- **Assumptions:** 6-month mortality of 15% in high-risk neonates
- **Effect size:** 40% improvement in AUROC (from 0.75 to 0.85)
- **Power:** 90% power, alpha = 0.05
- **Required sample:** 1,800 neonates (accounting for 10% loss to follow-up)

### Analysis Plan
1. **Descriptive statistics** for baseline characteristics
2. **Model comparison:** Multi-modal vs single-modality models
3. **Subgroup analyses:** By lesion complexity, gestational age
4. **Temporal validation:** Performance over time periods
5. **Interpretability analysis:** SHAP values for feature importance

## Ethical Considerations

### Ethical Review
- IRB approval at all participating sites
- Central IRB reliance agreement for consistency
- Data safety monitoring board (DSMB) oversight

### Informed Consent
- Parental consent for all study procedures
- Separate consent for genetic testing
- Option to receive genetic results with genetic counseling

### Privacy and Security
- De-identified data storage
- HIPAA-compliant data transmission
- Limited access to genetic data
- Data use agreements between sites

## Safety Monitoring

### DSMB Charter
- Quarterly review of enrollment and outcomes
- Interim analyses after 500 and 1,000 enrollments
- Stopping rules for unexpected harm or futility
- Monitoring for algorithmic bias

### Risk Mitigation
- Standard of care maintained for all patients
- Model predictions used only for research purposes
- Clinical decisions not based on unvalidated models
- Backup genetic testing available

## Timeline and Milestones

### Phase 1: Model Development (Months 1-12)
- **Months 1-3:** Data infrastructure setup, IRB approvals
- **Months 4-6:** Retrospective data collection and cleaning
- **Months 7-9:** Initial model development and training
- **Months 10-12:** Internal validation and model refinement

### Phase 2: Prospective Validation (Months 13-36)
- **Months 13-18:** Site initiation and enrollment start
- **Months 19-30:** Ongoing enrollment and data collection
- **Months 31-36:** Complete enrollment, final analysis

### Phase 3: Implementation (Months 37-48)
- **Months 37-42:** Clinical integration development
- **Months 43-48:** Pilot implementation and evaluation

## Budget and Resources

### Personnel
- **Principal Investigator:** 15% effort
- **Co-Investigators:** 10% effort each (4 sites)
- **Data Scientist:** 100% effort
- **Research Coordinators:** 1 FTE per site
- **Biostatistician:** 25% effort
- **Genetic Counselor:** 50% effort

### Direct Costs
- **Personnel:** $1.2M over 4 years
- **Genetic Testing:** $1,500/patient × 2,000 = $3M
- **Data Infrastructure:** $500K
- **Equipment:** ECG acquisition systems, $200K
- **Travel and Meetings:** $200K
- **Indirect Costs:** 40% of direct costs

**Total Estimated Budget:** $4.5M over 4 years

## Expected Outcomes and Impact

### Scientific Impact
- Validated multi-modal AI model for neonatal cardiac risk prediction
- Published methodology for pediatric multi-modal AI
- Insights into pathophysiology of neonatal cardiac decompensation

### Clinical Impact
- Earlier identification of high-risk neonates
- Improved resource allocation and treatment planning
- Reduced mortality through targeted interventions

### Societal Impact
- Improved outcomes for vulnerable neonatal population
- Framework for multi-modal AI in other pediatric conditions
- Training opportunities in pediatric medical AI

## Dissemination Plan

### Publications
- Primary outcomes manuscript in high-impact journal
- Methodology paper in AI/ML journal
- Subgroup analyses in specialty journals

### Conference Presentations
- American Heart Association (AHA) Scientific Sessions
- American Academy of Pediatrics (AAP) National Conference
- Machine Learning for Healthcare (MLHC) Conference

### Data Sharing
- De-identified dataset available through NIH repositories
- Open-source code for reproducibility
- Collaboration with other research groups

## Quality Assurance

### Data Quality
- Regular data audits and validation checks
- Standardized operating procedures (SOPs)
- Training for all study personnel
- Centralized data monitoring

### Model Quality
- External validation across multiple sites
- Robustness testing with synthetic data
- Fairness and bias assessment
- Clinical validation with expert review

## Contingency Plans

### Enrollment Challenges
- Expand to additional sites if enrollment slow
- Relax inclusion criteria after DSMB review
- Extend enrollment period if necessary

### Technical Challenges
- Backup analysis plans if AI models underperform
- Alternative model architectures ready
- Manual annotation fallbacks

### Funding Challenges
- Phased approach with go/no-go decisions
- Industry partnership opportunities
- Additional grant applications

---

**Principal Investigator:** [Name, MD, PhD]
**Contact:** [email], [phone]
**Funding Source:** [To be determined]

*This protocol will be updated as the study progresses and new information becomes available.*