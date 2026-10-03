# Kaggle Titanic - Original Dataset

An end-to-end machine learning pipeline to predict passenger survival on the Titanic.

##  Workflow

1. **Data Cleaning**: Handled missing values (Age, Fare, Embarked) and encoded categorical features (Sex).
2. **Feature Engineering**: 
   - Extracted titles (Mr, Mrs, Miss, etc.) from the `Name` column using regex.
   - Created a `Family_size` feature based on `SibSp` and `Parch`.
3. **Model Comparison**: Evaluated Logistic Regression vs. Random Forest.
4. **Hyperparameter Tuning**: Used GridSearchCV to find the best parameters for the Random Forest (e.g., `max_depth=6`).
5. **Ensemble Learning**: Built a soft VotingClassifier combining Logistic Regression and the tuned Random Forest.

##  Results
- **Local 5-Fold Cross-Validation Accuracy**: 0.8384
- **Kaggle Leaderboard Score**: 0.79425

##  File Descriptions
- `Advanced Titanic problem...ipynb`: Complete code for data processing and model training.
- `submission_voting_tuned.csv`: Final submission file for the Kaggle competition.
