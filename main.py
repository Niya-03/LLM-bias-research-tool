import src.dataset_manager as dm
import src.experimentor as experiment_runner
import src.visualisator as visualisator
import src.results_manager as results_manager
from datetime import datetime
from config import BASE_DATASET_PATH, SUPPORTED_MODELS, RESULTS_DIR, DIAGRAMS_DIR


categories = dm.load_categories_list(BASE_DATASET_PATH)

print("Available categories:")

for idx, cat in enumerate(categories):
    print("%i. %s" % (idx + 1, cat))


category = input("\nEnter category\n")

while category not in categories:
    print("\nEnter valid category!\n")
    category = input("Enter category\n")

data = dm.load_category("data/datasets/base_dataset.csv", category)

print("\nAvailable models:")
for idx, model in enumerate(SUPPORTED_MODELS):
    print("%i. %s" % (idx + 1, model))

model = input("\nEnter model\n")

while model not in SUPPORTED_MODELS:
    print("\nEnter valid model!")
    category = input("Enter model\n")

# model = input("stop here")

results = experiment_runner.run_experiment(data, model)

results_manager.save_results(results, category, model)


visualisator.plot_results(
    "%s/%s_%s_results_%s.json"
    % (RESULTS_DIR, category, model, str(datetime.today().strftime("%Y-%m-%d"))),
    "%s/%s_%s_results_%s.png"
    % (DIAGRAMS_DIR, category, model, str(datetime.today().strftime("%Y-%m-%d"))),
)
