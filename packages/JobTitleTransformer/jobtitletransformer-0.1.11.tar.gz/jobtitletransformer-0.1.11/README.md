# JobTitleTransformer

This is a library to transform / enrich job title values coming from various sources (databases, csv's....). It performs data transformation in multiple steps using a modular approach.

This Package is dedicated to Health Care Sector and not suitable for other sectors and their Job Title values.

# IMPORTANT MESSAGE:

This library mainly focus on transforming / enriching job title values to a standard format. For successful Integration of this library you will need to have a column 'job_title' in your dataset or any other similar column. Very Important is you will need to RENAME 'job_title' as 'speciality' before execution and you will need to copy your original dataframe to a NEW DATAFRAME 'df'

## Installation

Install with `pip`:

```bash
pip install JobTitleTransformer

