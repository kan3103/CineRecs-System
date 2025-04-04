# Contributing to Movie Recommendation System

Thank you for your interest in contributing to our Movie Recommendation System! This document provides guidelines on how to contribute effectively.

## Table of Contents
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [AI Algorithm](#ai-algorithm)
  - [Database and Data Warehouse](#database-and-data-warehouse)
- [Pull Request Process](#pull-request-process)
- [Git Workflow](#git-workflow)

## Getting Started
1. Fork the repository and clone it to your local machine.
2. Create a new branch for your feature/fix.
3. Follow the contribution guidelines outlined below for each part of the system.
4. Ensure that each scope (Backend, Frontend, AI Algorithm, Database) has a properly configured `.gitignore` file to prevent unnecessary files (e.g., `.txt`, `.log`, `node_modules`, `__pycache__`) from being pushed to the repository.


## Project Structure
```
/movie-recommendation-system
│── backend/           # FastAPI-based backend
│── frontend/          # ReactJS-based frontend
│── ai/      # AI model and recommendation logic
│── database/          # Database and Data Warehouse management
```

## How to Contribute

### Backend
- The backend is built using **FastAPI**.
- Follow RESTful API principles.
- Ensure the `.gitignore` file excludes unnecessary files like `__pycache__`, `.env`, and logs.


### Frontend
- The frontend is built using **ReactJS**.
- Follow modular component structure.
- Use Tailwind CSS for styling.
- The `.gitignore` file should exclude `node_modules/`, `.env`, and build artifacts.


### AI Algorithm
- The recommendation system leverages **KNN** and **collaborative filtering**.
- Implement models using **TensorFlow/PyTorch and Scikit-learn**.
- The `.gitignore` file should exclude large datasets, model weights, and temporary training logs.


### Database and Data Warehouse
- Use **PostgreSQL** for the primary database.
- Optimize database queries for performance.
- The `.gitignore` file should exclude database dumps, temporary data, and sensitive configurations.


## Pull Request Process
1. Ensure your code passes all tests.
2. Open a PR with a clear description of changes.
3. Request a review from maintainers.
4. Address feedback and make necessary changes.
5. Once approved, the leader of the respective part (Backend, Frontend, AI Algorithm, or Database) will verify and merge the PR!

## Git Workflow

### Create a new branch
```bash
git checkout -b <scope/branch-name>
```
Example:
```bash
git checkout -b frontend/add-login
```

### Check available branches
```bash
git branch
```
To check all branches, including remote:
```bash
git branch -a
```

### Switch to another branch
```bash
git switch <branch-name>
```

### Add and commit changes
```bash
git add .
git commit -m "Short description of changes"
```
Example:
```bash
git commit -m "Add user authentication"
```

### Push branch to GitHub
```bash
git push origin <scope/branch-name>
```
Example:
```bash
git push origin frontend/add-login
```

### Create a Pull Request to main
1. Push your branch to GitHub:
   ```bash
   git push origin <branch-name>
   ```
2. Open a pull request (PR) on GitHub, targeting the `main` branch.
3. Request a review from the leader of the respective part (Backend, Frontend, AI Algorithm, or Database).
4. Address any feedback and make necessary changes.
5. Once approved, the leader will merge the PR into `main`.

Thank you for contributing! 🚀