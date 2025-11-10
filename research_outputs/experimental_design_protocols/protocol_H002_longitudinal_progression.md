# Experimental Design Protocol: H002 - Longitudinal Disease Progression AI

**Protocol ID:** H002-LONG-PROG-2025
**Version:** 1.0
**Date:** 2025-11-09

## Study Overview

**Title:** Deep Learning Models for Predicting 5-Year Functional Decline in Pediatric Congenital Heart Disease Using Longitudinal ECG and Clinical Data

**Study Type:** Retrospective cohort study with prospective validation

**Primary Hypothesis:** Deep learning models incorporating longitudinal ECG and clinical data will predict 5-year functional decline in pediatric congenital heart disease patients with 85% accuracy, enabling early intervention strategies.

## Study Objectives

### Primary Objective
- To develop and validate longitudinal AI models that predict functional decline in pediatric CHD patients over 5 years

### Secondary Objectives
- To identify early predictors of disease progression
- To enable risk stratification for targeted interventions
- To understand temporal patterns in disease progression

## Study Design

### Design Summary
- **Phase 1:** Retrospective model development using historical data (18 months)
- **Phase 2:** Prospective validation using ongoing clinics (24 months)
- **Phase 3:** Clinical utility assessment (12 months)

### Study Population
- **Retrospective Cohort:** Patients seen 2010-2020 with ≥5 years follow-up
- **Prospective Cohort:** Current patients with ongoing follow-up
- **Target Sample:** 1,500 patients total

### Inclusion Criteria
- **Age:** 0-18 years at baseline
- **Diagnosis:** Any congenital heart disease
- **Follow-up:** Minimum 5 years of clinical data
- **Data Availability:** At least 3 ECGs and clinical visits over follow-up period

## Data Collection

### Temporal Data Elements
- **ECG Data:** Serial ECGs at least annually
- **Clinical Data:** Height, weight, blood pressure, medications
- **Functional Data:** Exercise capacity, NYHA/WHO class
- **Imaging Data:** Echocardiographic measurements
- **Intervention Data:** Surgeries, catheterizations, hospitalizations

### Outcome Measures
- **Primary Outcome:** Decline in functional capacity (>1 NYHA/WHO class)
- **Secondary Outcomes:** Hospitalization frequency, medication escalation, need for intervention
- **Time-to-Event:** Time from baseline to functional decline

## AI Model Development

### Longitudinal Architecture
- **Temporal Modeling:** LSTM/Transformer networks for sequential data
- **Multi-modal Input:** ECG waveforms + clinical measurements
- **Attention Mechanisms:** Identify critical time points
- **Uncertainty Quantification:** Confidence intervals for predictions

### Training Strategy
- **Time Series Split:** Temporal validation (train on 2010-2017, test on 2018-2020)
- **Cross-Validation:** Patient-level 5-fold cross-validation
- **Data Augmentation:** Synthetic time series generation
- **Regularization:** Dropout and early stopping

## Statistical Analysis

### Sample Size Justification
- **Event Rate:** Expected 20% functional decline over 5 years
- **Effect Size:** Aiming for 85% accuracy vs 70% baseline
- **Power:** 90% power, alpha = 0.05
- **Required Sample:** 1,200 patients (inflated to 1,500 for missing data)

### Analysis Plan
1. **Descriptive Analysis:** Baseline characteristics, temporal patterns
2. **Model Performance:** ROC curves, precision-recall, calibration
3. **Temporal Validation:** Performance over different time periods
4. **Subgroup Analysis:** By lesion complexity, age groups
5. **Interpretability:** Feature importance over time

## Ethical Considerations

### Privacy Protection
- **De-identification:** All patient identifiers removed
- **Data Storage:** Secure, HIPAA-compliant servers
- **Access Control:** Limited access to longitudinal data

### Clinical Relevance
- **No Direct Patient Contact:** Retrospective data analysis
- **Benefit Assessment:** Potential for improved patient care
- **Risk Minimization:** No direct intervention during development phase

## Timeline and Budget

### Timeline
- **Phase 1 (18 months):** Data collection, model development
- **Phase 2 (24 months):** Prospective validation
- **Phase 3 (12 months):** Clinical utility assessment

### Estimated Budget
- **Personnel:** $1.2M
- **Data Infrastructure:** $300K
- **Computational Resources:** $200K
- **Overhead:** 40% indirect costs
- **Total:** $2.3M over 4.5 years

## Expected Outcomes

### Scientific Contributions
- Validated longitudinal prediction models
- Understanding of disease progression patterns
- Methodology for pediatric longitudinal AI

### Clinical Impact
- Early identification of high-risk patients
- Targeted intervention strategies
- Improved resource allocation

---

*This protocol focuses on understanding disease progression over time to enable proactive clinical management.*