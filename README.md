# LEED Checklist & Score Estimator (Streamlit)

A simple Streamlit app to help plan a LEED project, track prerequisite-style checklist items, estimate points by category, and view an expected certification level.

## Files
- `app.py` — main Streamlit application
- `requirements.txt` — Python dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a new GitHub repository.
2. Upload these files to the repository.
3. Go to Streamlit Community Cloud.
4. Click **New app**.
5. Select your GitHub repo.
6. Set the main file path to `app.py`.
7. Deploy.

## Suggested GitHub repository structure
```text
your-repo/
├── app.py
├── requirements.txt
└── README.md
```

## Notes
This is a planning and estimation app, not an official LEED certification calculator. For actual certification, align the scoring logic with the exact LEED version and rating system you want to pursue.
