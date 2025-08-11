# SNOWPLOW_PROJECT

This project automates the DBT folder structure along with the creation of `dbt-profile.yml` based on the provided JSON in the input folder `AUTO-DBT-PROFILE\data\input`.  
The expectation was to add variables in the profile based on the Snowplow Unified package. However, I noticed that some variables provided in the JSON are not mapped with the configuration in [Snowplow Unified dbt configuration](https://docs.snowplow.io/docs/modeling-your-data/modeling-your-data-with-dbt/dbt-configuration/unified/).

The methodology used is to provide an option to create a mapping file `AUTO-DBT-PROFILE\data\mappings\mapping.yml` which maps variables in the input JSON to the template given in `AUTO-DBT-PROFILE\template\dbt-profile-template.txt`.

Currently, mapping handles the given JSON example. If additional variables are present in the input, please update the mapping.

The final DBT structure will be present in the **path:-SNOWPLOW_PROJECT\AUTO-DBT-PROFILE\data\final_output**

The main driving file uses the custom utils at `AUTO-DBT-PROFILE\utils\mapper.py` to traverse the mapping and create the final output in `AUTO-DBT-PROFILE\data\output`.  
The main script is `AUTO-DBT-PROFILE\solution.py`.

---

## Running the Script

Running the Python script is straightforward since it has no database connections and only minimal non-standard dependencies. I also tested it locally using Docker, but given the lightweight dependencies, using Docker can be skipped for this project.

### Prerequisites
- Python 3
- pip

### Steps

1. Clone the project  
   `https://github.com/inchu24/SNOWPLOW_PROJECT.git`

2. Navigate to the folder  
   `cd AUTO-DBT-PROFILE`

3. Install dependencies  
   `pip install -r requirements.txt`

4. Run the script  
   `python solution.py`

5. Sample input JSON files are provided in `AUTO-DBT-PROFILE\data\input` with each provided JSON separated. Outputs are in `AUTO-DBT-PROFILE\data\output`.

6. Sample logs are available in the `AUTO-DBT-PROFILE\log` folder. Check logs for any issues.

7. Testing & Code Quality
Unit tests are included and can be run using pytest.
 `pytest`.

9. Linter `flake8` is used to enforce PEP-8 Python coding standards.

10. A simple CI/CD workflow is included (`.github\workflows\ci.yml`) to run tests and lint checks before merging to the `main` branch.




