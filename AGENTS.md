# Goal
Build a personalized beauty decision assistant web app.

# Product Vision
The system helps users make better beauty product decisions by:
- understanding their skin type and preferences
- analyzing real user reviews
- filtering out promotional or suspicious content
- ranking products based on trustworthy evidence

# Core Features (MVP)
- user questionnaire (skin type, concerns, budget, preferences)
- review data ingestion (dataset or user-provided text)
- ad / suspicious review filtering
- product ranking (top 3 recommendations)
- explanation for each recommendation (evidence-based)

# Key Principles
- recommendations must be personalized
- recommendations must be explainable
- only use trustworthy data (after filtering)
- avoid overengineering; prioritize a working MVP
- system should feel like a real product, not a demo

# Rules
- do not scrape websites that do not explicitly allow it
- prefer open datasets, licensed data, or user-provided content
- keep the system modular (separate ingestion, filtering, ranking)
- every recommendation must include reasoning
- include simple tests for ranking and ad filtering
- ensure the app can be deployed

# Engineering Guidelines
- start with a minimal working version
- build in small steps (one module at a time)
- test each module before moving on
- avoid unnecessary complexity or premature optimization