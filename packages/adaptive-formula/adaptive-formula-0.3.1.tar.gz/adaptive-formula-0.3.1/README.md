# Adaptive Formula SDK

A cognitive programming framework that replaces complex conditional logic with intelligent, adaptive scoring systems.

## Why Adaptive Formula?

Traditional code filled with nested `if/else` statements becomes unmaintainable as business rules grow. This SDK transforms your decision logic into a **configurable scoring system** that learns and adapts over time, making your code more readable, testable, and scalable.

---

## Working with Real Datasets

### Example: Credit Risk Dataset
```python
import pandas as pd
from adaptive_formula import CognitiveSDK, Field

# Load your data
df = pd.read_csv('credit_data.csv')

# Initialize SDK
sdk = CognitiveSDK()  # or tier='professional' with license

# Configure based on domain knowledge
sdk.configure([
    # High importance for income vs loan ratio
    Field(name='person_income', reference=df['person_income'].median(), 
          importance=3.0, sensitivity=2.5),
    
    # Critical flag for previous defaults
    Field(name='cb_person_default_on_file', reference=False, 
          importance=5.0, sensitivity=5.0),
    
    # Moderate importance for employment length
    Field(name='person_emp_length', reference=5.0, 
          importance=2.0, sensitivity=2.0),
])

# Evaluate each application
for idx, row in df.iterrows():
    score = sdk.evaluate(row.to_dict())
    decision = 'Approved' if score > sdk.get_confidence_level() else 'Denied'
    print(f"Application {idx}: {score:.3f} - {decision}")

# Professional tier: Check adapted threshold
if hasattr(sdk, 'get_metrics'):
    metrics = sdk.get_metrics()
    print(f"Optimized confidence level: {metrics['current_confidence_level']:.3f}")
```

### Tips for Production

1. **Reference Values**: Use median/mode from your "good" historical cases
2. **Testing**: Validate with known outcomes before production
3. **Monitoring**: Track score distributions to identify drift
4. **Categorical Encoding**: Convert ordered categories to numbers
5. **Missing Data**: Handle before evaluation (SDK treats None as 0.0 similarity)

---

## Core Benefits

* **🧠 Declarative Configuration:** Define business rules as prioritized fields instead of procedural code
* **⚡ High Performance:** Core engine compiled to C++ using Cython for production-grade speed
* **📊 Adaptive Learning:** Professional and Enterprise tiers automatically adjust decision confidence based on patterns
* **🎯 Nuanced Decisions:** Generate confidence scores (0.0-1.0) instead of binary pass/fail outcomes
* **🔧 Flexible Data Handling:** Support for dictionaries, DataFrames, and NumPy arrays (Premium tiers)

---

## Installation

```bash
pip install adaptive-formula
```

---

## Quick Start

### Community Edition (Free)

```python
from adaptive_formula import CognitiveSDK, Field

# Initialize SDK
sdk = CognitiveSDK()

# Configure validation rules
sdk.configure([
    Field(name='has_verified_email', reference=False, importance=3.0, sensitivity=5.0),
    Field(name='profile_completeness', reference=0.0, importance=2.0, sensitivity=3.0),
    Field(name='country', reference='unknown', importance=1.0, sensitivity=1.5),
])

# Evaluate data
user_data = {
    'has_verified_email': True,
    'profile_completeness': 0.85,
    'country': 'CO'
}

score = sdk.evaluate(user_data)
print(f"Validation score: {score:.3f}")

if score > sdk.get_confidence_level():
    print("✅ Approved")
else:
    print("⚠️ Requires review")
```

### Professional Edition

```python
from adaptive_formula import CognitiveSDK, Field

# Initialize with license key
sdk = CognitiveSDK(tier='professional', license_key='PRO-XXXX-XXXX-XXXX')

# Configure evaluation rules
sdk.configure([
    Field(name='amount', reference=100.0, importance=3.0, sensitivity=3.5),
    Field(name='location', reference='home', importance=2.0, sensitivity=3.0),
    Field(name='device', reference='known', importance=3.0, sensitivity=4.0),
])

# Professional tier: Automatic confidence adjustment based on patterns
for transaction in transactions:
    score = sdk.evaluate(transaction)
    # Confidence level adapts automatically after each evaluation
    
# Access performance metrics
metrics = sdk.get_metrics()
print(f"Avg score: {metrics['avg_score']:.3f}")
print(f"Adapted confidence: {metrics['current_confidence_level']:.3f}")
```

---

## API Reference

### CognitiveSDK

Main interface for the Adaptive Formula SDK.

**Methods:**
- `__init__(tier='community', license_key=None)` - Initialize SDK
- `configure(fields)` - Set up evaluation rules
- `evaluate(data)` - Score data against rules (returns 0.0-1.0)
- `get_confidence_level()` - Get current decision confidence level
- `set_confidence_level(value)` - Manually adjust confidence level
- `get_metrics()` - Performance statistics (Premium only)

### Field

Configuration for individual evaluation criteria.

**Parameters:**
- `name` (str): Field identifier
- `reference` (Any): Baseline value for comparison
- `importance` (float): Priority factor (default: 1.0)
- `sensitivity` (float): Strictness factor (default: 1.5)

---

## How It Works

The SDK evaluates your data by comparing each field against its configured reference value. Each field's contribution is adjusted by its **importance** (how much it matters) and **sensitivity** (how strictly it's evaluated). 

The result is a confidence score between 0.0 and 1.0 that represents how well your data aligns with the configured expectations.

### Data Type Behavior

| Data Type              | Comparison Method   | Example                  | Score Impact         |
|------------------------|---------------------|--------------------------|----------------------|
| **Numeric**            | Relative difference | `amount=95` vs ref `100` | ~0.95 (very similar) |
| **String/Category**    | Exact match only    | `'rent'` vs ref `'own'`  | 0.3 (different)      |
| **Boolean**            | Binary comparison   | `True` vs ref `False`    | 0.0 (opposite)       |
| **Missing/None**       | Penalized           | `None` vs any ref        | 0.0 (missing)        |

### Calibration Guide

Start with these baseline values and adjust based on your results:

| Importance | Meaning      | Use Case                |
|------------|--------------|-------------------------|
| 1.0 - 2.0  | Nice to have | Secondary indicators    |
| 2.0 - 3.0  | Moderate     | Standard business rules |
| 3.0 - 4.0  | Important    | Key decision factors    |
| 4.0 - 5.0  | Critical     | Must-have requirements  |

| Sensitivity | Meaning     | Use Case                    |
|-------------|-------------|-----------------------------|
| 1.0 - 2.0   | Flexible    | Allow variations            |
| 2.0 - 3.0   | Moderate    | Standard strictness         |
| 3.0 - 4.0   | Strict      | Low tolerance for deviation |
| 4.0 - 5.0   | Very Strict | Near-exact match required   |

**Tip:** Start with (importance=2.0, sensitivity=2.0) for all fields, then adjust based on business requirements.

### Important Notes

- The SDK performs **unsupervised learning** - it adapts thresholds based on score distributions, not labeled outcomes
- For categorical variables, consider using numeric encodings if you need gradual similarities
- Professional/Enterprise tiers optimize these parameters automatically over time

---

## Tier Comparison

| Feature                    | Community  |     Professional       |       Enterprise       |
|----------------------------|------------|------------------------|------------------------|
| **Evaluations/month**      | Unlimited* |       Unlimited        |       Unlimited        |
| **Data formats**           | Dict only  | Dict, DataFrame, NumPy | Dict, DataFrame, NumPy |
| **Adaptive learning**      |    ❌      |          ✅           |          ✅            |
| **Performance metrics**    |    ❌      |          ✅           |          ✅            |
| **Automatic optimization** |    ❌      |         Basic          |       Advanced         |
| **Support**                | Community  |          Email         |      Priority SLA      |
| **License validity**       |    N/A     |          Annual        |         Annual         |

*Community tier is free for evaluation. Production use requires registration.

---

## Use Cases

### Credit Risk Assessment
```python
sdk.configure([
    # Numeric fields - gradual similarity
    Field(name='person_income', reference=50000, importance=4.0, sensitivity=3.0),
    Field(name='loan_percent_income', reference=0.2, importance=5.0, sensitivity=4.0),
    
    # Categorical fields - exact match scoring
    Field(name='person_home_ownership', reference='own', importance=3.0, sensitivity=2.0),
    Field(name='loan_intent', reference='personal', importance=2.0, sensitivity=2.0),
    
    # Boolean fields - binary scoring
    Field(name='cb_person_default_on_file', reference=False, importance=5.0, sensitivity=5.0),
])

# Note: For categorical variables with natural ordering (e.g., 'own'>'mortgage'>'rent'),
# consider numeric encoding: own=3, mortgage=2, rent=1
```

### Fraud Detection
```python
sdk.configure([
    Field(name='transaction_amount', reference=100, importance=3.0, sensitivity=3.5),
    Field(name='merchant_location', reference='domestic', importance=2.0, sensitivity=3.0),
    Field(name='time_since_last', reference=3600, importance=2.5, sensitivity=2.0),
])
```

### User Verification
```python
sdk.configure([
    Field(name='email_verified', reference=True, importance=5.0, sensitivity=5.0),
    Field(name='phone_verified', reference=True, importance=4.0, sensitivity=4.0),
    Field(name='documents_uploaded', reference=True, importance=3.0, sensitivity=3.5),
])
```

### Lead Scoring
```python
sdk.configure([
    Field(name='engagement_score', reference=0.5, importance=3.0, sensitivity=2.0),
    Field(name='company_size', reference='medium', importance=2.0, sensitivity=1.5),
    Field(name='budget_range', reference=50000, importance=4.0, sensitivity=3.0),
])
```

---

## Professional & Enterprise Licensing

Professional and Enterprise tiers include:
- Adaptive confidence learning from evaluation patterns
- Real-time performance metrics and insights
- Support for complex data structures
- Production-ready optimization algorithms

**To purchase a license:**
- Professional: $299/month or $2,999/year
- Enterprise: Contact for custom pricing
- Email: licensing@adaptiveformula.ai

**License format:**
- Professional: `PRO-XXXX-XXXX-XXXX`
- Enterprise: `ENT-XXXX-XXXX-XXXX`

---

## Migration from If/Else

**Before:**
```python
def validate_user(user):
    if not user.get('email_verified'):
        return False
    if user.get('risk_score', 0) > 80:
        return False
    if user.get('country') in ['XX', 'YY']:
        return False
    # ... dozens more conditions
    return True
```

**After:**
```python
sdk = CognitiveSDK()
sdk.configure([
    Field(name='email_verified', reference=True, importance=5.0, sensitivity=5.0),
    Field(name='risk_score', reference=0, importance=3.0, sensitivity=4.0),
    Field(name='country', reference='US', importance=2.0, sensitivity=2.0),
])

score = sdk.evaluate(user)
return score > sdk.get_confidence_level()
```

---

## Frequently Asked Questions

### How do I handle categorical variables with multiple values?
Categorical variables use exact match scoring (1.0 for match, 0.3 for mismatch). For ordered categories (e.g., credit ratings A>B>C), convert to numeric values for gradual similarity.

### Can I train the model with historical labeled data?
The SDK uses unsupervised adaptive learning. It optimizes based on score distributions, not labeled outcomes. For supervised learning, use the scores as features in your ML pipeline.

### How do I determine initial importance and sensitivity values?
Start with baseline (2.0, 2.0) for all fields. Increase importance for business-critical fields. Increase sensitivity when exact matches are required. Test with known cases and adjust.

### What's the difference between importance and sensitivity?
- **Importance**: How much a field contributes to the final score (weight)
- **Sensitivity**: How strictly differences are penalized (tolerance)

### Can I use this with pandas DataFrames?
Professional and Enterprise tiers support DataFrames directly:
```python
score = sdk.evaluate(df.iloc[0])  # Evaluate single row
```

### How does the adaptive learning work?
Professional/Enterprise tiers automatically adjust the confidence threshold based on score distributions. After 10+ evaluations, the system optimizes decision boundaries.

---

## Support

- **Documentation:** https://docs.adaptiveformula.ai
- **Community:** https://github.com/adaptiveformula/sdk/discussions
- **Issues:** https://github.com/adaptiveformula/sdk/issues
- **Professional/Enterprise Support:** support@adaptiveformula.ai

---

## License

MIT License for Community Edition. Professional and Enterprise editions are subject to commercial licensing terms.

© 2025 Adaptive Formula. Cognitive Programming is a trademark of Adaptive Formula, Inc.