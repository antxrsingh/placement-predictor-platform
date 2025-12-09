## Placement Predictor Platform

An end-to-end web application that helps B.Tech students estimate their placement chances and expected salary range based on their academic profile, work experience, projects and skills.

## Tech Stack

- Frontend: React, Fetch API
- Backend: Flask, Flask-CORS, gunicorn
- ML: scikit-learn (Logistic Regression), pandas, numpy
- Hosting: Render (backend), Vercel (frontend)
- Dataset: Kaggle 

## Features

- Predicts placement probability using a trained logistic regression model.
- Estimates a realistic salary range (LPA + INR) based on profile strength and market trends.
- Hybrid ML + rule-based adjustment to account for projects, internships, hackathons, CP level and skills.
- Provides personalized suggestions (regarding DSA, internships, projects, hackathons, clubs) to improve chances.
- Fully deployed and accessible via browser.

## Live Demo

- Frontend: [https://your-vercel-url.vercel.app](https://placement-predictor-platform.vercel.app/)
- Backend API: [https://your-render-url.onrender.com](https://placement-predictor-platform.onrender.com/)
