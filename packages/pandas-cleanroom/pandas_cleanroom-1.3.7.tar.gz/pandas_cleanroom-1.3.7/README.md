# Cleanroom 🧹

**Tiny, extensible pandas utilities for aliasing and basic data cleaning**

Cleanroom provides a simple set of pure functions you can compose to clean messy real-world data. It's designed to be lightweight, extensible, and work seamlessly with pandas DataFrames.

## 🚀 Features

- **Flexible Column Matching**: Automatically detects column variations (`first_name`, `First Name`, `f name`, `fname`, etc.)
- **Email Cleaning**: Normalize email addresses to lowercase
- **Name Formatting**: Smart title case with proper handling of particles (van, de, etc.)
- **Phone Standardization**: Convert phone numbers to international format
- **Address Normalization**: Clean ZIP codes, standardize states and countries
- **Schema-Based Cleaning**: Apply custom cleaning rules with flexible schemas
- **Auto-Clean**: Automatically clean common columns with zero configuration

## 📦 Installation

```bash
pip install cleanroom
```

## 🔧 Quick Start

```python
import pandas as pd
import cleanroom

# Sample messy data
df = pd.DataFrame({
    'f name': ['  john ', 'JANE'],
    'e-mail': ['JOHN@EXAMPLE.COM', 'jane@TEST.org'],
    'pnumber': ['(555) 123-4567', '555.987.6543'],
    'zip code': ['12345-6789', '98765'],
    'st': ['California', 'TX']
})

# One-line cleaning with flexible column matching
cleaned_df = cleanroom.auto_clean(df)
print(cleaned_df)
```

**Output:**
```
  f name e-mail              pnumber    zip code st
0   John  john@example.com   +15551234567  123456789  CA
1   Jane  jane@test.org      +15559876543     98765  TX
```

## 📚 API Reference

### Individual Cleaning Functions

#### `clean_email(series)`
Normalize email addresses to lowercase and strip whitespace.

```python
emails = pd.Series(['  JOHN@EXAMPLE.COM  ', 'jane@TEST.org'])
cleaned = cleanroom.clean_email(emails)
# Result: ['john@example.com', 'jane@test.org']
```

#### `clean_name(series, alias_map=None, case="title")`
Clean and format names with smart title casing.

```python
names = pd.Series(['  john smith  ', 'JANE DOE', 'bob o\'connor'])
cleaned = cleanroom.clean_name(names)
# Result: ['John Smith', 'Jane Doe', 'Bob O\'Connor']

# With custom aliases
aliases = {'johnny': 'John', 'bobby': 'Robert'}
cleaned = cleanroom.clean_name(names, alias_map=aliases)
```

#### `clean_phone(series, default_country="US")`
Standardize phone numbers to international format.

```python
phones = pd.Series(['(555) 123-4567', '555.987.6543', '+1-800-555-0199'])
cleaned = cleanroom.clean_phone(phones)
# Result: ['+15551234567', '+15559876543', '+18005550199']
```

#### `clean_number(series)`
Extract only digits (useful for ZIP codes, IDs).

```python
zips = pd.Series(['12345-6789', 'ABC 98765', '  54321  '])
cleaned = cleanroom.clean_number(zips)
# Result: ['123456789', '98765', '54321']
```

#### `clean_state(series, state_map=None)`
Standardize US state names to abbreviations.

```python
states = pd.Series(['California', 'TX', 'new york'])
cleaned = cleanroom.clean_state(states)
# Result: ['CA', 'TX', 'NY']
```

#### `clean_country(series, country_map=None)`
Standardize country names to ISO codes.

```python
countries = pd.Series(['United States', 'USA', 'United Kingdom'])
cleaned = cleanroom.clean_country(countries)
# Result: ['US', 'US', 'GB']
```

### DataFrame Operations

#### `auto_clean(df)`
Automatically clean common columns with flexible name matching.

Recognizes these column patterns:
- **Email**: `email`, `e-mail`, `mail`, `email_address`, `e_mail`
- **Names**: `first_name`, `First Name`, `fname`, `f_name`, `given_name`
- **Phone**: `phone`, `telephone`, `pnumber`, `phone_number`, `mobile`
- **Address**: `zip`, `zip_code`, `postal_code`, `state`, `country`

```python
# Works with any column naming convention
df_messy = pd.DataFrame({
    'First Name': ['john', 'JANE'],
    'family name': ['smith', 'DOE'],  
    'E-Mail Address': ['JOHN@EXAMPLE.COM', 'jane@test.org'],
    'telephone': ['(555) 123-4567', '555.987.6543']
})

cleaned = cleanroom.auto_clean(df_messy)
```

#### `apply_schema(df, schema)`
Apply custom cleaning rules with a flexible schema.

```python
schema = {
    'clean_email': {
        'func': cleanroom.clean_email,
        'source': ['email', 'email_address', 'e_mail']  # Try multiple columns
    },
    'full_name': {
        'func': cleanroom.clean_name,
        'source': ['first_name', 'last_name'],  # Combine columns
        'kwargs': {'case': 'title'}
    }
}

cleaned_df = cleanroom.apply_schema(df, schema)
```

## 🌍 Flexible Column Matching

Cleanroom automatically handles various column naming conventions:

| Data Type | Recognized Patterns |
|-----------|-------------------|
| **First Name** | `first_name`, `First Name`, `fname`, `f_name`, `f name`, `firstname`, `given_name` |
| **Last Name** | `last_name`, `Last Name`, `lname`, `surname`, `family_name`, `lastname` |
| **Email** | `email`, `e-mail`, `mail`, `email_address`, `e_mail` |
| **Phone** | `phone`, `telephone`, `pnumber`, `phone_number`, `mobile`, `cell` |
| **ZIP Code** | `zip`, `zip_code`, `zipcode`, `postal_code`, `postcode` |
| **State** | `state`, `st`, `province`, `region` |
| **Country** | `country`, `nation`, `nationality` |

## 🏗️ Design Philosophy

- **Simple**: Small set of pure functions you can compose
- **Extensible**: Pass custom alias maps and cleaning rules
- **Flexible I/O**: Works on `pd.Series`, DataFrame columns, or entire DataFrames
- **Non-destructive**: Always returns new objects, never modifies input data
- **Pandas-native**: Leverages pandas' powerful string operations

## 🧪 Examples

### Real-world messy data
```python
import pandas as pd
import cleanroom

# Typical messy customer data
customers = pd.DataFrame({
    'f name': ['  alice  ', 'BOB', 'Charlie Brown'],
    'surname': ['SMITH', 'jones', 'o\'connor'],
    'e-mail': ['ALICE@GMAIL.COM', 'bob@YAHOO.com', '  charlie@test.org  '],
    'pnumber': ['555-1234', '(800) 555-0199', '+1.212.555.9876'],
    'zip code': ['12345-6789', 'ABC 90210', '10001'],
    'st': ['California', 'TX', 'new york'],
    'nation': ['USA', 'United States', 'US']
})

# Clean everything with one function call
clean_customers = cleanroom.auto_clean(customers)
```

### Custom cleaning pipeline
```python
# Build your own cleaning pipeline
def clean_customer_data(df):
    result = df.copy()
    
    # Clean emails
    if 'email' in result.columns:
        result['email'] = cleanroom.clean_email(result['email'])
    
    # Standardize names with custom aliases
    name_aliases = {'bobby': 'Robert', 'mike': 'Michael'}
    if 'first_name' in result.columns:
        result['first_name'] = cleanroom.clean_name(
            result['first_name'], 
            alias_map=name_aliases
        )
    
    return result
```

## 📋 Requirements

- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.21.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Documentation**: [GitHub README](https://github.com/yourusername/cleanroom#readme)
- **Issues**: [GitHub Issues](https://github.com/yourusername/cleanroom/issues)
- **Source Code**: [GitHub Repository](https://github.com/yourusername/cleanroom)
