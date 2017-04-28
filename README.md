# models
Repo for code and results of models and exploratory data analysis.

## DataKind + Kiva

For a thorough introduction to the work Kiva does, check out [the detailed welcome doc](https://docs.google.com/document/d/10rCACYpqx_LTh_1RaEd2jGNX2XXOfBU8xOqvI8TVGLQ/edit) Jonathan Joa, the Data Ambassador for this project, put together.

## Project Goals

Kiva has three main aims for this project:

1. I want to use loan, lender and borrower data to explore what types of loans and borrowers are prone to partial loan repayments so that kiva can work with borrowers and lenders to restructure repayments when necessary that maximally suit the borrower (their business is successful and repays loan) and lender (they continue to re-lend) so that that microfinance grows and succeeds with new borrowers getting access to finance and grows the lender base by improving repayment rates.
2. I want to use loan, lender and borrower data to predict which loans are at risk of low repayment rates so that kiva can improve their loan risk algorithm which assesses loan risk for prospective lenders so that that microfinance grows and sustains with more accurate and symmetric information.
3. I want to use loan and borrower data to explore the words, phrases and characteristics most associated with successful borrower profiles/loans  so that kiva and its small business partners can coach new borrowers to create the most effective loan profile for getting fully funded so that that microfinance grows, sustains and maximizes borrowers’ access to finance.

## Code in this Repo
- prob1_loan_repayments

 - Python code (and requirements.txt file) that will take the two DataKind CSVs (repayments_expected.csv and repayments_collected.csv) and combine them into a single file that can be used for modeling
 - Running `python repayment_normalizer.py` will produce the combined dataset as long as the filepaths in repayment_normalizer.py point to the correct files
 - This code can be reused on any set of data in the following format to recreate the combined dataset (in case you'd like to re-fit the model, tinker, test some assumptions or improve the mode in the future)
 - more information on repayments_collected & repayments_expected can be found in the Data Sources section of this README, as can an example of the final combined dataset

## Data Sources

Available via Google Drive.  For access, please open an issue in this repo requesting access and a Data Ambassador will follow up with a link.
