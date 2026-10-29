*
PyMart wants a production-ready command-line back-office toolkit to support its daily operations. Build a Python application that imports product, customer, and order data from text-based files, validates and cleans that data, processes orders, and produces dated operational reports on demand and on schedule.

Business context

PyMart is a mid-sized retailer with multiple categories of products.

Store staff export daily data extracts from an existing POS system. These exports are not always clean: missing fields, wrong separators, inconsistent casing, and occasional invalid numbers/dates.

Managers need repeatable reports (daily and monthly) that can be archived and re-produced later.

Functional requirements

Command-line interface

Provide a CLI entry point (e.g., running a module with -m or running a script) that supports at minimum:

Importing data files into an internal representation.

Creating and listing orders.

Generating reports.

Printing clear error messages without crashing.

Data importing + string/list processing

Input files are plain text (CSV-like), with at least one file for each entity type: products, customers, orders (or order lines).

Implement robust cleaning/validation using string and list techniques (e.g., split, strip, join, replace, case normalization, filtering, mapping).

Handle common issues: extra whitespace, empty lines, missing columns, invalid numeric values, negative quantities, malformed identifiers.

Exception handling (including custom exceptions)

Use try/except/else/finally appropriately for file I/O and parsing.

Define and raise at least two custom exception classes (e.g., DataValidationError, RecordFormatError, UnknownProductError, DuplicateIdError).

Errors must be actionable (include file/line context when possible).

OOP design (classes, inheritance, polymorphism)

Model the domain with classes (minimum: Product, Customer, Order, and at least one additional class of your choice).

Use inheritance for at least one hierarchy (example: Product -> PerishableProduct / DigitalProduct, or Customer -> IndividualCustomer / BusinessCustomer).

Demonstrate polymorphism by having derived classes override at least one method used by the rest of the program (e.g., pricing, tax/discount computation, serialization/output formatting).

Custom modules/packages

Organize the solution as an installable or runnable package (multiple modules) rather than a single script.

Include a clear package structure separating concerns (e.g., models, io/parsers, services, cli, reports, utils, exceptions).

Imports must be clean and consistent across the package.

Generators + file-system operations

Use at least one generator to stream large inputs or report rows (e.g., yield parsed records line-by-line, yield computed report lines, yield orders matching criteria).

Implement file-system operations to:

Create an output directory structure for reports (if missing).

Write reports to files (and not only to stdout).

Archive reports by date (e.g., per day and/or per month).

datetime/time/calendar usage

Reports must include timestamps and/or reporting periods.

Use datetime/time/calendar to support at least two of the following:

Generate a daily report filename with the current date.

Generate a monthly summary for the current month (e.g., using calendar month boundaries).

Validate/parse dates in input data.

Schedule-like behavior (e.g., create reports for a date provided as an argument; or produce “next report date” logic).

Outputs (minimum)

At least two report types written to disk (examples: daily sales summary, stock level report, top-selling products, customers with highest spend, failed records report).

Reports must be reproducible: the same inputs should produce consistent outputs.

Example commands (use these exact forms if you choose to provide them in your project)

python -m pymart.cli --help
python -m pymart.cli import --products data/products.txt --customers data/customers.txt --orders data/orders.txt
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
Deliverables

Source code

A Python package containing your full implementation.

Clear module/package structure.

Dependency declaration

If you use any third-party packages, include a requirements.txt.

If you use only the standard library, requirements.txt is optional.

Evidence of a working solution (choose one)

A step-by-step procedure document with screenshots showing:

How to run the CLI.

A successful import.

At least two generated report files.

Examples of handled validation errors.

OR

A short live or recorded demonstration presenting:

Project structure.

A run of the CLI that imports data.

Generation of at least two reports.

An example of graceful error handling.

Grading rubric (100%)

Functionality and completeness (35%)

CLI works end-to-end; import, processing, and report generation meet requirements.

Reports are correct, consistent, and written to disk.

Code quality and maintainability (20%)

PEP 8 readability, naming, modularity, separation of concerns, sensible packaging.

OOP design (20%)

Clear domain modeling, correct use of inheritance, meaningful polymorphism, encapsulation.

Error handling and robustness (10%)

Custom exceptions, informative messages, resilience to bad input, no unhandled crashes.

Standard library usage (10%)

Appropriate use of os/path/file handling and datetime/time/calendar features.

Documentation / demo clarity (5%)

Clear run instructions and evidence of working output.

Submission checklist

Project runs on a clean environment with the declared dependencies.

Package imports work (no relative-import confusion at runtime).

Reports directory is created automatically when missing.

At least one generator is present and used in program flow.

At least two custom exception classes are defined and raised.

At least two report files are generated and saved with date-based naming.

Deliverable evidence included (procedure+screenshots OR demo recording).

requirements.txt included if any third-party package is used.

