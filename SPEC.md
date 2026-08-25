# Weather2Go: Route Radar MVP Specification

## Purpose

Weather2Go: Route Radar is a Michigan-focused data science application that estimates **weather-related driving risk** for a planned trip.

The project is a clean rebuild of earlier Weather2Go versions. It retains the existing data strategy while improving the reproducibility of the data pipeline, expanding model experimentation, and integrating the trained model into a Streamlit route-planning application.

## MVP User Workflow

A user:

1. Enters a Michigan start city and destination city.
2. Selects a departure date and time.
3. Views a single route between the two locations.
4. Sees weather details for the start location at departure time.
5. Sees weather details for the destination at estimated arrival time.
6. Receives one overall trip risk:
   * Low
   * Moderate Risk
   * High Risk
   * Severe Risk
7. Receives safety guidance appropriate to the predicted risk level.

Both locations must be in Michigan.

## Risk Definition

The model estimates **weather-related driving risk**. It does not predict whether a crash will occur.

The model produces separate risk scores for the start and destination weather conditions.

Each score is converted to a risk level using these thresholds:

* **Low:** 0% to <20%
* **Moderate Risk:** 20% to <40%
* **High Risk:** 40% to <60%
* **Severe Risk:** 60% to 100%

The displayed overall trip risk is the worse of the two risk levels:

`Low < Moderate Risk < High Risk < Severe Risk`

Only the overall trip risk is displayed to the user.

## Data

The MVP uses the same data strategy as previous Weather2Go versions:

* US Accidents data for accident-associated weather conditions
* Open-Meteo historical weather data for normal/non-accident Michigan conditions

Existing source files may be reused where appropriate, while other source data may be downloaded again.

Data is organized into:

* raw data
* processed data

## ETL

Production ETL must be reproducible using Python scripts rather than notebooks.

The pipeline must transform source data into model-ready processed data without manual editing.

Notebooks may be used for:

* exploratory data analysis
* model experimentation
* investigation and visualization

The production ETL and final model-training workflow must also exist outside notebooks.

### Data Validation

The ETL must perform lightweight validation appropriate to the modeling pipeline, including:

* required columns exist
* required datasets are not empty
* required modeling fields do not contain unexpected missing values
* important numeric values and data types are valid
* duplicate records are checked
* expected target values are valid
* processed output has the expected structure

Invalid data should fail clearly rather than silently continuing through the pipeline.

## Modeling

The MVP converts model output probabilities into four risk levels:

* Low
* Moderate Risk
* High Risk
* Severe Risk

Risk levels are derived from model output probabilities using the thresholds defined in the Risk Definition section.

Model development must include:

* Logistic Regression as a baseline
* comparison of appropriate classification models
* stratified random train/test splitting
* a held-out test set used only for final evaluation
* fixed random seeds where applicable

The primary evaluation priority is **recall for Severe Risk conditions**, since failing to identify highest-risk weather is considered more important than maximizing overall accuracy.

Additional evaluation metrics may be used to understand overall model behavior.

Class balance will be adjusted using a hybrid under-sampling and over-sampling strategy, targeting approximately a 4:1 ratio of non-accident to accident observations in the training data.

The deployed model outputs only the final risk label, not prediction probabilities.

## Model Features

Prediction features must be available from the live weather data used by the application.

Weather information includes:

* weather condition/category
* temperature
* humidity
* precipitation
* wind speed

Time-related features may also be included when supported by the training and inference workflow.

The training and application feature definitions must remain consistent.

## Weather

Open-Meteo is used for weather data.

The user provides a departure date and time.

The application retrieves:

* start-location weather for departure time
* destination weather for estimated arrival time

If required weather data cannot be retrieved for either location, the application must not calculate an overall trip risk.

## Locations and Routing

Both start and destination must resolve to Michigan cities.

Locations outside Michigan must be rejected with a clear user-facing message.

The MVP displays one route containing:

* route line
* start marker
* destination marker

Only one route is required.

The specific mapping, geocoding, and routing provider is not prescribed. Free and practical services are preferred.

Weather-related risk is evaluated only at the start and destination, not along the route.

## Streamlit Application

The MVP is a single-page Streamlit application.

The main page includes:

* start and destination inputs
* departure date and time
* prominently displayed overall trip risk
* route map
* start weather details
* destination weather details
* risk-appropriate safety guidance

The sidebar contains explanatory information about the model and what the prediction represents.

Application state should preserve completed trip results during normal Streamlit reruns.

No visualization other than the route map is required.

## Deployment

The MVP must be deployable using Streamlit Community Cloud.

The repository must contain the trained model artifact and other files required for the deployed application to run without retraining the model.

## Reproducibility

A developer should be able to reproduce the project workflow:

**source data → ETL → processed data → model training → saved model → Streamlit application**

The project should not depend on manual notebook steps for production data preparation or model training.

## Testing

Testing should remain minimal and focused on high-value application behavior.

At minimum, tests should cover:

* Michigan location validation
* external API response/error handling

Additional tests may be added when they protect important project logic.

## MVP Scope

The MVP is intentionally limited to:

* Michigan trips
* one start location
* one destination
* one route
* start and destination weather
* one overall Low / Moderate Risk / High Risk / Severe Risk weather-related driving-risk classification
* basic safety guidance
* Streamlit deployment

Features outside this workflow are not part of the MVP unless this specification is explicitly updated.